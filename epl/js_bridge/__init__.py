"""
EPL JavaScript/TypeScript Bridge

Manages a persistent Node.js subprocess for JS/TS interop with EPL.
Communication is via newline-delimited JSON over stdin/stdout.
"""

import atexit
import json
import os
import shutil
import subprocess
import sys
import threading


# Path to the Node.js worker script bundled with EPL
_WORKER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_worker.js')

# Timeout for individual IPC calls (seconds)
_DEFAULT_TIMEOUT = 30

# NPM packages that are safe to auto-install
_JS_SAFE_AUTO_INSTALL = frozenset({
    # HTTP
    'axios', 'node-fetch', 'got', 'undici', 'superagent',
    # Utilities
    'lodash', 'ramda', 'date-fns', 'moment', 'dayjs', 'uuid',
    'nanoid', 'ms', 'dotenv', 'debug',
    # Data / Parsing
    'csv-parser', 'xlsx', 'papaparse', 'cheerio', 'xml2js',
    'yaml', 'toml', 'marked', 'showdown',
    # AI / ML
    'openai', '@google/generative-ai', 'langchain',
    # Database
    'better-sqlite3', 'pg', 'mysql2', 'mongoose', 'redis',
    'knex', 'sequelize', 'prisma',
    # CLI
    'chalk', 'ora', 'inquirer', 'commander', 'yargs', 'prompts',
    # File / OS
    'fs-extra', 'glob', 'globby', 'chokidar', 'rimraf', 'mkdirp',
    'archiver', 'adm-zip', 'sharp',
    # Crypto / Auth
    'bcrypt', 'jsonwebtoken', 'crypto-js', 'jose', 'passport',
    # Testing
    'jest', 'mocha', 'chai', 'vitest', 'sinon',
    # Validation
    'zod', 'joi', 'yup', 'ajv', 'validator',
    # Templating
    'ejs', 'handlebars', 'pug', 'nunjucks',
    # Networking
    'ws', 'socket.io', 'socket.io-client',
})


def _find_node():
    """Find the Node.js executable, or return None."""
    node = shutil.which('node')
    if node:
        return node
    # Try common install locations on Windows
    for candidate in [
        r'C:\Program Files\nodejs\node.exe',
        r'C:\Program Files (x86)\nodejs\node.exe',
        os.path.expanduser('~\\AppData\\Roaming\\nvm\\current\\node.exe'),
    ]:
        if os.path.isfile(candidate):
            return candidate
    return None


class NodeBridgeError(Exception):
    """Raised when the Node.js bridge encounters an error."""
    pass


class NodeBridge:
    """
    Manages a persistent Node.js subprocess for JS/TS interop.

    Usage:
        bridge = NodeBridge.get_instance()
        handle = bridge.require("lodash")
        result = bridge.call(handle, "sortBy", [[3, 1, 2]])
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        """Get or create the singleton bridge instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        """Shut down and reset the singleton (for testing)."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.shutdown()
                cls._instance = None

    def __init__(self):
        self._process = None
        self._next_id = 1
        self._id_lock = threading.Lock()
        self._started = False
        self._read_lock = threading.Lock()
        self._timeout = _DEFAULT_TIMEOUT

    def _ensure_started(self):
        """Lazily start the Node.js subprocess on first use."""
        if self._started and self._process and self._process.poll() is None:
            return

        node_exe = _find_node()
        if not node_exe:
            raise NodeBridgeError(
                'Node.js is not installed or not found in PATH. '
                'The JavaScript bridge requires Node.js 18+. '
                'Install it from: https://nodejs.org/'
            )

        try:
            self._process = subprocess.Popen(
                [node_exe, _WORKER_SCRIPT],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                text=True,
                bufsize=1,  # line-buffered
            )
        except OSError as e:
            raise NodeBridgeError(f'Failed to start Node.js bridge: {e}')

        # Wait for the "ready" signal
        try:
            ready_line = self._process.stdout.readline()
            if not ready_line:
                stderr = self._process.stderr.read()
                raise NodeBridgeError(
                    f'Node.js bridge failed to start. stderr: {stderr.strip()}'
                )
            ready = json.loads(ready_line)
            if not ready.get('ready'):
                raise NodeBridgeError(
                    f'Node.js bridge sent unexpected init: {ready_line.strip()}'
                )
        except json.JSONDecodeError:
            raise NodeBridgeError(
                f'Node.js bridge sent invalid JSON on startup: {ready_line.strip()}'
            )

        self._started = True
        atexit.register(self.shutdown)

    def _next_request_id(self):
        with self._id_lock:
            rid = self._next_id
            self._next_id += 1
            return rid

    def _send(self, command: dict):
        """Send a JSON command to the Node worker."""
        self._ensure_started()
        line = json.dumps(command) + '\n'
        try:
            self._process.stdin.write(line)
            self._process.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            raise NodeBridgeError(f'JS bridge pipe broken: {e}')

    def _recv(self, request_id: int) -> dict:
        """Read a JSON response from the Node worker."""
        with self._read_lock:
            try:
                line = self._process.stdout.readline()
                if not line:
                    stderr_out = ''
                    if self._process.stderr:
                        stderr_out = self._process.stderr.read()
                    raise NodeBridgeError(
                        f'JS bridge process terminated unexpectedly. '
                        f'stderr: {stderr_out.strip()}'
                    )
                return json.loads(line)
            except json.JSONDecodeError:
                raise NodeBridgeError(f'JS bridge returned invalid JSON: {line.strip()}')

    def _request(self, command: dict) -> dict:
        """Send a command and wait for its response."""
        rid = self._next_request_id()
        command['id'] = rid
        self._send(command)
        response = self._recv(rid)
        if not response.get('ok'):
            error_msg = response.get('error', 'Unknown JS bridge error')
            raise NodeBridgeError(error_msg)
        return response

    # ─── Public API ──────────────────────────────────────

    def require(self, module_name: str) -> str:
        """Load a JS/TS module and return its handle ID."""
        self._ensure_started()
        try:
            response = self._request({'cmd': 'require', 'module': module_name})
            return response['handle']
        except NodeBridgeError as e:
            error_msg = str(e)
            if 'Cannot find module' in error_msg or 'MODULE_NOT_FOUND' in error_msg:
                # Try auto-install
                pkg_name = module_name.split('/')[0]
                if pkg_name.startswith('@') and '/' in module_name:
                    # Scoped package: @scope/name
                    parts = module_name.split('/')
                    pkg_name = '/'.join(parts[:2])

                if pkg_name.lower() in _JS_SAFE_AUTO_INSTALL:
                    self._auto_install(pkg_name)
                    # Retry require after install
                    response = self._request({'cmd': 'require', 'module': module_name})
                    return response['handle']
                else:
                    raise NodeBridgeError(
                        f'JavaScript module "{module_name}" is not installed. '
                        f'Run "npm install {pkg_name}" in your project directory, '
                        f'or add it to the allowlist.'
                    )
            raise

    def call(self, handle: str, method: str = None, args: list = None) -> 'Any':
        """Call a function/method on a handle. Returns deserialized result."""
        cmd = {'cmd': 'call', 'handle': handle}
        if method:
            cmd['method'] = method
        cmd['args'] = [self._serialize_arg(a) for a in (args or [])]
        response = self._request(cmd)
        return self._deserialize_result(response.get('result'))

    def get_prop(self, handle: str, prop: str) -> 'Any':
        """Get a property from a JS object handle."""
        response = self._request({'cmd': 'get', 'handle': handle, 'prop': prop})
        return self._deserialize_result(response.get('result'))

    def set_prop(self, handle: str, prop: str, value) -> None:
        """Set a property on a JS object handle."""
        self._request({
            'cmd': 'set', 'handle': handle,
            'prop': prop, 'value': self._serialize_arg(value),
        })

    def release(self, handle: str) -> None:
        """Release a handle, freeing it from the worker's memory."""
        try:
            self._request({'cmd': 'delete', 'handle': handle})
        except NodeBridgeError:
            pass  # Ignore errors on cleanup

    def shutdown(self):
        """Shut down the Node.js worker process."""
        if self._process and self._process.poll() is None:
            try:
                self._send({'id': self._next_request_id(), 'cmd': 'shutdown'})
                self._process.wait(timeout=5)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
        self._started = False
        self._process = None

    # ─── Serialization Helpers ───────────────────────────

    def _serialize_arg(self, value):
        """Serialize an EPL value for transport to the JS worker."""
        if value is None:
            return {'type': 'null', 'value': None}
        if isinstance(value, bool):
            return {'type': 'boolean', 'value': value}
        if isinstance(value, int):
            return {'type': 'number', 'value': value}
        if isinstance(value, float):
            return {'type': 'number', 'value': value}
        if isinstance(value, str):
            return {'type': 'string', 'value': value}
        if isinstance(value, list):
            return {'type': 'array', 'value': [self._serialize_arg(v) for v in value]}
        if isinstance(value, dict):
            return {'type': 'object', 'value': {
                k: self._serialize_arg(v) for k, v in value.items()
            }}
        # JSModule handle — pass the handle reference
        if hasattr(value, 'handle'):
            return {'type': 'handle', 'handle': value.handle}
        # Fallback: convert to string
        return {'type': 'string', 'value': str(value)}

    def _deserialize_result(self, result):
        """Deserialize a JS worker result back into EPL values."""
        if result is None:
            return None
        rtype = result.get('type', 'null')
        if rtype == 'null':
            return None
        if rtype in ('boolean', 'number', 'string'):
            return result['value']
        if rtype == 'array':
            return [self._deserialize_result(item) for item in result.get('value', [])]
        if rtype == 'object':
            return {
                k: self._deserialize_result(v)
                for k, v in result.get('value', {}).items()
            }
        if rtype == 'handle':
            # Return a JSModuleHandle so the interpreter can wrap it
            return JSModuleHandle(
                bridge=self,
                handle=result['handle'],
                type_name=result.get('typeName', 'Object'),
            )
        return result.get('value')

    # ─── NPM Auto-Install ────────────────────────────────

    def _auto_install(self, package_name: str):
        """Auto-install an allowlisted npm package."""
        npm = shutil.which('npm')
        if not npm:
            raise NodeBridgeError(
                f'Cannot auto-install "{package_name}": npm not found in PATH.'
            )
        print(f'[EPL] JavaScript package "{package_name}" not found. Auto-installing...')
        try:
            subprocess.check_call(
                [npm, 'install', package_name, '--save'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.getcwd(),
            )
            print(f'[EPL] Successfully installed "{package_name}".')
        except subprocess.CalledProcessError:
            raise NodeBridgeError(
                f'Failed to auto-install "{package_name}". '
                f'Run "npm install {package_name}" manually.'
            )


class JSModuleHandle:
    """
    A lightweight reference to a JS object living in the Node worker.
    Used internally by the bridge to pass handle references back to the interpreter.
    """
    def __init__(self, bridge: NodeBridge, handle: str, type_name: str = 'Object'):
        self.bridge = bridge
        self.handle = handle
        self.type_name = type_name

    def __repr__(self):
        return f'<js handle {self.handle} ({self.type_name})>'
