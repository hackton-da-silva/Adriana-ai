# 06 Interfaces

> Contracts at repo boundaries: API routes, env vars, runtime events, and shared TypeScript payloads.

## HTTP Route Contracts

### `GET /api/generate-agora-token`

Query params:

- `uid` optional; invalid/zero resolves to random RTM-safe UID.
- `channel` optional; defaults to generated `ai-conversation-<ts>-<rand>`.

Success response:

```json
{ "token": "...", "uid": "1234", "channel": "ai-conversation-..." }
```

Failure response: `{ "error": string, "details"?: string }` with `500`.

### `POST /api/invite-agent`

Body (`ClientStartRequest`):

```json
{ "requester_id": "1234", "channel_name": "ai-conversation-..." }
```

Success (`AgentResponse`):

```json
{ "agent_id": "...", "create_ts": 1710000000, "state": "RUNNING" }
```

Validation failures return `400`; server failures return `500`.

### `POST /api/stop-conversation`

Body (`StopConversationRequest`): `{ "agent_id": "..." }`.

Responses:

- `{ "success": true }`
- `{ "success": true, "state": "already-stopping" }` for idempotent stop state
- `{ "error": string }` on failure

### `POST /api/chat/completions`

Optional SSE proxy path (not default runtime path). Requires `NEXT_LLM_API_KEY` and `NEXT_LLM_URL` when used.

## Event/Data Interfaces

- RTM transcript/state/metrics/errors consumed through `AgoraVoiceAI` event emitter.
- Raw RTM `message` event parsed as fallback for `message.error` and `message.sal_status` payloads.
- `AGENT_METRICS` payloads displayed by `QuickstartPipelineMetrics`.

## Environment Contract

Required:

- `NEXT_PUBLIC_AGORA_APP_ID`
- `NEXT_AGORA_APP_CERTIFICATE`

This is the complete base `.env.local` contract. The optional BYOK route and provider snippets use additional variables only when a developer explicitly enables them.

## Test Coverage for Interfaces

- `scripts/verify-api-contracts.ts` asserts token generation, input validation, env failures, and SSE framing cases.

## Shared Client-Side Interfaces

From `types/conversation.ts` (high-use):

- `AgoraTokenData`: token bootstrap payload consumed by `LandingPage`.
- `AgoraRenewalTokens`: renewal callback result (`rtcToken`, `rtmToken`).
- `ConversationComponentProps`: runtime dependencies for in-call component.

## Interface Invariants

- Token payload must always include `token`, `uid`, `channel`.
- Invite route requires both `requester_id` and `channel_name`.
- Stop route requires `agent_id`; missing should never be tolerated silently.
- Token route should always return UID as string for downstream compatibility.

## Event Interface Notes

- Metrics stream entries are append-only in component state, capped to recent window.
- Connection issue records carry `source`, `agentUserId`, code/message, timestamp.
- SAL and signaling fallback payloads are parsed defensively because message schema can vary.

## Backward Compatibility Guidance

- If route response shape changes, update both client consumers and contract tests in same change.
- If adding fields, keep existing fields stable to avoid quickstart consumer breakage.
- Reflect interface changes in README and L1 docs to keep sample copyable.

## Related Deep Dives

- [conversation_lifecycle.md](L2/conversation_lifecycle.md) — How route contracts are used in sequence.
- [transcript_pipeline.md](L2/transcript_pipeline.md) — Event-level contract mapping.

## Local Visual Detector

`lib/visual-detection.ts` defines `VisualDetector.detect(video | canvas)` returning `{label, score, box: {x, y, width, height}}[]`, with confidence and coordinates normalized to 0–1. `dispose()` releases model resources after pending inference completes. The current adapter filters `person`; future industrial adapters must keep the coordinate contract. There is no vision API route, RTM detection event, voice tool, or additional environment variable.

With annotation configured, the invite response includes an optional `annotation_token`. The annotation route accepts an authenticated Agora POST, an authenticated browser GET for pending work and a PUT with its job ID and one JPEG (or null when the camera is off). Returned boxes use normalized top-left coordinates.

When configured, invite returns an optional `research_token` for the browser. `POST /api/document-mcp` speaks stateless Streamable HTTP with a separate session capability and advertises the `ManualManutencaoLTQ` server with `consultar_manual_de_manutencao` and `consultar_resultado`. `consultar_manual_de_manutencao` accepts the original query and optional translated `search_terms`, used for BM25 when supplied. The original question drives semantic retrieval and answer generation. `GET /api/document-results` uses the browser capability and returns that call’s pending or completed jobs. An authenticated POST on the same route can route an eligible completed user turn if no recent job exists. The server validates scope, suppresses repeats, and keeps the same job limits. If Agora delivery fails, the browser result includes deliveryFailed. Answers cite the title and page or section from the input index.

`POST /api/call-telemetry` uses the browser research capability and accepts microphone flags a camera state, or a transcript turn number, character count and eligibility flag. It does not accept text or media.

With server-side PLANTA_MCP_TOKEN and HTTPS AGORA_ANNOTATION_ORIGIN configured, invite-agent also registers TelemetriaCLPLTQ (status_clp, status_maquina, historico) and DocumentacaoPlantaLTQ (consultar_documentacao_equipamento_ltq, consultar_manual_clp). The authenticated Next.js POST route forwards /api/planta/telemetria and /api/planta/documentacao to loopback ports 8011 and 8012 respectively. The upstreams require Bearer authentication. Both endpoints expose simulated plant data. SKF research remains optional.

Document jobs return `not_found` for zero excerpts, `insufficient_evidence` for an explicit abstention after retrieval, and `failed` for provider or answer-format errors.
