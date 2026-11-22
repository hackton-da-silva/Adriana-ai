'use client';

import { useCallback, useEffect, useRef } from 'react';
import type { PostmortemTurn } from '@/types/postmortem';

type Diagnostic = { name: string; value: string | number | boolean };
type Input = { token?: string; turns: PostmortemTurn[]; diagnostics: Diagnostic[] };

export function usePostmortem({ token, turns, diagnostics }: Input) {
  const latest = useRef({ turns, diagnostics });
  const sent = useRef(new Map<string, string>());
  const sentDiagnostics = useRef(new Map<string, Diagnostic['value']>());
  const inFlight = useRef<Promise<boolean> | null>(null);
  const ending = useRef(false);
  useEffect(() => { latest.current = { turns, diagnostics }; }, [turns, diagnostics]);

  const flush = useCallback(async (): Promise<boolean> => {
    if (!token) return true;
    if (inFlight.current) await inFlight.current;
    const work = async () => {
      const pending = latest.current.turns.filter(turn => sent.current.get(`${turn.speaker}:${turn.turn}`) !== JSON.stringify(turn));
      const changed = latest.current.diagnostics.filter(item => sentDiagnostics.current.get(item.name) !== item.value).slice(-20);
      // Small batches stay below the browser's 64 KiB keepalive budget even with Unicode.
      do {
        const batch = pending.splice(0, 2);
        const diagnosticBatch = changed.splice(0, 10);
        try {
          const response = await fetch('/api/postmortems', {
            method: 'PUT', headers: { 'Content-Type': 'application/json', 'X-Postmortem-Token': token },
            body: JSON.stringify({ turns: batch, diagnostics: diagnosticBatch }), signal: AbortSignal.timeout(3000),
          });
          if (!response.ok) return false;
          for (const turn of batch) sent.current.set(`${turn.speaker}:${turn.turn}`, JSON.stringify(turn));
          for (const item of diagnosticBatch) sentDiagnostics.current.set(item.name, item.value);
        } catch { return false; }
      } while (pending.length || changed.length);
      return true;
    };
    const promise = work();
    inFlight.current = promise;
    try { return await promise; } finally { if (inFlight.current === promise) inFlight.current = null; }
  }, [token]);

  useEffect(() => {
    if (!token) return;
    let ticks = 0;
    const interval = setInterval(() => {
      if (ending.current || inFlight.current) return;
      // Flush changed evidence every second; an empty heartbeat every 15 seconds.
      ticks++;
      const changed = latest.current.turns.some(turn => sent.current.get(`${turn.speaker}:${turn.turn}`) !== JSON.stringify(turn))
        || latest.current.diagnostics.some(item => sentDiagnostics.current.get(item.name) !== item.value);
      if (changed || ticks % 15 === 0) void flush();
    }, 1000);
    const pagehide = () => {
      if (ending.current) return;
      ending.current = true;
      const pending = latest.current.turns.filter(turn => sent.current.get(`${turn.speaker}:${turn.turn}`) !== JSON.stringify(turn));
      void fetch('/api/postmortems', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Postmortem-Token': token }, keepalive: true,
        body: JSON.stringify({ action: 'finish', reason: 'page_closed', batch: {
          turns: pending.slice(-2), diagnostics: [{ name: 'capture_incomplete', value: pending.length > 2 || Boolean(inFlight.current) }],
        } }),
      }).catch(() => undefined);
    };
    window.addEventListener('pagehide', pagehide);
    return () => { clearInterval(interval); window.removeEventListener('pagehide', pagehide); };
  }, [token, flush]);

  return useCallback(async () => {
    if (ending.current) return false;
    ending.current = true;
    const collected = await flush();
    if (!collected && token) {
      try {
        await fetch('/api/postmortems', {
          method: 'PUT', headers: { 'Content-Type': 'application/json', 'X-Postmortem-Token': token },
          body: JSON.stringify({ diagnostics: [{ name: 'capture_incomplete', value: true }] }),
          signal: AbortSignal.timeout(1000),
        });
      } catch {}
    }
    return true;
  }, [flush, token]);
}
