/**
 * EPL Node.js Bridge Worker
 * 
 * A persistent Node.js process that receives JSON commands from EPL
 * over stdin and sends JSON responses over stdout.
 * 
 * Protocol: One JSON object per line (newline-delimited JSON).
 * 
 * Commands:
 *   require  — Load an npm/local module, return a handle
 *   call     — Call a function or method on a handle
 *   get      — Get a property from a handle
 *   set      — Set a property on a handle
 *   delete   — Release a handle from memory
 *   shutdown — Exit the worker process
 */

'use strict';

const { createRequire } = require('module');
const path = require('path');

// Handle registry — maps string IDs to live JS objects
const handles = new Map();
let nextHandleId = 1;

// The require function anchored to the working directory
const localRequire = createRequire(path.resolve(process.cwd(), 'node_modules'));

/**
 * Store a value and return its handle ID.
 * Primitives are returned inline (no handle needed).
 */
function storeHandle(value) {
    const id = 'h' + (nextHandleId++);
    handles.set(id, value);
    return id;
}

/**
 * Serialize a value for transport back to EPL.
 * Primitives are sent inline. Complex objects get a handle.
 */
function serialize(value) {
    if (value === null || value === undefined) {
        return { type: 'null', value: null };
    }
    if (typeof value === 'boolean') {
        return { type: 'boolean', value: value };
    }
    if (typeof value === 'number') {
        return { type: 'number', value: value };
    }
    if (typeof value === 'string') {
        return { type: 'string', value: value };
    }
    if (Array.isArray(value)) {
        // Serialize arrays with items up to a reasonable depth
        try {
            const items = value.map(item => serialize(item));
            return { type: 'array', value: items };
        } catch {
            const handle = storeHandle(value);
            return { type: 'handle', handle: handle, typeName: 'Array' };
        }
    }
    if (typeof value === 'object') {
        // Try to serialize plain objects inline
        const proto = Object.getPrototypeOf(value);
        if (proto === Object.prototype || proto === null) {
            try {
                const result = {};
                for (const [k, v] of Object.entries(value)) {
                    result[k] = serialize(v);
                }
                return { type: 'object', value: result };
            } catch {
                // Fall through to handle
            }
        }
        // Complex object — store as handle
        const handle = storeHandle(value);
        const typeName = value.constructor ? value.constructor.name : 'Object';
        return { type: 'handle', handle: handle, typeName: typeName };
    }
    if (typeof value === 'function') {
        const handle = storeHandle(value);
        return { type: 'handle', handle: handle, typeName: 'Function' };
    }
    // Fallback
    return { type: 'string', value: String(value) };
}

/**
 * Deserialize a value coming from EPL back into JS.
 */
function deserialize(item) {
    if (item === null || item === undefined) return item;
    if (typeof item !== 'object') return item;
    if (item.type === 'null') return null;
    if (item.type === 'boolean') return item.value;
    if (item.type === 'number') return item.value;
    if (item.type === 'string') return item.value;
    if (item.type === 'handle') return handles.get(item.handle);
    if (item.type === 'array') return (item.value || []).map(deserialize);
    if (item.type === 'object') {
        const result = {};
        for (const [k, v] of Object.entries(item.value || {})) {
            result[k] = deserialize(v);
        }
        return result;
    }
    // Raw value fallback (plain primitives sent directly)
    if (item.value !== undefined) return item.value;
    return item;
}

/**
 * Process a single command and return a response object.
 */
async function processCommand(cmd) {
    const id = cmd.id;
    try {
        switch (cmd.cmd) {
            case 'require': {
                let mod;
                try {
                    mod = require(cmd.module);
                } catch {
                    mod = localRequire(cmd.module);
                }
                const handle = storeHandle(mod);
                return { id, ok: true, handle, typeName: typeof mod };
            }

            case 'call': {
                const obj = handles.get(cmd.handle);
                if (!obj) return { id, ok: false, error: `Invalid handle: ${cmd.handle}` };

                const args = (cmd.args || []).map(deserialize);

                let result;
                if (cmd.method) {
                    // Method call: obj.method(args)
                    if (typeof obj[cmd.method] !== 'function') {
                        return { id, ok: false, error: `"${cmd.method}" is not a function on this object.` };
                    }
                    result = obj[cmd.method](...args);
                } else {
                    // Direct call: obj(args) — for when the handle IS a function
                    if (typeof obj !== 'function') {
                        return { id, ok: false, error: 'Object is not callable.' };
                    }
                    result = obj(...args);
                }

                // Await promises automatically
                if (result && typeof result.then === 'function') {
                    result = await result;
                }

                return { id, ok: true, result: serialize(result) };
            }

            case 'get': {
                const obj = handles.get(cmd.handle);
                if (!obj) return { id, ok: false, error: `Invalid handle: ${cmd.handle}` };

                const prop = cmd.prop;
                if (!(prop in obj) && obj[prop] === undefined) {
                    return { id, ok: false, error: `Property "${prop}" does not exist.` };
                }

                const value = obj[prop];
                return { id, ok: true, result: serialize(value) };
            }

            case 'set': {
                const obj = handles.get(cmd.handle);
                if (!obj) return { id, ok: false, error: `Invalid handle: ${cmd.handle}` };

                obj[cmd.prop] = deserialize(cmd.value);
                return { id, ok: true };
            }

            case 'delete': {
                handles.delete(cmd.handle);
                return { id, ok: true };
            }

            case 'shutdown': {
                // Send response before exiting
                send({ id, ok: true });
                process.exit(0);
                break;
            }

            default:
                return { id, ok: false, error: `Unknown command: ${cmd.cmd}` };
        }
    } catch (err) {
        return { id, ok: false, error: err.message || String(err) };
    }
}

/**
 * Send a JSON response to stdout (one line).
 */
function send(obj) {
    process.stdout.write(JSON.stringify(obj) + '\n');
}

// ─── Main Loop: Read stdin line by line ─────────────────

let buffer = '';

process.stdin.setEncoding('utf-8');
process.stdin.on('data', async (chunk) => {
    buffer += chunk;
    let newlineIndex;
    while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
        const line = buffer.slice(0, newlineIndex).trim();
        buffer = buffer.slice(newlineIndex + 1);

        if (!line) continue;

        let cmd;
        try {
            cmd = JSON.parse(line);
        } catch (parseErr) {
            send({ id: null, ok: false, error: `Invalid JSON: ${parseErr.message}` });
            continue;
        }

        const response = await processCommand(cmd);
        if (response) send(response);
    }
});

process.stdin.on('end', () => {
    process.exit(0);
});

// Signal readiness
send({ id: 0, ok: true, ready: true });
