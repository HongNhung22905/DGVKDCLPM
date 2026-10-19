import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { redact } from '../src/redact.ts';

export const evidenceRoot = fileURLToPath(new URL('./2026-10-19/', import.meta.url));
export async function saveEvidence(name: string, value: unknown) {
  await mkdir(evidenceRoot, { recursive: true });
  await writeFile(path.join(evidenceRoot, name), redact(JSON.stringify(value, null, 2)) + '\n', 'utf8');
}
export async function loadEvidence(name: string): Promise<any> {
  return JSON.parse(await readFile(path.join(evidenceRoot, name), 'utf8'));
}
