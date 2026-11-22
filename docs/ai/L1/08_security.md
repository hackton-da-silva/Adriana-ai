# 08 Security

> Security model, trust boundaries, secret handling, and safety controls for this quickstart.

## Trust Boundaries

- Browser is untrusted and never receives `NEXT_AGORA_APP_CERTIFICATE`.
- Next.js server routes hold credentials and mint scoped, expiring tokens.
- Agora cloud executes managed agent pipeline using server-issued credentials.

## Secret Handling Rules

- Keep `NEXT_AGORA_APP_CERTIFICATE` server-side only.
- Do not expose BYOK provider API keys to client bundles.
- Store secrets in `.env.local` for dev and deployment secret store in Vercel.
- `env.local.example` documents expected keys without real values.

## Token Security Model

- Tokens expire (default 1 hour).
- Token endpoint allows caller-provided UID/channel but still uses server secret signing.
- Renewal flow requests new RTC/RTM tokens near expiry.
- RTM capability is required and intentionally embedded by `buildTokenWithRtm`.

## Input Validation and Failure Handling

- Route handlers validate required fields and env availability.
- Errors return structured JSON with bounded detail.
- Stop route treats already-stopping/not-found agent as idempotent success.

## Agent Behavior Safety

- Prompt includes explicit honesty and non-hallucination policy for product claims.
- Agent failure message is constrained (`Please wait a moment.`) for degraded-path behavior.

## Operational Security Practices

- Run `pnpm run verify` before release changes.
- Avoid logging secrets; current logs are operational and should remain non-secret.
- Use least-privilege project bindings when managing Agora environments.

## Known Limits

- This quickstart is a sample app; it does not implement user auth/tenant isolation.
- If productionizing, add authenticated route access and per-user authorization checks.

## Security Review Checklist

1. Confirm `NEXT_AGORA_APP_CERTIFICATE` is never referenced in client files.
2. Confirm token minting still uses server route only.
3. Confirm route error payloads do not leak secrets.
4. Confirm BYOK keys are optional and remain server-side.
5. Confirm docs do not instruct users to expose secrets in public config.

## Threat Notes for This Sample

- Token misuse risk is bounded by token expiry but still requires secure key custody.
- Public start/stop endpoints are unauthenticated in sample form; production needs auth.
- RTM message payloads are parsed defensively but should be treated as untrusted input.

## Hardening Steps for Productionization

- Add authenticated identity and authorization to all mutation routes.
- Scope agent start permissions per user/session ownership.
- Add rate limiting for token and invite endpoints.
- Add request tracing IDs for security incident investigation.
- Add environment-specific secret rotation policy and monitoring.

## Deployment Secret Checklist (Vercel)

- `NEXT_PUBLIC_AGORA_APP_ID` set for all required environments.
- `NEXT_AGORA_APP_CERTIFICATE` set as server-side secret only.
- Optional BYOK keys set only when related provider block is enabled.
- Preview environments use non-production credentials.

## Security-Relevant Files

- `app/api/generate-agora-token/route.ts`
- `app/api/invite-agent/route.ts`
- `app/api/stop-conversation/route.ts`
- `env.local.example`
- `README.md` environment section

## Audit Trigger Events

Re-audit security docs when any of these change:

- token issuance logic
- agent start/stop route authorization assumptions
- environment variable set or naming
- provider integration path (default vs BYOK)

## Related Deep Dives

- [conversation_lifecycle.md](L2/conversation_lifecycle.md) — Token issuance and renewal sequence details.
- [transcript_pipeline.md](L2/transcript_pipeline.md) — RTM event surfaces and error propagation boundaries.

## Local Camera Test

Camera access begins only through the user's button and browser permission. The visual test requests video without audio, processes frames locally, and does not upload, persist, or forward frames/detections to Agora. Model weights and the public example photo are same-origin static assets. Stop, tab switch, error, and unmount release its owned camera tracks. This test localizes people and does not identify individuals. The voice iframe opens its own video track only after the user clicks **Compartilhar câmera**. That track is sent to Agora RTC and frames can reach the managed LLM. Ending sharing releases the track. Local detector annotations are never included.

The annotation tool uses separate random, expiring capabilities for the Agora callback and the browser. It limits calls per session and per process and forwards one bounded JPEG per explicit command. The app does not store captured frames server-side. Store the OpenAI key only on the server.

Document source stays outside the public folder. Initial indexing sends document chunks to the OpenAI embeddings API. Subsequent requests send the query for a vector and only retrieved excerpts for synthesis. Local vector cache files belong outside `public/` and Git. The Agora session receives the result and citations. Callback and browser access use separate expiring, per-call capabilities. The browser sends only eligible completed maintenance utterances and a brief related topic to the fallback route. Use public or approved demo material while the ngrok voice endpoint is accessible without user authentication.

Langfuse is bound to loopback. Its private credentials stay in ignored env files and trace export runs server-side. Trace Input and Output record whitelisted control flow and counts without the spoken text, document excerpts, media, or MCP/Agora credentials.

## Private postmortem evidence

Unlike diagnostic-only Langfuse traces, the separate local postmortem journal deliberately stores spoken text and bounded tool results and sends them to the configured chat provider for analysis. Use per-call random browser and tool capabilities; keep request-size, session, event and retry limits. Status responses expose no conversation content. Files are mode 0600 in the ignored files/postmortems/ directory outside public/. Do not record frames, full documents, auth headers or credentials; known server keys and postmortem capabilities are redacted. Transcription/tool content is untrusted evidence, never generation instructions. Preserve the schema and evidence IDs; simulation results are not verified plant readings. File retention is manual; expiration removes in-memory access, not disk artifacts.
