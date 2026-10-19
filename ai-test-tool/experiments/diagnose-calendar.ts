import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import vm from 'node:vm';
import { frontendRoot } from '../src/config.ts';
import { saveEvidence } from './evidence.ts';

// Chẩn đoán hàm sản phẩm hiện có; không viết lại thuật toán, không sửa source/DB.
const require = createRequire(path.join(frontendRoot, 'package.json'));
const ts = require('typescript');
const file = 'hsk-app/frontend/components/stats/StatsClient.tsx';
const source = await readFile(path.join(frontendRoot, 'components/stats/StatsClient.tsx'), 'utf8');
const ast = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const declaration = ast.statements.find((node: any) => ts.isFunctionDeclaration(node) && node.name?.text === 'buildCalendarGrid');
if (!declaration) throw new Error('Không tìm thấy buildCalendarGrid.');
const code = ts.transpileModule(declaration.getText(ast), { compilerOptions: { target: ts.ScriptTarget.ES2022 } }).outputText;
const localDateKey = (date: Date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
const context = vm.createContext({ Date, Map, localDateKey });
vm.runInContext(code, context);
const today = localDateKey(new Date());
const results = [17, 26, 52].map(weeks => {
  const grid = vm.runInContext(`buildCalendarGrid([{date:'${today}',totalCards:20,score:100,sessions:1,durationSec:60}],${weeks})`, context);
  const cells = grid.flat();
  return { weeks, totalCells: cells.length, firstDate: cells[0].date, lastDate: cells.at(-1).date,
    containsToday: cells.some((cell: any) => cell.date === today), activeCells: cells.filter((cell: any) => cell.cards > 0).length };
});
await saveEvidence('calendar-function-observation.json', { checkedAt: new Date().toISOString(), source: file,
  function: 'buildCalendarGrid', method: 'Extract actual function with TypeScript AST, transpile and run in VM without changing source; provide one record for today.', today, results });
console.log(JSON.stringify({ today, results }));
