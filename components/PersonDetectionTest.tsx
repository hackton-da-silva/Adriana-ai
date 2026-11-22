'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { Camera, CameraOff, Circle, ImageIcon, Loader2, ScanLine, Square, SwitchCamera, Users } from 'lucide-react';
import type { VisualDetection, VisualDetector, VisualSource } from '@/lib/visual-detection';
import { AGORA_CAMERA_REQUEST } from '@/lib/camera-events';
import styles from './PersonDetectionTest.module.css';

type Phase = 'idle' | 'loading' | 'camera' | 'example' | 'error';
type CameraFacing = 'user' | 'environment';

const cameraNames: Record<CameraFacing, string> = {
  user: 'frontal',
  environment: 'traseira',
};

function cameraErrorMessage(error: unknown, facing?: CameraFacing) {
  if (error instanceof DOMException) {
    if (error.name === 'OverconstrainedError' && facing) {
      return `A câmera ${cameraNames[facing]} não está disponível. Tente a outra câmera ou use a imagem de exemplo.`;
    }
    if (error.name === 'NotAllowedError') return 'O acesso à câmera foi negado. Permita a câmera no navegador ou use a imagem de exemplo.';
    if (error.name === 'NotFoundError') return 'Não encontramos uma câmera. Você pode testar com a imagem de exemplo.';
    if (error.name === 'NotReadableError') return 'A câmera está indisponível ou em uso por outro aplicativo. Feche-o e tente novamente.';
  }
  return 'Não foi possível iniciar a detecção. Confira a conexão para baixar o detector e tente novamente.';
}

export function PersonDetectionTest() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const modelRef = useRef<Promise<VisualDetector> | null>(null);
  const inferenceRef = useRef<Promise<VisualDetection[]> | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const runRef = useRef(0);
  const [phase, setPhase] = useState<Phase>('idle');
  const [source, setSource] = useState<'camera' | 'example'>('camera');
  const [error, setError] = useState('');
  const [detections, setDetections] = useState<VisualDetection[]>([]);
  const [dimensions, setDimensions] = useState({ width: 1280, height: 720 });
  const [threshold, setThreshold] = useState(55);
  const [shape, setShape] = useState<'box' | 'circle'>('box');
  const [facing, setFacing] = useState<CameraFacing>();
  const otherFacing = facing === 'environment' ? 'user' : 'environment';

  const releaseMedia = useCallback(() => {
    runRef.current += 1;
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
    }
  }, []);

  useEffect(() => () => {
    releaseMedia();
    const model = modelRef.current;
    if (model) {
      // An in-flight inference must finish before its tensors are disposed.
      void Promise.allSettled([model, inferenceRef.current]).then(([result]) => {
        if (result.status === 'fulfilled') result.value.dispose();
      });
    }
  }, [releaseMedia]);

  async function getDetector() {
    if (!modelRef.current) {
      modelRef.current = import('@/lib/visual-detection')
        .then(({ loadPersonDetector }) => loadPersonDetector())
        .catch((loadError) => {
          modelRef.current = null;
          throw loadError;
        });
    }
    return modelRef.current;
  }

  const stop = useCallback(() => {
    releaseMedia();
    setDetections([]);
    setPhase('idle');
    setError('');
  }, [releaseMedia]);

  useEffect(() => {
    if (source !== 'camera' || (phase !== 'camera' && phase !== 'loading')) return;
    window.addEventListener(AGORA_CAMERA_REQUEST, stop);
    return () => window.removeEventListener(AGORA_CAMERA_REQUEST, stop);
  }, [phase, source, stop]);

  async function infer(detector: VisualDetector, input: VisualSource, run: number, repeat: boolean) {
    if (run !== runRef.current) return;
    if ('readyState' in input && input.readyState < 2) {
      timerRef.current = setTimeout(() => { void infer(detector, input, run, repeat); }, 150);
      return;
    }
    try {
      // Switching sources must not overlap inference on the same model/backend.
      await inferenceRef.current?.catch(() => undefined);
      if (run !== runRef.current) return;
      const pending = detector.detect(input);
      inferenceRef.current = pending;
      const found = await pending;
      if (run !== runRef.current) return;
      setDetections(found);
      if (repeat) timerRef.current = setTimeout(() => { void infer(detector, input, run, true); }, 200);
    } catch (detectError) {
      if (run !== runRef.current) return;
      releaseMedia();
      setDetections([]);
      setError(cameraErrorMessage(detectError));
      setPhase('error');
    }
  }

  async function start(nextSource: 'camera' | 'example', requestedFacing = facing) {
    releaseMedia();
    const run = runRef.current;
    setSource(nextSource);
    setPhase('loading');
    setError('');
    setDetections([]);
    try {
      const detector = await getDetector();
      if (run !== runRef.current) return;

      if (nextSource === 'example') {
        const image = new window.Image();
        image.src = '/vision-demo/people.jpg';
        await image.decode();
        if (run !== runRef.current) return;
        const canvas = canvasRef.current;
        if (!canvas) return;
        canvas.width = image.naturalWidth;
        canvas.height = image.naturalHeight;
        const context = canvas.getContext('2d');
        if (!context) throw new Error('Canvas unavailable');
        context.drawImage(image, 0, 0);
        setDimensions({ width: canvas.width, height: canvas.height });
        await infer(detector, canvas, run, false);
        if (run === runRef.current) setPhase('example');
        return;
      }

      if (!navigator.mediaDevices?.getUserMedia) throw new Error('Camera unavailable');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: requestedFacing ? { exact: requestedFacing } : { ideal: 'user' },
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });
      if (run !== runRef.current) {
        stream.getTracks().forEach((track) => track.stop());
        return;
      }
      streamRef.current = stream;
      const video = videoRef.current;
      if (!video) {
        releaseMedia();
        return;
      }
      video.srcObject = stream;
      await video.play();
      if (run !== runRef.current) return;
      setDimensions({ width: video.videoWidth, height: video.videoHeight });
      const track = stream.getVideoTracks()[0];
      const actualFacing = track?.getSettings().facingMode;
      if (actualFacing === 'user' || actualFacing === 'environment') setFacing(actualFacing);
      track?.addEventListener('ended', () => {
        if (run === runRef.current) stop();
      }, { once: true });
      setPhase('camera');
      void infer(detector, video, run, true);
    } catch (startError) {
      if (run !== runRef.current) return;
      releaseMedia();
      setError(cameraErrorMessage(startError, nextSource === 'camera' ? requestedFacing : undefined));
      setPhase('error');
    }
  }

  function switchCamera() {
    setFacing(otherFacing);
    if (phase === 'camera' || (phase === 'error' && source === 'camera')) {
      void start('camera', otherFacing);
    }
  }

  const visible = detections.filter((detection) => detection.score >= threshold / 100);
  const active = phase === 'camera' || phase === 'example';
  const labelSize = Math.max(16, dimensions.width * 0.025);

  return (
    <div className={styles.test}>
      <div className={styles.toolbar}>
        <div className={styles.sourceButtons}>
          <button type="button" className={styles.primary} onClick={() => { void start('camera'); }} disabled={phase === 'loading' || phase === 'camera'}>
            <Camera size={16} aria-hidden="true" />{phase === 'camera' ? 'Câmera ativa' : facing ? `Ativar câmera ${cameraNames[facing]}` : 'Ativar câmera'}
          </button>
          <button type="button" onClick={switchCamera} disabled={phase === 'loading'}>
            <SwitchCamera size={16} aria-hidden="true" />Usar {cameraNames[otherFacing]}
          </button>
          <button type="button" onClick={() => { void start('example'); }} disabled={phase === 'loading'}><ImageIcon size={16} aria-hidden="true" />Usar exemplo</button>
          {phase !== 'idle' && <button type="button" onClick={stop} aria-label="Parar detecção e desligar câmera"><CameraOff size={16} aria-hidden="true" />Parar</button>}
        </div>
        <div className={styles.shapes} aria-label="Formato da marcação">
          <button type="button" aria-pressed={shape === 'box'} onClick={() => setShape('box')} title="Marcar com caixas"><Square size={16} aria-hidden="true" /><span>Caixa</span></button>
          <button type="button" aria-pressed={shape === 'circle'} onClick={() => setShape('circle')} title="Marcar com círculos"><Circle size={16} aria-hidden="true" /><span>Círculo</span></button>
        </div>
      </div>

      <div className={styles.stage} aria-label="Visualização da detecção de pessoas">
        <video ref={videoRef} className={styles.media} hidden={!active || source !== 'camera'} autoPlay playsInline muted aria-label="Câmera para detectar pessoas"
          onResize={({ currentTarget }) => {
            if (streamRef.current && currentTarget.videoWidth && currentTarget.videoHeight) {
              setDimensions({ width: currentTarget.videoWidth, height: currentTarget.videoHeight });
            }
          }}
        />
        <canvas ref={canvasRef} className={styles.media} hidden={!active || source !== 'example'} aria-label="Imagem de exemplo para detecção de pessoas" />
        {active && <svg className={styles.overlay} viewBox={`0 0 ${dimensions.width} ${dimensions.height}`} preserveAspectRatio="xMidYMid meet" role="img" aria-label={`${visible.length} pessoas destacadas na imagem`}>
          {visible.map((detection, index) => {
            const x = detection.box.x * dimensions.width;
            const y = detection.box.y * dimensions.height;
            const width = detection.box.width * dimensions.width;
            const height = detection.box.height * dimensions.height;
            const labelY = Math.max(labelSize * 1.5, y);
            return <g key={index} className={styles.mark}>
              {shape === 'box' ? <rect x={x} y={y} width={width} height={height} rx={5} /> : <ellipse cx={x + width / 2} cy={y + height / 2} rx={width / 2} ry={height / 2} />}
              <rect className={styles.labelBackground} x={x} y={labelY - labelSize * 1.5} width={labelSize * 7.8} height={labelSize * 1.5} rx={4} />
              <text x={x + labelSize * 0.35} y={labelY - labelSize * 0.4} fontSize={labelSize}>{detection.label} · {Math.round(detection.score * 100)}%</text>
            </g>;
          })}
        </svg>}
        {!active && <div className={styles.empty}>
          {phase === 'loading' ? <Loader2 size={34} className={styles.spinner} aria-hidden="true" /> : <ScanLine size={42} aria-hidden="true" />}
          <h3>{phase === 'loading' ? 'Preparando a visão…' : 'Vamos testar a visão?'}</h3>
          <p>{phase === 'loading' ? 'O detector está sendo carregado no navegador. Na primeira vez, pode levar alguns segundos.' : 'Ative a câmera ou use a imagem de exemplo. As pessoas encontradas aparecem destacadas na tela.'}</p>
          <span>As imagens da câmera são processadas neste dispositivo.</span>
        </div>}
        {active && <div className={styles.liveBadge}><span className={styles.liveDot} />{source === 'example' ? 'Imagem de exemplo' : facing ? `Câmera ${cameraNames[facing]}` : 'Câmera ao vivo'}</div>}
      </div>

      <div className={styles.settings}>
        <span className={styles.count} role="status" aria-live="polite"><Users size={17} aria-hidden="true" />{active ? `${visible.length} ${visible.length === 1 ? 'pessoa detectada' : 'pessoas detectadas'}` : phase === 'loading' ? 'Carregando detector' : 'Detecção parada'}</span>
        <label className={styles.threshold}>Confiança mínima <input type="range" min="35" max="90" step="5" value={threshold} onChange={(event) => setThreshold(Number(event.target.value))} /><span>{threshold}%</span></label>
      </div>
      {error && <p className={styles.error} role="alert">{error}</p>}
      <p className={styles.note}>As marcações ficam no teste local. Para enviar vídeo à IA, use Compartilhar câmera na chamada.</p>
      {source === 'example' && active && <a className={styles.credit} href="https://github.com/tensorflow/tfjs-models/tree/master/coco-ssd/demo" target="_blank" rel="noreferrer">Imagem de exemplo: demonstração TensorFlow.js · Apache 2.0</a>}
    </div>
  );
}
