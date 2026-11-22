# Agent Development Guide

This guide is for coding agents making changes in `agent-quickstart-nextjs`.

## How to Load

This repository uses progressive disclosure documentation. Docs live under `docs/ai/` in three levels.

1. Read [docs/ai/L0_repo_card.md](docs/ai/L0_repo_card.md) to identify the repo.
2. Load ALL 8 files in [docs/ai/L1/](docs/ai/L1/). They are small — load all upfront.
3. Follow L2 deep-dive links only when L1 isn't detailed enough. The index is at [docs/ai/L1/L2/_index.md](docs/ai/L1/L2/_index.md).

This repo declares `Recipe Role: base` in L0, so also read [docs/ai/RECIPE.md](docs/ai/RECIPE.md) when evaluating extension points, invariants, or stable contracts.

The sections below (Start Here, Patterns, Anti-Patterns, etc.) remain the canonical contributor handbook for hands-on work; the `docs/ai/` tree is the structured summary used by AI agents.

## Start Here

- Read [README.md](./README.md) for setup, commands, verification, and deployment.
- Use [docs/ai/RECIPE.md](docs/ai/RECIPE.md) for the base quickstart recipe contract.
- Use [docs/ai/L1/L2/from_scratch_bootstrap.md](docs/ai/L1/L2/from_scratch_bootstrap.md) for the baseline implementation map.
- Use [docs/ai/L1/L2/transcript_pipeline.md](docs/ai/L1/L2/transcript_pipeline.md) for transcript and RTM behavior.
- For layout and responsibilities inside `components/`, `app/api/`, and `lib/`, use [docs/ai/L1/03_code_map.md](docs/ai/L1/03_code_map.md) and [docs/ai/L1/02_architecture.md](docs/ai/L1/02_architecture.md).

## Current System Shape

- App shell: Next.js 16 App Router, React 19, and TypeScript
- Client RTC: `agora-rtc-react` hooks over `agora-rtc-sdk-ng`
- Messaging: `agora-rtm` for transcripts, agent state, metrics, and error events
- Toolkit core: `agora-agent-client-toolkit` for `AgoraVoiceAI`, transcript helpers, and turn status
- UI components: `agora-agent-uikit` for visualizer, transcript, and mic controls
- Server SDK: `agora-agents` for managed agent session startup
- API routes: token generation, agent invite, chat, and stop routes live in `app/api`
- Default agent config: Agora-managed STT, LLM, and TTS; `.env.local` contains only Agora project credentials

## Supported Modes

### Local Development

- Run from the repo root with `pnpm run dev`.
- Next.js serves the app and the route handlers at `http://localhost:3000`.
- Local credentials are read from `.env.local`, usually written by `agora project env write .env.local`.

### Vercel Deployment

- Deploy the repository as a single Next.js app.
- Set `NEXT_PUBLIC_AGORA_APP_ID` and `NEXT_AGORA_APP_CERTIFICATE` in the deployment target.
- Keep `NEXT_AGORA_APP_CERTIFICATE` server-side only.

## Routing / Ownership

- UI and RTC/RTM client lifecycle live in `components`.
- Browser-facing API routes live in `app/api`.
- Shared constants and transcript normalization live in `lib`.
- If a workflow, request contract, or ownership boundary changes, update `README.md`, `AGENTS.md`, and the relevant `docs/ai/` files in the same change.

## Key Files

- `app/api/generate-agora-token/route.ts`: issues RTC + RTM tokens for the browser user.
- `app/api/invite-agent/route.ts`: starts the managed agent session; edit here for system prompt, VAD, model, or voice changes.
- `app/api/stop-conversation/route.ts`: stops the agent session.
- `app/api/chat/completions/route.ts`: optional OpenAI-compatible SSE proxy for a custom LLM (not wired by default).
- `components/LandingPage.tsx`: session bootstrap, RTM setup, provider wiring, and conversation lifecycle.
- `components/ConversationComponent.tsx`: RTC join, mic publication, `AgoraVoiceAI` init, transcript state, and renewals.
- `components/QuickstartConversationLayout.tsx`: in-call header, transcript rail, and controls dock.
- `components/QuickstartPipelineMetrics.tsx`: per-stage latency chips from `AGENT_METRICS`.
- `components/QuickstartTranscriptPanel.tsx`: live transcript rail.
- `lib/chat-completions.ts`: server-side custom LLM SSE handler factory; the route only exports `POST`.
- `lib/agora.ts`: shared agent UID defaults.
- `lib/conversation.ts`: transcript normalization and visualizer state mapping.
- `env.local.example`: local environment template.
- `scripts/verify-api-contracts.ts`: route contract verification.

## Patterns

### StrictMode Guard (`isReady`)

Both `useJoin` and `useLocalMicrophoneTrack` are gated by `isReady` to prevent double initialization in React StrictMode dev mode. The cleanup fires synchronously before any `setTimeout`, so only the real second mount's timer fires.

```tsx
const [isReady, setIsReady] = useState(false);
useEffect(() => {
  let cancelled = false;
  const id = setTimeout(() => {
    if (!cancelled) setIsReady(true);
  }, 0);
  return () => {
    cancelled = true;
    clearTimeout(id);
    setIsReady(false);
  };
}, []);
const { isConnected: joinSuccess } = useJoin(config, isReady);
const { localMicrophoneTrack } = useLocalMicrophoneTrack(isReady);
```

### Hook Ownership

- `useJoin` owns `client.leave()`; never call it manually.
- `useLocalMicrophoneTrack` owns track lifecycle; do not manually call `.close()`.
- `usePublish` owns publish state; mute with `track.setEnabled()` and do not manually unpublish.

### AgoraVoiceAI Init

Initialize `AgoraVoiceAI` from `agora-agent-client-toolkit` inside `ConversationComponent`, gated on `isReady && joinSuccess`.

```tsx
useEffect(() => {
  if (!isReady || !joinSuccess) return;
  // AgoraVoiceAI.init() is called here exactly once.
}, [isReady, joinSuccess]);
```

`isReady` becomes true only after the StrictMode fake-unmount cycle completes. Once `isReady` is true, React does not double invoke the effect for later dependency changes such as `joinSuccess` becoming true.

### Transcript and UI Mapping

- Manage `transcript` and `agentState` through `useState` plus `ai.on(TRANSCRIPT_UPDATED, ...)` and `ai.on(AGENT_STATE_CHANGED, ...)`.
- The toolkit uses `uid="0"` as a sentinel for the local user's speech. Remap that value to `client.uid` before passing messages into `QuickstartTranscriptPanel`, or user speech renders on the agent side.
- Include `INTERRUPTED` turns in `messageList`; filter only `IN_PROGRESS`. If the agent's first turn is interrupted and omitted, `messageList` stays empty and the transcript panel never shows that first turn.

### Tokens and Styling

- RTM token access must come from `RtcTokenBuilder.buildTokenWithRtm`; a standard RTC-only token does not grant RTM access.
- Tailwind must scan uikit classes with `./node_modules/agora-agent-uikit/dist/**/*.{js,mjs}` in `tailwind.config.ts`.

## Working Rules

- Prefer the smallest change that keeps the quickstart copyable and production-style.
- Keep RTC client creation StrictMode-safe with `useRef`, not `useMemo`.
- Keep token generation on `RtcTokenBuilder.buildTokenWithRtm`.
- Keep transcript UID remapping aligned with the toolkit sentinel behavior.
- Do not require third-party vendor API keys unless the code actually introduces a BYOK provider path.
- Keep README, AGENTS, and `docs/ai/` aligned with implementation changes.

## Commands

From the repo root:

```bash
pnpm install
pnpm run doctor
pnpm run dev
pnpm run verify
```

Useful narrower checks:

```bash
pnpm run lint
pnpm run typecheck
pnpm run verify:api
pnpm run build
```

## Verification Safety

- Safe without live Agora credentials:
  - `pnpm run lint`
  - `pnpm run typecheck`
  - `pnpm run verify:api`
  - `pnpm run build`
- Requires local env setup but not a live Agora session:
  - `pnpm run doctor`
  - `pnpm run verify`
- Often blocked inside restricted sandboxes because of port binding or process spawning:
  - `pnpm run dev`

## Anti-Patterns / What NOT To Do

- Do not call `client.leave()` manually; it breaks `useJoin` cleanup.
- Do not call `localMicrophoneTrack.close()` manually; it breaks hook ownership.
- Do not remove the `isReady` guard.
- Do not set `reactStrictMode: false` as a workaround.
- Do not use the deprecated `turnDetection.type: 'agora_vad'` flat API; use `turnDetection.config.start_of_speech` and `turnDetection.config.end_of_speech`.
- Do not replace `RtcTokenBuilder.buildTokenWithRtm` with an RTC-only token builder.
- Do not hide SDK requirements only in `CLAUDE.md`; all agent-facing guidance belongs in `AGENTS.md`.

## Done Criteria

Before finishing a change:

1. Run the narrowest relevant verification command.
2. For shipped app/runtime changes, ensure `pnpm run verify` passes.
3. If you changed files in `components/` or `app/api/`, verify that `README.md`, this file, and the relevant `docs/ai/` files still match the implementation.
4. Update root README and affected docs when workflow, request contracts, architecture, or environment guidance changes.
5. If the change touches workflows, interfaces, gotchas, or security details, update the matching file under [docs/ai/L1/](docs/ai/L1/) and bump `Last Reviewed` in [docs/ai/L0_repo_card.md](docs/ai/L0_repo_card.md).

## Git Conventions

### Commit messages — conventional commits

- **Format:** `type: description` or `type(scope): description`
- **Types:** `feat:` (new feature), `fix:` (bug fix), `chore:` (maintenance, version bumps), `test:` (test additions/changes), `docs:` (documentation)
- **Scoped variant:** `feat(scope):`, `fix(scope):` — e.g. `feat(api): add stop-conversation status flag`
- **Lowercase after prefix** — `feat: add feature`, not `feat: Add feature`
- **Present tense** — "add feature", not "added feature"
- **PR number appended** — `feat: add feature (#123)`

### Branch names

- **Format:** `type/short-description` — lowercase, hyphen-separated
- **Types match commit types:** `feat/`, `fix/`, `chore/`, `test/`, `docs/`
- **Examples:** `feat/agent-metrics`, `fix/transcript-uid`, `docs/progressive-disclosure`

### General rules

- **No AI tool names** — never mention claude, cursor, copilot, cody, aider, gemini, codex, chatgpt, or gpt-3/4 in commit messages or PR descriptions.
- **No Co-Authored-By trailers** — omit AI attribution lines.
- **No `--no-verify`** — let git hooks run normally.
- **No git config changes** — do not modify `user.name` or `user.email`.

## Doc Commands

| Command         | When to use                                                  |
| --------------- | ------------------------------------------------------------ |
| generate docs   | No `docs/ai/` directory exists yet                           |
| update docs     | Code changed since the `Last Reviewed` date in L0            |
| test docs       | Verify docs give agents the right context (writes `docs/ai/test-results.md`) |
| fix docs        | Close findings from a docs review or test run                |

The generator and tester live in the [AgoraIO-Community/ai-devkit](https://github.com/AgoraIO-Community/ai-devkit) skill set. See the [progressive disclosure standard](https://github.com/AgoraIO-Community/ai-devkit/blob/main/docs/progressive-disclosure-standard.md) for the full specification.

## Unmute local POC

This checkout is a local Portuguese voice conversation POC. The invite route uses pt-BR STT, Portuguese instructions/greeting, and the original managed LLM/TTS. Tool invocation is disabled unless voice annotation, document retrieval or plant MCPs are configured. Fill the two Agora variables in `.env.local` before starting a real conversation; no provider keys are required. Main pre-call/transcript/end controls are localized. API contracts and RTC/RTM lifecycle are unchanged.

### LTQ demonstration screen

The root page renders `LtqWorkspace`: `VisualWorkbench` defaults to a person-detection test and offers the locally served Tripo showcase MP4 in the LTQ tab, beside the independent Agora voice experience. `/voice` renders the original `LandingPage` and is embedded with `allow="microphone; camera; autoplay"`. Do not point the voice iframe at `/`, which would recursively embed the workspace. The MP4 is a conceptual visual demonstration, not an interactive or engineering-validated CAD asset. The LTQ preview is independent of the voice and annotation controls. The Tripo GLB export is subscription-gated; do not extract it through internal viewer resources.

### Local person-detection test

`PersonDetectionTest` owns a video-only camera stream, lazy detector, sequential inference, and an SVG overlay. Its tracks are independent of Agora: stop these owned camera tracks on stop, tab switch, errors, or unmount; never apply this cleanup to hook-owned Agora tracks. Release the current video track before requesting a different facing mode. Generation guards reject stale camera/load/inference results. Wait for in-flight inference before disposing the detector. Keep model imports behind the user action so voice startup does not load TensorFlow.

`lib/visual-detection.ts` exposes `VisualDetector`: labels/scores plus normalized 0–1 bounding boxes. The current adapter filters COCO-SSD to `person`, with local weights in `public/vision-demo/coco-ssd/`, WebGL and CPU fallback. Preserve coordinate alignment between contained video/canvas and SVG when changing layout or detectors. The example image and weights are attributed under `public/vision-demo/`. `PersonDetectionTest` does not forward its frames or detections. `AgoraCameraShare` owns a separate video track and publishes it only after explicit user action. It signals the same-origin workspace to release the local test camera before opening the RTC track. Keep publish/unpublish limited to that video track and close it on stop, failure or unmount. The invite route configures the managed LLM for text and image input. This does not recognize identities or diagnose industrial equipment.

### Mobile tunnel demo

Build with `pnpm run build`, serve with `pnpm start --hostname 127.0.0.1 --port 3002`, then run `ngrok http 3002`. Use the emitted HTTPS URL on the phone, accept the ngrok informational page, and grant camera/microphone only through their separate controls. Keep both processes running; rebuild/restart after code changes. Local development remains on its original port (3001 in this session). This path avoids tunneling the dev runtime, which may block resources for an unconfigured origin. Tunnel URLs are temporary; do not hardcode one into the app.

### Voice-driven annotation

`OPENAI_API_KEY` and the fixed HTTPS `AGORA_ANNOTATION_ORIGIN` enable the Agora REST tools `circular_objeto` and `observar_camera`. `/api/vision-annotation` hands jobs to the browser with separate per-session capabilities, validates a single bounded JPEG, calls OpenAI server-side, and returns normalized coordinates or a short scene description. Keep the key private, preserve session and rate limits, and render the circle on the exact submitted frame. The in-memory job bridge requires one Next.js process.

### Document retrieval

The voice assistant helps equipment operators troubleshoot by voice. Request the camera only for an unresolved visual detail or an explicit visual request. Ground technical guidance in applicable document excerpts and disclose missing evidence.

`RAG_DOCUMENT_PATH`, `OPENAI_API_KEY`, and the Agora webhook origin enable the `ManualManutencaoLTQ` MCP server and its tools `consultar_manual_de_manutencao` and `consultar_resultado`. Keep source files outside `public/` and out of Git. The server builds a BM25 index and caches OpenAI embeddings locally under `.rag/vectors/`, keyed by the chunk fingerprint and embedding settings. Hybrid retrieval uses the original query for embeddings, translated terms for BM25 when supplied, and retains citations from Markdown headings or form-feed pages. For a foreign-language source, `RAG_DOCUMENT_LANGUAGE` instructs Agora to send translated search terms alongside the original question. The MCP endpoint uses a per-session capability and queues the work without awaiting OpenAI. Initial indexing sends source chunks to the embeddings endpoint. The answer generator receives only retrieved excerpts and the question. Send each terminal research result to its originating Agora model via session.think. Reserve browser TTS for explicit replay. A separate browser capability scopes result polling to the conversation. Process-local jobs require one long-running Next.js process. The retrieval tool and camera annotation can run in the same session. The voice prompt should route normal reports of relevant maintenance symptoms to research without requiring a reference to the manual or MCP. Keep the transcript fallback limited to completed local-user turns in scope, and avoid creating a second job when the primary MCP call already queued one.

### Local tracing

`ops/langfuse/compose.yml` runs a private loopback-only Langfuse instance. `lib/call-observability.ts` exports OTLP traces from the Next.js server. Keep Langfuse secrets server-side. Populate Langfuse Input and Output with whitelisted diagnostic fields. Do not log transcript text, document excerpts, or camera frames. The session-bound browser telemetry endpoint accepts only whitelisted state transitions and counts. Keep telemetry failures outside call and tool control flow.

### Retry e fallback Feita

Configure `FEITA_API_KEY` no servidor para ativar a Feita como fallback do manual e da análise de câmera. O adaptador em `lib/ai-provider.ts` faz até duas novas tentativas por provedor em falhas transitórias, com backoff exponencial (200 ms, 400 ms) e jitter de até 149 ms, respeitando Retry-After e o prazo total. Se a OpenAI falhar, a Feita recebe a pergunta e os trechos recuperados ou o quadro solicitado. O modelo padrão é `qwen/qwen4-max`, configurável por `FEITA_MODEL`. Para embeddings, o fallback continua sendo a busca por BM25. A voz usa o Agora.

### Simulated plant MCPs

Keep TelemetriaCLPLTQ and DocumentacaoPlantaLTQ separate from SKF research. The Python services share the simulator catalog and require PLANTA_MCP_TOKEN. Next.js forwards both fixed endpoints on the existing tunnel. Only expose tools registered for the corresponding server.
