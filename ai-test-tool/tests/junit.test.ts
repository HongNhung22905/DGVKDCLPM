import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseJUnit, reportStatus } from '../src/junit.ts';

test('đọc JUnit của Vitest: tên, thời gian và ký tự XML', () => {
  const report = parseJUnit('<?xml version="1.0"?><testsuites tests="2" failures="0" errors="0" time="1.25"><testsuite name="SM-2"><testcase classname="core.test.ts" name="quality &gt;= 3" time="0.2"/><testcase name="giữ &amp; bảo toàn" time="0.1"/></testsuite></testsuites>');
  assert.deepEqual(report.summary, { total: 2, passed: 2, failed: 0, error: 0, skipped: 0 });
  assert.equal(report.cases[0].name, 'quality >= 3');
  assert.equal(report.cases[1].name, 'giữ & bảo toàn');
  assert.equal(report.duration, 1.25);
  assert.equal(reportStatus(report, 0), 'passed');
});
test('đọc pytest: failure, error thu thập, skipped và CDATA', () => {
  const report = parseJUnit(`<testsuites><testsuite name="pytest" tests="4" failures="1" errors="1" skipped="1">
    <testcase name="pass" time="0.2"/>
    <testcase name="fail"><failure message="không tìm thấy nút"><![CDATA[assert count < 1\nE AssertionError]]></failure><system-out>Captured output</system-out></testcase>
    <testcase name="collection"><error message="ImportError">No module named selenium</error></testcase>
    <testcase name="skip"><skipped message="chưa sẵn sàng"/></testcase>
  </testsuite></testsuites>`);
  assert.deepEqual(report.summary, { total: 4, passed: 1, failed: 1, error: 1, skipped: 1 });
  assert.equal(report.cases[1].details, 'assert count < 1\nE AssertionError');
  assert.equal(report.cases[1].output, 'Captured output');
  assert.equal(report.cases[2].message, 'ImportError');
  assert.equal(reportStatus(report, 1), 'error');
});
test('hỗ trợ root testsuite và suite lồng nhau, không đếm trùng', () => {
  const report = parseJUnit('<testsuite name="parent" tests="2"><testsuite name="child"><testcase name="a"/><testcase name="b"/></testsuite></testsuite>');
  assert.equal(report.summary.total, 2);
  assert.equal(report.cases[0].suite, 'parent / child');
  assert.equal(report.warnings.length, 0);
});
test('không báo PASS khi thiếu testcase, XML rỗng test, hoặc exit code khác 0', () => {
  const incomplete = parseJUnit('<testsuites tests="3"><testsuite><testcase name="only one"/></testsuite></testsuites>');
  assert.equal(reportStatus(incomplete, 0), 'error');
  assert.equal(reportStatus(parseJUnit('<testsuites/>'), 0), 'error');
  assert.equal(reportStatus(parseJUnit('<testsuite><testcase name="ok"/></testsuite>'), 2), 'error');
  assert.equal(reportStatus(parseJUnit('<testsuite><testcase name="skip"><skipped/></testcase></testsuite>'), 0), 'skipped');
});
test('không làm mất trạng thái FAIL khi có test thất bại', () => {
  assert.equal(reportStatus(parseJUnit('<testsuite><testcase name="f"><failure/></testcase></testsuite>'), 1), 'failed');
});
test('không bỏ qua lỗi tổng hợp của suite con trong pytest XML', () => {
  const report = parseJUnit('<testsuites><testsuite tests="1" errors="1"><testcase name="looks passed"/></testsuite></testsuites>');
  assert.equal(reportStatus(report), 'error');
  assert.match(report.warnings[0], /errors=1/);
});
test('từ chối XML hỏng, báo cáo sai định dạng và khai báo entity', () => {
  for (const xml of ['', '<testsuite><testcase></testsuite>', '<html/>', '<!DOCTYPE a [<!ENTITY x SYSTEM "file:///secret">]><testsuite/>']) assert.throws(() => parseJUnit(xml));
});
