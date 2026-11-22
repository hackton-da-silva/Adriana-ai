export type AnnotationBox = { x: number; y: number; width: number; height: number };

export type AnnotationRequest = { id: string; target: string; mode: 'mark' | 'describe' };

export function isAnnotationBox(value: unknown): value is AnnotationBox {
  if (!value || typeof value !== 'object') return false;
  const { x, y, width, height } = value as AnnotationBox;
  return [x, y, width, height].every(Number.isFinite) && x >= 0 && y >= 0 &&
    width > 0 && height > 0 && x + width <= 1.000001 && y + height <= 1.000001;
}
