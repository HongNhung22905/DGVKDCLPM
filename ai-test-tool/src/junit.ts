import { XMLParser, XMLValidator } from 'fast-xml-parser';
import { MAX_XML_BYTES } from './config.ts';
import { emptySummary } from './types.ts';
import type { Report, TestCase, RunStatus } from './types.ts';

const asArray = (value: any): any[] => value === undefined ? [] : Array.isArray(value) ? value : [value];
const number = (value: unknown): number => Math.max(0, Number.isFinite(Number(value)) ? Number(value) : 0);
function text(value: any): string {
  if (value === undefined || value === null) return '';
  if (Array.isArray(value)) return value.map(text).join('\n');
  if (typeof value !== 'object') return String(value);
  return text(value['#text']);
}

export function parseJUnit(xml: string): Report {
  if (!xml.trim() || Buffer.byteLength(xml) > MAX_XML_BYTES) throw new Error('XML trống hoặc vượt giới hạn 8 MB.');
  if (/<!DOCTYPE|<!ENTITY/i.test(xml)) throw new Error('Không hỗ trợ XML có DOCTYPE hoặc ENTITY.');
  const validation = XMLValidator.validate(xml);
  if (validation !== true) throw new Error(`XML không hợp lệ: ${validation.err.msg}`);
  const document = new XMLParser({
    ignoreAttributes: false, attributeNamePrefix: '@_', parseAttributeValue: false,
    parseTagValue: false, trimValues: false, processEntities: true,
  }).parse(xml);
  if (!Object.hasOwn(document, 'testsuites') && !Object.hasOwn(document, 'testsuite')) throw new Error('Cần báo cáo JUnit XML có thẻ testsuites hoặc testsuite.');
  const report: Report = { summary: emptySummary(), cases: [], warnings: [], duration: 0 };
  function visit(suite: any, parents: string[]) {
    if (!suite || typeof suite !== 'object') return;
    const before = { ...report.summary };
    const suitePath = [...parents, String(suite['@_name'] ?? 'Test suite')];
    for (const item of asArray(suite.testcase)) {
      if (report.cases.length >= 20000) throw new Error('Báo cáo vượt giới hạn 20.000 ca kiểm thử.');
      const test = item && typeof item === 'object' ? item : {};
      const status = test.error !== undefined ? 'error' : test.failure !== undefined ? 'failed' : test.skipped !== undefined ? 'skipped' : 'passed';
      const issue = asArray(test.error ?? test.failure ?? test.skipped);
      const testCase: TestCase = {
        id: String(report.cases.length + 1), name: String(test['@_name'] ?? 'Không có tên'),
        suite: suitePath.join(' / '), classname: String(test['@_classname'] ?? ''), status,
        duration: number(test['@_time']), message: issue.map(i => typeof i === 'object' ? String(i?.['@_message'] ?? '') : text(i)).filter(Boolean).join('\n'),
        details: issue.map(text).filter(Boolean).join('\n'),
        output: [text(test['system-out']), text(test['system-err'])].filter(Boolean).join('\n'),
      };
      report.cases.push(testCase);
      report.summary.total++;
      report.summary[status]++;
    }
    for (const issue of asArray(suite.error)) report.warnings.push(`Lỗi cấp suite ${suitePath.join(' / ')}: ${text(issue) || issue?.['@_message'] || 'Không có mô tả'}`);
    for (const child of asArray(suite.testsuite)) visit(child, suitePath);
    for (const [attribute, key] of [['tests', 'total'], ['failures', 'failed'], ['errors', 'error'], ['skipped', 'skipped']] as const) {
      const raw = suite[`@_${attribute}`];
      if (raw === undefined) continue;
      const declared = Number(raw);
      const actual = report.summary[key] - before[key];
      if (!Number.isInteger(declared) || declared < 0 || declared !== actual) report.warnings.push(`${suitePath.join(' / ')}: XML khai báo ${attribute}=${String(raw)} nhưng đọc được ${actual}; kết quả chưa đầy đủ hoặc không nhất quán.`);
    }
  }
  const roots = asArray(document.testsuites ?? document.testsuite);
  for (const root of roots) visit(root, []);
  if (!report.summary.total) report.warnings.push('Báo cáo không chứa ca kiểm thử nào.');
  report.duration = roots.reduce((sum, root) => sum + number(root?.['@_time']), 0) || report.cases.reduce((sum, item) => sum + item.duration, 0);
  return report;
}

export function reportStatus(report: Report, exitCode?: number | null): RunStatus {
  if (report.warnings.length || report.summary.error > 0) return 'error';
  if (report.summary.failed > 0) return 'failed';
  if (exitCode !== undefined && exitCode !== 0) return 'error';
  if (report.summary.passed > 0) return 'passed';
  return 'skipped';
}
