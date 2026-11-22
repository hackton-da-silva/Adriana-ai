export function plantMcpServers(postmortemToolToken?: string) {
  const token = process.env.PLANTA_MCP_TOKEN;
  const origin = process.env.AGORA_ANNOTATION_ORIGIN;
  if (!token || !origin) return [];
  const url = URL.parse(origin);
  if (!url || url.protocol !== 'https:' || url.username || url.password) return [];

  return [
    { name: 'TelemetriaCLPLTQ', path: 'telemetria', tools: ['status_clp', 'status_maquina', 'historico'] },
    { name: 'DocumentacaoPlantaLTQ', path: 'documentacao', tools: ['consultar_documentacao_equipamento_ltq', 'consultar_manual_clp'] },
  ].map(({ name, path, tools }) => ({
    name,
    endpoint: new URL('/api/planta/' + path, url).href,
    transport: 'streamable_http' as const,
    headers: { Authorization: 'Bearer ' + token, ...(postmortemToolToken && { 'X-Postmortem-Tool': postmortemToolToken }) },
    allowed_tools: tools,
    timeout_ms: 5000,
  }));
}
