'use client';

import { useEffect, useRef } from 'react';

type Input = {
  token?: string;
  connected: boolean;
  micReady: boolean;
  micEnabled: boolean;
  micUnavailable: boolean;
  publishFailed: boolean;
  utterance?: { turn: number; characters: number; eligible: boolean };
  partial?: { turn: number; characters: number };
};

export function reportCallTelemetry(token: string, event: Record<string, string | number | boolean>) {
  void fetch('/api/call-telemetry', {
    method: 'POST',
    headers: { 'X-Research-Token': token, 'Content-Type': 'application/json' },
    body: JSON.stringify(event),
    keepalive: true,
  }).catch(() => undefined);
}

export function useCallTelemetry({ token, connected, micReady, micEnabled, micUnavailable, publishFailed, utterance, partial }: Input) {
  const latest = useRef<string | undefined>(undefined);
  const latestPartial = useRef<string | undefined>(undefined);
  const turn = utterance?.turn;
  const characters = utterance?.characters;
  const eligible = utterance?.eligible;
  const partialTurn = partial?.turn;
  const partialCharacters = partial?.characters;

  useEffect(() => {
    if (!token) return;
    reportCallTelemetry(token, { event: 'microphone', connected, ready: micReady, enabled: micEnabled, unavailable: micUnavailable, publishFailed });
  }, [token, connected, micReady, micEnabled, micUnavailable, publishFailed]);

  useEffect(() => {
    if (!token || turn === undefined || characters === undefined || eligible === undefined) return;
    const signature = `${token}:${turn}`;
    if (latest.current === signature) return;
    latest.current = signature;
    reportCallTelemetry(token, { event: 'transcript', turn, characters, eligible, final: true });
  }, [token, turn, characters, eligible]);

  useEffect(() => {
    if (!token || partialTurn === undefined || !partialCharacters) return;
    const signature = `${token}:${partialTurn}`;
    if (latestPartial.current === signature) return;
    latestPartial.current = signature;
    reportCallTelemetry(token, { event: 'transcript', turn: partialTurn, characters: partialCharacters, eligible: false, final: false });
  }, [token, partialTurn, partialCharacters]);
}
