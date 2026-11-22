export type PostmortemTurn = {
  turn: number;
  speaker: 'operator' | 'assistant';
  status: 'completed' | 'interrupted';
  text: string;
  truncated?: boolean;
};
export type PostmortemStatus = {
  id: string;
  status: 'collecting' | 'queued' | 'generating' | 'completed' | 'partial' | 'failed';
  files?: { markdown: string; json: string };
  notice?: string;
};
