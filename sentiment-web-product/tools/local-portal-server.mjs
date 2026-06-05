import { createReadStream, existsSync, statSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'node:http';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const root = resolve(__dirname, '../local_portal');
const port = Number(process.env.PORT || 8080);
const host = process.env.HOST || '127.0.0.1';

const mimeTypes = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
};

function safePath(pathname) {
  const decoded = decodeURIComponent(pathname.split('?')[0]);
  const normalized = normalize(decoded).replace(/^(\.\.[/\\])+/, '');
  const filePath = resolve(join(root, normalized));
  return filePath.startsWith(root) ? filePath : null;
}

async function sendError(response, status, message) {
  response.writeHead(status, { 'Content-Type': 'text/plain; charset=utf-8' });
  response.end(message);
}

createServer(async (request, response) => {
  const url = new URL(request.url || '/', `http://${request.headers.host || 'localhost'}`);
  let filePath = safePath(url.pathname);
  if (!filePath) {
    await sendError(response, 403, 'Forbidden');
    return;
  }

  if (url.pathname === '/platform') {
    response.writeHead(301, { Location: '/platform/' });
    response.end();
    return;
  }

  if (existsSync(filePath) && statSync(filePath).isDirectory()) {
    filePath = join(filePath, 'index.html');
  }

  if (!existsSync(filePath)) {
    await sendError(response, 404, 'Not Found');
    return;
  }

  const extension = extname(filePath);
  response.writeHead(200, {
    'Content-Type': mimeTypes[extension] || 'application/octet-stream',
  });

  if (extension === '.html') {
    response.end(await readFile(filePath));
    return;
  }

  createReadStream(filePath).pipe(response);
}).listen(port, host, () => {
  console.log(`Local portal is running at http://localhost:${port}/`);
});
