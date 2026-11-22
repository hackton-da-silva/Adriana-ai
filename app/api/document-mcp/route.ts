import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { WebStandardStreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js';
import { z } from 'zod';
import { CONSULT_MAINTENANCE_MANUAL, getResearchSession, MAINTENANCE_MANUAL_MCP, startResearch } from '@/lib/document-research';
import { traceCall } from '@/lib/call-observability';

export const runtime = 'nodejs';

export async function POST(request: Request) {
  const auth = request.headers.get('Authorization');
  const session = getResearchSession(auth?.startsWith('Bearer ') ? auth.slice(7) : null, 'mcp');
  if (!session) return new Response(null, { status: 401 });
  const startedAt = Date.now();
  const body = await request.clone().json().catch(() => null);
  const mcp = new McpServer({ name: MAINTENANCE_MANUAL_MCP, version: '1.0.0' }, {
    instructions: 'Consulte o manual SKF para fundamentar a manutenção dos rolamentos do laminador de tiras a quente.',
  });
  const transport = new WebStandardStreamableHTTPServerTransport({ enableJsonResponse: true });
  const language = process.env.RAG_DOCUMENT_LANGUAGE?.trim();
  function output(value: unknown) {
    return { content: [{ type: 'text' as const, text: JSON.stringify(value) }] };
  }
  mcp.registerTool(CONSULT_MAINTENANCE_MANUAL, {
    description: 'Pesquisa sintomas, inspeção e manutenção de rolamentos cilíndricos de quatro carreiras no manual SKF. Retorna o ID da consulta em segundo plano.',
    inputSchema: {
      query: z.string().min(1).max(450).describe('Pergunta ou relato do usuário, com o componente e sintoma inferidos da conversa.'),
      search_terms: z.string().min(1).max(450).optional().describe(language
        ? `Traduza os termos técnicos da pergunta para o idioma do documento (${language}). Preserve siglas e códigos de peças.`
        : 'Termos técnicos alternativos para encontrar a resposta no documento.'),
    },
  }, ({ query, search_terms }) => {
    const result = startResearch(session, query, search_terms);
    traceCall(session.trace, {
      name: `mcp.${CONSULT_MAINTENANCE_MANUAL}`, type: 'tool',
      input: { tool: CONSULT_MAINTENANCE_MANUAL, queryCharacters: query.length, translatedTerms: Boolean(search_terms) },
      data: { status: result.status, ...(result.id && { jobId: result.id }) },
    });
    return output(result);
  });
  mcp.registerTool('consultar_resultado', {
    description: 'Recupera o andamento ou a resposta de uma pesquisa SKF pelo ID quando o operador pedir uma atualização.',
    inputSchema: { id: z.string().uuid() },
  }, ({ id }) => output(session.jobs.get(id)?.result ?? { status: 'unknown' }));
  await mcp.connect(transport);
  const response = await transport.handleRequest(request);
  const method = body?.method;
  if (method === 'initialize' || method === 'tools/list' || method === 'tools/call') {
    let tools = '';
    if (method === 'tools/list' && response.ok) {
      const listed = await response.clone().json().catch(() => null);
      if (Array.isArray(listed?.result?.tools)) {
        tools = listed.result.tools.map((tool: { name: string }) => tool.name).join(', ');
      }
    }
    traceCall(session.trace, {
      name: `mcp.${method.replace('/', '_')}`, type: 'event', startedAt,
      input: { method, transport: 'streamable_http' },
      error: !response.ok, data: { httpStatus: response.status, ...(tools && { tools }) },
    });
  }
  return response;
}

export function GET() {
  return new Response(null, { status: 405, headers: { Allow: 'POST' } });
}
