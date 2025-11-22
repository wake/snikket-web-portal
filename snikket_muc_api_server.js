// server.js - Node v12 可用
const http = require('http');
const { spawn } = require('child_process');

const HOST = '127.0.0.1';
const PORT = 5999;
const DOCKER_CONTAINER = 'snikket';

// 非常保守的 JID / 房間 / 權限檢查，避免被 injection
function isValidRoom(room) {
  return /^[a-zA-Z0-9._-]+@groups\.chat\.protype\.tw$/.test(room);
}

function isValidUser(user) {
  return /^[a-zA-Z0-9._-]+@chat\.protype\.tw$/.test(user);
}

function isValidAffiliation(aff) {
  return ['owner', 'admin', 'member', 'none', 'outcast'].indexOf(aff) !== -1;
}

function runProsodyShell(luaCode, callback) {
  const args = [
    'exec',
    DOCKER_CONTAINER,
    'prosodyctl',
    'shell',
    luaCode
  ];

  const proc = spawn('docker', args);

  let stdout = '';
  let stderr = '';

  proc.stdout.on('data', (data) => {
    stdout += data.toString();
  });

  proc.stderr.on('data', (data) => {
    stderr += data.toString();
  });

  proc.on('close', (code) => {
    callback(code, stdout, stderr);
  });
}

function sendJson(res, statusCode, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body)
  });
  res.end(body);
}

const server = http.createServer((req, res) => {
  if (req.method !== 'POST') {
    return sendJson(res, 405, { error: 'Method Not Allowed' });
  }

  let body = '';
  req.on('data', chunk => {
    body += chunk.toString();
    if (body.length > 1e6) { // 1MB 防止惡意
      req.connection.destroy();
    }
  });

  req.on('end', () => {
    let data;
    try {
      data = JSON.parse(body || '{}');
    } catch (e) {
      return sendJson(res, 400, { error: 'Invalid JSON' });
    }

    if (req.url === '/muc/list') {
      const mucDomain = data.muc_domain;
      if (typeof mucDomain !== 'string' || !mucDomain.endsWith('.protype.tw')) {
        return sendJson(res, 400, { error: 'Invalid muc_domain' });
      }

      const lua = "muc:list('" + mucDomain.replace(/'/g, "\\'") + "')";
      return runProsodyShell(lua, (code, stdout, stderr) => {
        if (code !== 0) {
          return sendJson(res, 500, { error: 'prosody error', stderr });
        }
        return sendJson(res, 200, { ok: true, stdout });
      });

    } else if (req.url === '/muc/get-affiliation') {
      const room = data.room;
      const user = data.user;

      if (!isValidRoom(room) || !isValidUser(user)) {
        return sendJson(res, 400, { error: 'Invalid room or user' });
      }

      const lua =
        "muc:room('" + room + "'):get_affiliation('" + user + "')";
      return runProsodyShell(lua, (code, stdout, stderr) => {
        if (code !== 0) {
          return sendJson(res, 500, { error: 'prosody error', stderr });
        }
        return sendJson(res, 200, { ok: true, stdout });
      });

    } else if (req.url === '/muc/set-affiliation') {
      const room = data.room;
      const user = data.user;
      const affiliation = data.affiliation;

      if (!isValidRoom(room) || !isValidUser(user) || !isValidAffiliation(affiliation)) {
        return sendJson(res, 400, { error: 'Invalid room, user, or affiliation' });
      }

      const lua =
        "muc:room('" + room + "'):set_affiliation(true, '" +
        user + "', '" + affiliation + "')";

      return runProsodyShell(lua, (code, stdout, stderr) => {
        if (code !== 0) {
          return sendJson(res, 500, { error: 'prosody error', stderr });
        }
        return sendJson(res, 200, { ok: true, stdout });
      });

    } else {
      return sendJson(res, 404, { error: 'Not Found' });
    }
  });
});

server.listen(PORT, HOST, () => {
  console.log(`MUC API server listening on http://${HOST}:${PORT}`);
});
