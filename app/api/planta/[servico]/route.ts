import { timingSafeEqual } from 'node:crypto';

const ports = new Map([['telemetria', 8011], ['documentacao', 8012]]);

export async function POST(request: Request, context: { params: Promise<{ servico: string }> }) {
  const { servico } = await context.params;
  const port = ports.get(servico);
  const token = process.env.PLANTA_MCP_TOKEN;
  if (!port || !token) return new Response(null, { status: 404 });

  const authorization = request.headers.get('authorization') ?? '';
  const supplied = Buffer.from(authorization);
  const expected = Buffer.from('Bearer ' + token);
  if (supplied.length !== expected.length || !timingSafeEqual(supplied, expected)) {
    return new Response(null, { status: 401 });
  }

  const headers = new Headers({
    authorization,
    'content-type': 'application/json',
    accept: 'application/json, text/event-stream',
  });
  const version = request.headers.get('mcp-protocol-version');
  if (version) headers.set('mcp-protocol-version', version);
  try {
    const upstream = await fetch(`http://127.0.0.1:${port}/mcp`, {
      method: 'POST',
      headers,
      body: await request.text(),
      redirect: 'error',
      signal: AbortSignal.timeout(5000),
    });
    return new Response(upstream.body, {
      status: upstream.status,
      headers: { 'content-type': upstream.headers.get('content-type') ?? 'application/json' },
    });
  } catch {
    return Response.json({ error: 'Serviço da planta indisponível.' }, { status: 503 });
  }
}
