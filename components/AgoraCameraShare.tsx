'use client';

import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import AgoraRTC, { useRTCClient, type ICameraVideoTrack } from 'agora-rtc-react';
import { AGORA_CAMERA_REQUEST } from '@/lib/camera-events';
import { Button } from './ui/button';
import { useVisionAnnotation } from './useVisionAnnotation';
import { reportCallTelemetry } from './useCallTelemetry';

type Facing = 'user' | 'environment';

function getCameraError(cause: unknown) {
  const code = typeof cause === 'object' && cause && 'code' in cause ? cause.code : undefined;
  const name = cause instanceof Error ? cause.name : undefined;
  if (code === 'PERMISSION_DENIED' || name === 'NotAllowedError') {
    return 'O navegador bloqueou a câmera. Permita o acesso nas configurações do site ou abra a conversa em tela cheia.';
  }
  if (code === 'DEVICE_NOT_FOUND' || name === 'NotFoundError' || name === 'OverconstrainedError') {
    return 'Essa câmera não está disponível. Escolha a outra lente e tente novamente.';
  }
  if (code === 'NOT_READABLE' || name === 'NotReadableError') {
    return 'A câmera está ocupada ou indisponível. Feche outros apps que usam a câmera e tente novamente.';
  }
  return typeof code === 'string' && /^[A-Z_]+$/.test(code)
    ? `Não foi possível abrir a câmera (${code}).`
    : 'Não foi possível abrir a câmera. Confira a permissão do navegador e tente novamente.';
}

export function AgoraCameraShare({ connected, annotationToken, researchToken }: {
  connected: boolean;
  annotationToken?: string;
  researchToken?: string;
}) {
  const client = useRTCClient();
  const preview = useRef<HTMLDivElement>(null);
  const camera = useRef<ICameraVideoTrack | null>(null);
  const mounted = useRef(false);
  const [facing, setFacing] = useState<Facing>('environment');
  const [sharing, setSharing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const { annotation, status, clearAnnotation } = useVisionAnnotation(annotationToken, preview);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      const track = camera.current;
      camera.current = null;
      track?.stop();
      track?.close();
    };
  }, []);

  async function startSharing() {
    setBusy(true);
    setError('');
    if (researchToken) reportCallTelemetry(researchToken, { event: 'camera', state: 'starting' });
    let track: ICameraVideoTrack | undefined;
    let publishing = false;
    try {
      // The workspace and its voice frame share an origin. Release the local
      // detector's camera before opening the Agora camera on mobile.
      try {
        window.parent.dispatchEvent(new Event(AGORA_CAMERA_REQUEST));
      } catch {
        // The standalone voice route also works inside a third-party frame.
      }
      track = await AgoraRTC.createCameraVideoTrack({ facingMode: facing, encoderConfig: '480p_1' });
      if (!mounted.current) {
        track.close();
        return;
      }
      camera.current = track;
      publishing = true;
      await client.publish(track);
      if (!mounted.current) return;
      const actualFacing = track.getMediaStreamTrack().getSettings().facingMode;
      if (actualFacing === 'environment' || actualFacing === 'user') setFacing(actualFacing);
      setSharing(true);
      if (researchToken) reportCallTelemetry(researchToken, { event: 'camera', state: 'published' });
    } catch (cause) {
      track?.close();
      camera.current = null;
      if (mounted.current) {
        if (researchToken) reportCallTelemetry(researchToken, { event: 'camera', state: publishing ? 'publish_failed' : 'capture_failed' });
        console.warn('Agora camera could not be shared:', cause);
        setError(publishing
          ? 'A câmera abriu, mas o Agora não conseguiu enviar o vídeo. Confira a conexão e tente novamente.'
          : getCameraError(cause));
      }
    } finally {
      if (mounted.current) setBusy(false);
    }
  }

  async function stopSharing() {
    const track = camera.current;
    if (!track) return;
    setBusy(true);
    setError('');
    clearAnnotation();
    track.stop();
    try {
      await client.unpublish(track);
    } catch (cause) {
      console.warn('Agora camera could not be unpublished:', cause);
    } finally {
      track.close();
      if (camera.current === track) camera.current = null;
      if (mounted.current) {
        setSharing(false);
        setBusy(false);
        if (researchToken) reportCallTelemetry(researchToken, { event: 'camera', state: 'stopped' });
      }
    }
  }

  useEffect(() => {
    const track = camera.current;
    if (sharing && track && preview.current) track.play(preview.current, { fit: 'contain', mirror: false });
  }, [sharing]);

  useEffect(() => {
    const track = camera.current;
    if (!sharing || !track) return;
    const handleEnded = () => {
      if (camera.current !== track) return;
      camera.current = null;
      track.stop();
      track.close();
      setSharing(false);
      setError('O navegador encerrou o acesso à câmera.');
      if (researchToken) reportCallTelemetry(researchToken, { event: 'camera', state: 'ended' });
    };
    track.on('track-ended', handleEnded);
    return () => track.off('track-ended', handleEnded);
  }, [sharing, researchToken]);

  useEffect(() => {
    if (!researchToken || !sharing || busy || !connected) return;
    const track = camera.current;
    if (!track) return;
    const timer = setTimeout(() => {
      const stats = track.getStats();
      const sending = (stats.sendFrameRate ?? 0) > 0 || stats.sendBitrate > 0;
      reportCallTelemetry(researchToken, { event: 'camera', state: sending ? 'sending_frames' : 'no_frames' });
    }, 3500);
    return () => clearTimeout(timer);
  }, [sharing, facing, connected, busy, researchToken]);

  async function switchCamera() {
    const next = facing === 'environment' ? 'user' : 'environment';
    const track = camera.current;
    setError('');
    if (!track) {
      setFacing(next);
      return;
    }
    setBusy(true);
    try {
      await track.setDevice({ facingMode: next });
      if (mounted.current && camera.current === track) setFacing(next);
    } catch {
      if (mounted.current) setError('Não foi possível trocar de câmera neste dispositivo.');
    } finally {
      if (mounted.current) setBusy(false);
    }
  }

  return (
    <div className="mx-auto mt-2 flex max-w-sm flex-col items-center gap-1.5 text-center text-xs">
      {sharing && <div ref={preview} className="h-20 w-28 overflow-hidden rounded-md bg-black" aria-label="Prévia do vídeo enviado ao Agora" />}
      {sharing && annotation && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/85 p-4">
          <section aria-label={`Quadro marcado: ${annotation.target}`} className="flex max-h-full w-full max-w-xl flex-col items-center gap-2 rounded-lg bg-card p-3">
            <div className="relative" style={{ width: `min(100%, ${annotation.width / annotation.height * 46}dvh)` }}>
              <Image unoptimized src={annotation.image} width={annotation.width} height={annotation.height}
                className="h-auto w-full rounded" alt={`Quadro congelado com marcação de ${annotation.target}`} />
              <svg aria-hidden="true" className="pointer-events-none absolute inset-0 h-full w-full"
                viewBox={`0 0 ${annotation.width} ${annotation.height}`}>
                <ellipse
                  cx={(annotation.box.x + annotation.box.width / 2) * annotation.width}
                  cy={(annotation.box.y + annotation.box.height / 2) * annotation.height}
                  rx={annotation.box.width * annotation.width / 2}
                  ry={annotation.box.height * annotation.height / 2}
                  fill="none" stroke="#4dffae" strokeWidth="3" vectorEffect="non-scaling-stroke"
                />
              </svg>
            </div>
            <p>{annotation.target}</p>
            <Button type="button" size="sm" onClick={clearAnnotation}>Voltar ao vídeo</Button>
          </section>
        </div>
      )}
      <div className="flex flex-wrap justify-center gap-2">
        <Button type="button" size="sm" variant="outline" disabled={busy || (!connected && !sharing)}
          onClick={() => { void (sharing ? stopSharing() : startSharing()); }}>
          {busy ? 'Aguarde…' : sharing ? 'Parar vídeo' : 'Compartilhar câmera'}
        </Button>
        <Button type="button" size="sm" variant="ghost" disabled={busy} onClick={() => { void switchCamera(); }}>
          Usar {facing === 'environment' ? 'frontal' : 'traseira'}
        </Button>
      </div>
      <p role="status" className="text-muted-foreground">
        {sharing ? 'Vídeo enviado ao Agora' : 'Câmera desligada'} · {facing === 'environment' ? 'Traseira' : 'Frontal'}
      </p>
      {sharing && annotationToken && <p className="text-muted-foreground">Diga “circule a garrafa” para marcar um objeto.</p>}
      {status && <p role="status">{status}</p>}
      {error && (
        <div role="alert" className="text-destructive">
          <p>{error}</p>
          {error.includes('tela cheia') && (
            <a href="/voice" target="_blank" rel="noreferrer" className="underline">Abrir conversa em tela cheia</a>
          )}
        </div>
      )}
    </div>
  );
}
