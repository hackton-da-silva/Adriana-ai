import { recordPostmortemTool } from '@/lib/postmortem';
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
  const raw = await request.text();
  let call: { method?: string; params?: { name?: string; arguments?: unknown } } | undefined;
  try { call = JSON.parse(raw); } catch {}
  const tool = call?.method === 'tools/call' ? call.params : undefined;
  const startedAt = Date.now();
  const capability = request.headers.get('X-Postmortem-Tool');
  if (tool) recordPostmortemTool(capability, `plant.${servico}.requested`, { tool: tool.name, arguments: tool.arguments, status: 'pending', simulated: true });
  try {
    const upstream = await fetch(`http://127.0.0.1:${port}/mcp`, {
      method: 'POST',
      headers,
      body: raw,
      redirect: 'error',
      signal: AbortSignal.timeout(5000),
    });
    // These fixed Python services use stateless JSON responses, not SSE streams.
    const responseBody = await upstream.text();
    if (tool) {
      let result: unknown = { status: 'unreadable_response' };
      try { result = JSON.parse(responseBody); } catch {}
      recordPostmortemTool(capability, `plant.${servico}.result`, { tool: tool.name, result, httpStatus: upstream.status, durationMs: Date.now() - startedAt, simulated: true });
    }
    return new Response(responseBody, {
      status: upstream.status,
      headers: { 'content-type': upstream.headers.get('content-type') ?? 'application/json' },
    });
  } catch {
    if (tool) recordPostmortemTool(capability, `plant.${servico}.result`, { tool: tool.name, status: 'unavailable', durationMs: Date.now() - startedAt, simulated: true });
    return Response.json({ error: 'Serviço da planta indisponível.' }, { status: 503 });
  }
}
