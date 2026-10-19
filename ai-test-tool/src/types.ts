export type CaseStatus = 'passed' | 'failed' | 'error' | 'skipped';
export type RunStatus = CaseStatus | 'running' | 'cancelled' | 'timeout' | 'interrupted';
export interface TestCase {
  id: string;
  name: string;
  suite: string;
  classname: string;
  status: CaseStatus;
  duration: number;
  message: string;
  details: string;
  output: string;
}
export interface Summary { total: number; passed: number; failed: number; error: number; skipped: number }
export interface Report { summary: Summary; cases: TestCase[]; warnings: string[]; duration: number }
export interface Analysis {
  model: string;
  createdAt: string;
  explanation: string;
}
export interface Run {
  id: string;
  groupId: string;
  name: string;
  engine: 'vitest' | 'selenium' | 'import';
  source: 'execution' | 'import';
  status: RunStatus;
  startedAt: string;
  finishedAt?: string;
  duration: number;
  timeoutSeconds: number;
  exitCode?: number | null;
  command?: string;
  reportFile?: string;
  report?: Report;
  error?: string;
  analysis?: Analysis;
}
export interface Group {
  id: string;
  name: string;
  engine: 'vitest' | 'selenium';
  description: string;
  files: string[];
  timeoutSeconds: number;
}
export const emptySummary = (): Summary => ({ total: 0, passed: 0, failed: 0, error: 0, skipped: 0 });
