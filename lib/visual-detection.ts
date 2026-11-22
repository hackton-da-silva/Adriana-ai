export type VisualDetection = {
  label: string;
  score: number;
  box: { x: number; y: number; width: number; height: number };
};

export type VisualSource = HTMLVideoElement | HTMLCanvasElement;

export interface VisualDetector {
  detect(source: VisualSource): Promise<VisualDetection[]>;
  dispose(): void;
}

// Normalized coordinates keep the overlay aligned when the preview is resized.
export function normalizePersonDetections(
  predictions: { class: string; score: number; bbox: number[] }[],
  width: number,
  height: number,
): VisualDetection[] {
  if (!(width > 0 && height > 0)) return [];

  return predictions.flatMap((prediction) => {
    if (prediction.class !== 'person' || !Number.isFinite(prediction.score)) return [];
    const [x, y, boxWidth, boxHeight] = prediction.bbox;
    if (![x, y, boxWidth, boxHeight].every(Number.isFinite) || boxWidth <= 0 || boxHeight <= 0) return [];
    const left = Math.max(0, Math.min(1, x / width));
    const top = Math.max(0, Math.min(1, y / height));
    const right = Math.max(0, Math.min(1, (x + boxWidth) / width));
    const bottom = Math.max(0, Math.min(1, (y + boxHeight) / height));
    if (right <= left || bottom <= top) return [];
    return [{
      label: 'Pessoa',
      score: Math.max(0, Math.min(1, prediction.score)),
      box: { x: left, y: top, width: right - left, height: bottom - top },
    }];
  });
}

export async function loadPersonDetector(): Promise<VisualDetector> {
  const tf = await import('@tensorflow/tfjs-core');
  await Promise.all([
    import('@tensorflow/tfjs-backend-webgl'),
    import('@tensorflow/tfjs-backend-cpu'),
  ]);
  try {
    if (!(await tf.setBackend('webgl'))) await tf.setBackend('cpu');
  } catch {
    await tf.setBackend('cpu');
  }
  await tf.ready();
  const cocoSsd = await import('@tensorflow-models/coco-ssd');
  const model = await cocoSsd.load({
    base: 'lite_mobilenet_v2',
    modelUrl: '/vision-demo/coco-ssd/model.json',
  });

  return {
    async detect(source) {
      const width = 'videoWidth' in source ? source.videoWidth : source.width;
      const height = 'videoHeight' in source ? source.videoHeight : source.height;
      if (!width || !height) return [];
      const predictions = await model.detect(source, 20, 0.3);
      return normalizePersonDetections(predictions, width, height);
    },
    dispose: () => model.dispose(),
  };
}
