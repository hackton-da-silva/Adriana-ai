# 02 Architecture

> Runtime architecture for browser RTC/RTM, Next.js route handlers, and Agora managed agent session.

## High-Level Shape

- The root workspace defaults to a local person detector, with a Tripo showcase video available in the LTQ tab, next to a same-origin `/voice` iframe. `/voice` owns the original voice app; its opt-in camera control publishes video via the same RTC client, and Agora supplies frames to the text-and-image LLM. The separate local detector does not forward images or annotations. `PersonDetectionTest` owns its video-only stream and overlay; TensorFlow/COCO-SSD loads only after a user action, with local weights and WebGL/CPU backends. Inference is serialized and stale runs are ignored; tab switching releases camera tracks without remounting the voice iframe.
- Next.js App Router frontend and API routes in one deployable app.
- Browser joins Agora RTC channel and uses RTM for transcript/state/metrics/errors.
- Server-side routes mint token and call Agora Agent Server SDK.
- Agent executes STT -> LLM -> TTS pipeline in Agora cloud.

## Component Graph

```text
Browser UI (LandingPage + ConversationComponent)
  -> GET /api/generate-agora-token
  -> POST /api/invite-agent
  -> RTC join/publish mic
  -> RTM subscribe + AgoraVoiceAI events
  -> POST /api/stop-conversation

Next.js API routes
  -> agora-token (RtcTokenBuilder.buildTokenWithRtm)
  -> agora-agents (start/stop managed agent)

Agora Cloud
  -> Agent session (Deepgram STT + OpenAI LLM + MiniMax TTS by default)
  -> RTM payloads (transcript, state, metrics, error)
```

## Start Sequence

1. UI fetches RTC+RTM token and channel.
2. UI invites agent and initializes RTM in parallel.
3. UI mounts conversation view.
4. `useJoin` connects RTC once `isReady` guard passes.
5. `AgoraVoiceAI.init()` subscribes transcript/state/metrics streams.

## End Sequence

1. UI calls `/api/stop-conversation` with `agent_id` if present.
2. UI logs out RTM client.
3. RTC hook ownership handles leave/unpublish cleanup.
4. Component state resets to pre-call shell.

## Core State Domains

- Session bootstrap: `LandingPage` (`agoraData`, `rtmClient`, loading/error flags).
- RTC transport and mic: `ConversationComponent` + `agora-rtc-react` hooks.
- Transcript + agent state: `AgoraVoiceAI` events mapped through `lib/conversation.ts`.
- Metrics and connection issues: `AGENT_METRICS`, `MESSAGE_ERROR`, `SAL_STATUS`, RTM fallback parsing.

## External Dependencies

- `agora-rtc-react` / `agora-rtc-sdk-ng` for media transport.
- `agora-rtm` for data channel.
- `agora-agent-client-toolkit` and `agora-agent-uikit` for conversation logic/UI.
- `agora-agents` for managed agent lifecycle.

## Deployment Modes

- Local development via `pnpm run dev`.
- Vercel deployment as single Next.js app with server env vars.

## Data and Control Boundaries

- Browser never sees the app certificate; only receives signed short-lived tokens.
- Agent lifecycle control (`start`, `stop`) is server-routed.
- Transcript/state/metrics are data-plane RTM events from agent to browser.
- UI control-plane actions (start/end, renew) originate in `LandingPage`.

## Internal Interfaces Between Components

`LandingPage` -> `ConversationComponent` props:

- `agoraData` (`token`, `uid`, `channel`, optional `agentId`)
- `rtmClient` (already logged-in and subscribed)
- `onTokenWillExpire(uid)` callback for dual-token renewal
- `onEndConversation()` callback for teardown and route stop call

`ConversationComponent` -> child UI components:

- normalized transcript items and current in-progress turn
- agent visualizer state derived from transport + semantic state
- connection issue list and derived severity
- recent metric window for stage latency chips

## Why the App Router Structure Matters

- API handlers under `app/api` co-deploy with UI and share env management.
- Client components isolate browser-only SDK usage via dynamic import and `ssr: false`.
- This avoids SSR-side access to WebRTC-dependent modules.

## Change Impact Hints

- Changes to token or invite routes affect both startup and renewal paths.
- Changes to transcript mapping can break both transcript panel and visualizer semantics.
- Changes to RTM setup in `LandingPage` affect toolkit subscription readiness.

## Related Deep Dives

- [conversation_lifecycle.md](L2/conversation_lifecycle.md) — Detailed bootstrapping and teardown timeline.
- [transcript_pipeline.md](L2/transcript_pipeline.md) — Event mapping, UID remap, in-progress/completed segmentation.

## Voice annotation

The Agora REST tool queues a request for the browser in the same Next.js process. The browser submits one JPEG from its live Agora preview. OpenAI returns normalized bounds, which the browser draws on the submitted frame while Agora receives the outcome for its voice response.

The document RAG uses a private BM25 index, a local vector cache, and a process-local job queue. The worker fuses lexical and semantic ranks and falls back to BM25 if embeddings are unavailable. The authenticated MCP start tool replies immediately. The worker retrieves passages and uses OpenAI to synthesize a cited answer. A completed user utterance about maintenance can reach the same queue through the browser fallback when the MCP call was missed. The worker sends terminal results to the originating Agora session via think with append actions. The browser polls for display and offers manual playback.

The optional Langfuse exporter correlates Agora invite, browser microphone/transcript signals, MCP discovery and execution, retrieval/generation, RTC camera state and the explicit single-frame vision tools using one server-generated trace ID per call.

### Retry e fallback Feita

Configure `FEITA_API_KEY` no servidor para ativar a Feita como fallback do manual e da análise de câmera. O adaptador em `lib/ai-provider.ts` faz até duas novas tentativas por provedor em falhas transitórias, com backoff exponencial (200 ms, 400 ms) e jitter de até 149 ms, respeitando Retry-After e o prazo total. Se a OpenAI falhar, a Feita recebe a pergunta e os trechos recuperados ou o quadro solicitado. O modelo padrão é `qwen/qwen4-max`, configurável por `FEITA_MODEL`. Para embeddings, o fallback continua sendo a busca por BM25. A voz usa o Agora.

## Post-call reporting

Invite creates an independent capability and journal correlated by trace ID. usePostmortem batches completed/interrupted turns and diagnostics while the server journals manual/vision/plant tool results separately from Langfuse. Stop seals the matching session and queues a bounded asynchronous generator; pagehide or two-minute heartbeat inactivity can also seal it. Up to two workers checkpoint JSON, request schema-validated analysis, and atomically write private Markdown/JSON under files/postmortems/. Provider failure produces a basic report with original evidence. Collection and queue are process-local; sealed sessions exclude later tool results.
