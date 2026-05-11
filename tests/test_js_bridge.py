"""
Tests for the EPL JavaScript/TypeScript Bridge

Covers:
  - Parser: Use javascript/typescript syntax
  - AST: UseJSStatement node
  - Bridge: NodeBridge (mocked and integration)
  - Interpreter: JSModule dispatch
  - JS Transpiler: UseJSStatement emission
  - Error Explainer: JS bridge patterns
"""

import unittest
import sys
import os
import json
import shutil

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from epl.tokens import TokenType
from epl.lexer import Lexer
from epl.parser import Parser
from epl import ast_nodes as ast


# ═══════════════════════════════════════════════════════════
# Phase 1: Parser Tests
# ═══════════════════════════════════════════════════════════

class TestJSBridgeParser(unittest.TestCase):
    """Test that the parser correctly handles Use javascript/typescript syntax."""

    def _parse(self, code):
        tokens = Lexer(code).tokenize()
        return Parser(tokens).parse()

    def test_use_javascript_basic(self):
        """Use javascript "lodash" → UseJSStatement with auto-alias."""
        prog = self._parse('Use javascript "lodash"')
        self.assertEqual(len(prog.statements), 1)
        stmt = prog.statements[0]
        self.assertIsInstance(stmt, ast.UseJSStatement)
        self.assertEqual(stmt.library, "lodash")
        self.assertEqual(stmt.alias, "lodash")
        self.assertFalse(stmt.is_typescript)

    def test_use_javascript_with_alias(self):
        """Use javascript "axios" as http → UseJSStatement with custom alias."""
        prog = self._parse('Use javascript "axios" as http')
        stmt = prog.statements[0]
        self.assertIsInstance(stmt, ast.UseJSStatement)
        self.assertEqual(stmt.library, "axios")
        self.assertEqual(stmt.alias, "http")
        self.assertFalse(stmt.is_typescript)

    def test_use_typescript_basic(self):
        """Use typescript "my-utils" → UseJSStatement with is_typescript=True."""
        prog = self._parse('Use typescript "my-utils"')
        stmt = prog.statements[0]
        self.assertIsInstance(stmt, ast.UseJSStatement)
        self.assertEqual(stmt.library, "my-utils")
        self.assertEqual(stmt.alias, "my_utils")  # hyphens sanitized
        self.assertTrue(stmt.is_typescript)

    def test_use_typescript_with_alias(self):
        """Use typescript "my-lib" as utils → UseJSStatement with custom alias."""
        prog = self._parse('Use typescript "my-lib" as utils')
        stmt = prog.statements[0]
        self.assertIsInstance(stmt, ast.UseJSStatement)
        self.assertEqual(stmt.library, "my-lib")
        self.assertEqual(stmt.alias, "utils")
        self.assertTrue(stmt.is_typescript)

    def test_use_javascript_scoped_package(self):
        """Use javascript "@google/generative-ai" as genai → scoped npm package."""
        prog = self._parse('Use javascript "@google/generative-ai" as genai')
        stmt = prog.statements[0]
        self.assertIsInstance(stmt, ast.UseJSStatement)
        self.assertEqual(stmt.library, "@google/generative-ai")
        self.assertEqual(stmt.alias, "genai")

    def test_use_python_still_works(self):
        """Use python "requests" → should still produce UseStatement (not UseJSStatement)."""
        prog = self._parse('Use python "requests"')
        stmt = prog.statements[0]
        self.assertIsInstance(stmt, ast.UseStatement)
        self.assertNotIsInstance(stmt, ast.UseJSStatement)

    def test_use_epl_package_still_works(self):
        """Use "my_module" → should still produce ImportStatement."""
        prog = self._parse('Use "my_module"')
        stmt = prog.statements[0]
        self.assertIsInstance(stmt, ast.ImportStatement)


# ═══════════════════════════════════════════════════════════
# Phase 2: AST Node Tests
# ═══════════════════════════════════════════════════════════

class TestUseJSStatementNode(unittest.TestCase):
    """Test the UseJSStatement AST node."""

    def test_node_creation(self):
        node = ast.UseJSStatement("lodash", "lodash", False, 1)
        self.assertEqual(node.library, "lodash")
        self.assertEqual(node.alias, "lodash")
        self.assertFalse(node.is_typescript)
        self.assertEqual(node.line, 1)

    def test_typescript_flag(self):
        node = ast.UseJSStatement("my-lib", "lib", True, 5)
        self.assertTrue(node.is_typescript)

    def test_default_values(self):
        node = ast.UseJSStatement("pkg")
        self.assertIsNone(node.alias)
        self.assertFalse(node.is_typescript)
        self.assertEqual(node.line, 0)


# ═══════════════════════════════════════════════════════════
# Phase 3: Token Tests
# ═══════════════════════════════════════════════════════════

class TestJavascriptToken(unittest.TestCase):
    """Test that 'javascript' is tokenized as a keyword."""

    def test_javascript_keyword_token(self):
        tokens = Lexer("javascript").tokenize()
        self.assertEqual(tokens[0].type, TokenType.JAVASCRIPT)

    def test_javascript_case_insensitive(self):
        tokens = Lexer("JavaScript").tokenize()
        self.assertEqual(tokens[0].type, TokenType.JAVASCRIPT)

    def test_typescript_is_identifier(self):
        """'typescript' is not a keyword; it should be tokenized as IDENTIFIER."""
        tokens = Lexer("typescript").tokenize()
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "typescript")


# ═══════════════════════════════════════════════════════════
# Phase 4: Bridge Manager Tests (Mocked)
# ═══════════════════════════════════════════════════════════

class TestNodeBridgeSerialization(unittest.TestCase):
    """Test the serialization/deserialization helpers."""

    def setUp(self):
        from epl.js_bridge import NodeBridge
        # Create a bridge instance without starting the process
        self.bridge = NodeBridge()

    def test_serialize_primitives(self):
        self.assertEqual(self.bridge._serialize_arg(None), {'type': 'null', 'value': None})
        self.assertEqual(self.bridge._serialize_arg(42), {'type': 'number', 'value': 42})
        self.assertEqual(self.bridge._serialize_arg(3.14), {'type': 'number', 'value': 3.14})
        self.assertEqual(self.bridge._serialize_arg("hello"), {'type': 'string', 'value': 'hello'})
        self.assertEqual(self.bridge._serialize_arg(True), {'type': 'boolean', 'value': True})

    def test_serialize_list(self):
        result = self.bridge._serialize_arg([1, "two", 3])
        self.assertEqual(result['type'], 'array')
        self.assertEqual(len(result['value']), 3)

    def test_serialize_dict(self):
        result = self.bridge._serialize_arg({"key": "value"})
        self.assertEqual(result['type'], 'object')

    def test_deserialize_primitives(self):
        self.assertIsNone(self.bridge._deserialize_result({'type': 'null', 'value': None}))
        self.assertEqual(self.bridge._deserialize_result({'type': 'number', 'value': 42}), 42)
        self.assertEqual(self.bridge._deserialize_result({'type': 'string', 'value': 'hi'}), 'hi')
        self.assertEqual(self.bridge._deserialize_result({'type': 'boolean', 'value': False}), False)

    def test_deserialize_array(self):
        result = self.bridge._deserialize_result({
            'type': 'array',
            'value': [
                {'type': 'number', 'value': 1},
                {'type': 'string', 'value': 'two'},
            ]
        })
        self.assertEqual(result, [1, 'two'])

    def test_deserialize_object(self):
        result = self.bridge._deserialize_result({
            'type': 'object',
            'value': {
                'name': {'type': 'string', 'value': 'EPL'},
                'version': {'type': 'number', 'value': 8},
            }
        })
        self.assertEqual(result, {'name': 'EPL', 'version': 8})

    def test_deserialize_handle(self):
        from epl.js_bridge import JSModuleHandle
        result = self.bridge._deserialize_result({
            'type': 'handle',
            'handle': 'h42',
            'typeName': 'Function'
        })
        self.assertIsInstance(result, JSModuleHandle)
        self.assertEqual(result.handle, 'h42')


# ═══════════════════════════════════════════════════════════
# Phase 5: JS Transpiler Tests
# ═══════════════════════════════════════════════════════════

class TestJSTranspilerUseJS(unittest.TestCase):
    """Test that UseJSStatement transpiles to correct import/require."""

    def test_esm_output(self):
        from epl.js_transpiler import JSTranspiler
        node = ast.UseJSStatement("axios", "http", False, 1)
        program = ast.Program([node])
        transpiler = JSTranspiler(target='browser', module_format='esm')
        output = transpiler.transpile(program)
        self.assertIn('import * as http from "axios"', output)

    def test_cjs_output(self):
        from epl.js_transpiler import JSTranspiler
        node = ast.UseJSStatement("lodash", "_", False, 1)
        program = ast.Program([node])
        transpiler = JSTranspiler(target='node', module_format='cjs')
        output = transpiler.transpile(program)
        self.assertIn('const _ = require("lodash")', output)

    def test_esm_node_output(self):
        from epl.js_transpiler import JSTranspiler
        node = ast.UseJSStatement("chalk", "chalk", False, 1)
        program = ast.Program([node])
        transpiler = JSTranspiler(target='node', module_format='esm')
        output = transpiler.transpile(program)
        self.assertIn('import * as chalk from "chalk"', output)


# ═══════════════════════════════════════════════════════════
# Phase 6: Error Explainer Tests
# ═══════════════════════════════════════════════════════════

class TestJSBridgeErrorExplainer(unittest.TestCase):
    """Test that the error explainer handles JS bridge errors."""

    def _explain(self, msg):
        from epl.error_explainer import explain
        # Create a mock error with .message and .line
        class MockError:
            def __init__(self, message):
                self.message = message
                self.line = 1
            def _error_code(self):
                return 'E0000'
        return explain(MockError(msg), source='Use javascript "test"')

    def test_node_not_installed(self):
        exp = self._explain('Node.js is not installed or not found in PATH.')
        self.assertIn('Node.js', exp.what_went_wrong)
        self.assertIn('nodejs.org', exp.how_to_fix)

    def test_module_not_found(self):
        exp = self._explain('JavaScript module "axios" is not installed.')
        self.assertIn('axios', exp.what_went_wrong)
        self.assertIn('jsinstall', exp.how_to_fix)

    def test_bridge_pipe_broken(self):
        exp = self._explain('JS bridge pipe broken: Connection refused')
        self.assertIn('crashed', exp.what_went_wrong)


# ═══════════════════════════════════════════════════════════
# Phase 7: Integration Tests (requires Node.js)
# ═══════════════════════════════════════════════════════════

@unittest.skipUnless(shutil.which('node'), "Node.js not installed — skipping integration tests")
class TestNodeBridgeIntegration(unittest.TestCase):
    """Integration tests that run against a real Node.js process."""

    def setUp(self):
        from epl.js_bridge import NodeBridge
        NodeBridge.reset()  # Clean singleton
        self.bridge = NodeBridge.get_instance()

    def tearDown(self):
        from epl.js_bridge import NodeBridge
        NodeBridge.reset()

    def test_require_builtin_path(self):
        """Require a Node.js built-in module."""
        handle = self.bridge.require("path")
        self.assertIsNotNone(handle)
        self.assertTrue(handle.startswith("h"))

    def test_call_path_join(self):
        """Call path.join() via the bridge."""
        handle = self.bridge.require("path")
        result = self.bridge.call(handle, "join", ["/home", "user", "file.txt"])
        # On Windows or Unix, path.join will produce different results
        self.assertIsInstance(result, str)
        self.assertIn("file.txt", result)

    def test_call_path_basename(self):
        """Call path.basename() via the bridge."""
        handle = self.bridge.require("path")
        result = self.bridge.call(handle, "basename", ["/home/user/file.txt"])
        self.assertEqual(result, "file.txt")

    def test_get_property(self):
        """Get a property from a module."""
        handle = self.bridge.require("path")
        sep = self.bridge.get_prop(handle, "sep")
        self.assertIn(sep, ['/', '\\'])

    def test_require_nonexistent_module_raises(self):
        """Requiring a module that doesn't exist should raise an error."""
        from epl.js_bridge import NodeBridgeError
        with self.assertRaises(NodeBridgeError):
            self.bridge.require("__nonexistent_epl_test_module__")

    def test_call_math_via_eval(self):
        """Require a built-in like 'os' and check type."""
        handle = self.bridge.require("os")
        result = self.bridge.call(handle, "platform", [])
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


# ═══════════════════════════════════════════════════════════
# Phase 8: Interpreter JSModule Tests
# ═══════════════════════════════════════════════════════════

class TestJSModuleClass(unittest.TestCase):
    """Test the JSModule wrapper class in the interpreter."""

    def test_jsmodule_repr(self):
        from epl.interpreter import JSModule
        mod = JSModule(bridge=None, handle="h1", name="lodash")
        self.assertEqual(repr(mod), "<js module lodash>")

    def test_jsmodule_attributes(self):
        from epl.interpreter import JSModule
        mod = JSModule(bridge="bridge_ref", handle="h42", name="axios")
        self.assertEqual(mod.handle, "h42")
        self.assertEqual(mod.name, "axios")
        self.assertEqual(mod.bridge, "bridge_ref")


if __name__ == '__main__':
    unittest.main()
