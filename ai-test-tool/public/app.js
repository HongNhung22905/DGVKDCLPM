const $ = selector => document.querySelector(selector);
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const icon = name => `<svg aria-hidden="true"><use href="#i-${name}"/></svg>`;
const statusLabels = { passed: 'PASS', failed: 'FAIL', error: 'LỖI', skipped: 'BỎ QUA', running: 'ĐANG CHẠY', cancelled: 'ĐÃ DỪNG', timeout: 'HẾT THỜI GIAN', interrupted: 'GIÁN ĐOẠN' };
const badge = status => `<span class="badge ${esc(status)}">${esc(statusLabels[status] || status)}</span>`;
const date = value => value ? new Date(value).toLocaleString('vi-VN', { hour12: false }) : '—';
const duration = seconds => seconds === undefined ? '—' : seconds < 60 ? `${seconds.toFixed(2)}s` : `${Math.floor(seconds / 60)}p ${Math.round(seconds % 60)}s`;
const state = { config: null, runs: [], selected: null, run: null, engine: 'vitest', tab: 'results', caseFilter: 'all', view: 'workspace', log: '', analyzing: false, loading: false, polling: false, detailVersion: '' };
let toastTimer;
function toast(message) {
  $('#toast').textContent = message;
  $('#toast').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 8000);
}
async function api(url, options = {}) {
  const response = await fetch(url, { ...options, headers: { 'Content-Type': 'application/json', ...options.headers } });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Không thể kết nối công cụ.');
  return result;
}
function showView(view) {
  state.view = view;
  for (const element of document.querySelectorAll('.view')) element.hidden = element.id !== `view-${view}`;
  for (const button of document.querySelectorAll('.nav-item')) button.classList.toggle('active', button.dataset.view === view);
  $('#breadcrumb').textContent = { workspace: 'Không gian kiểm thử', history: 'Lịch sử chạy', guide: 'Hướng dẫn sử dụng' }[view];
  if (view === 'history') renderHistory();
}
function renderGroups() {
  const groups = state.config.groups.filter(group => group.engine === state.engine);
  $('#group').innerHTML = groups.map(group => `<option value="${esc(group.id)}">${esc(group.name)}</option>`).join('');
  for (const button of document.querySelectorAll('[data-engine]')) button.classList.toggle('active', button.dataset.engine === state.engine);
  updateGroup();
}
function updateGroup() {
  const group = state.config.groups.find(group => group.id === $('#group').value);
  if (!group) return;
  $('#group-description').textContent = group.description;
  $('#group-files').innerHTML = group.files.map(file => `<div>${esc(file)}</div>`).join('');
  $('#timeout').value = group.timeoutSeconds;
  $('#engine-note').textContent = group.engine === 'vitest' ? 'Chạy bộ hộp trắng hiện có. Không cần khởi động website HSK.' : 'Cần Chrome, pytest, selenium và HSK kiểm thử tại localhost:3000. Khởi động bằng npm --prefix ai-test-tool run hsk:test với Neon branch riêng. Test có thể tạo dữ liệu mới.';
}
function renderConfig() {
  $('#sidebar-ai').textContent = state.config.gemini.configured ? `Đã có API key · ${state.config.gemini.model}` : 'Chưa có API key · vẫn chạy test được';
  $('#run-button').disabled = !!state.config.activeRunId || state.loading;
  $('#run-button').innerHTML = state.config.activeRunId ? '<span class="spinner"></span>Đang có test chạy' : `${icon('play')}Chạy kiểm thử`;
  $('#history-count').textContent = state.runs.length;
}
function renderHeader() {
  const run = state.run;
  if (!run) {
    $('#run-header').innerHTML = '<div class="run-title"><h2>Kết quả lần chạy</h2><p>Chọn nhóm test để bắt đầu</p></div><span class="badge skipped">SẴN SÀNG</span>';
    return;
  }
  $('#run-header').innerHTML = `<div class="run-title"><h2>${esc(run.name)}</h2><p>${badge(run.status)}${esc(date(run.startedAt))}</p></div><div class="run-actions">${run.status === 'running' ? '<button class="button danger" id="cancel-button">Dừng test</button>' : ''}${run.reportFile ? `<a class="button secondary" href="/api/runs/${run.id}/xml">${icon('download')}XML</a>` : ''}</div>`;
}
function renderMetrics() {
  const summary = state.run?.report?.summary;
  const known = !!summary;
  const rate = known && summary.total ? `${Math.round(summary.passed / summary.total * 100)}%` : '—';
  $('#metrics').innerHTML = [
    ['TỔNG CA KIỂM THỬ', known ? summary.total : '—', known ? `${summary.skipped} bỏ qua · ${summary.error} lỗi` : 'Chưa có báo cáo', 'code', ''],
    ['CA ĐẠT', known ? summary.passed : '—', known ? `${summary.failed} thất bại · ${rate} đạt trên tổng ca` : 'Chờ kết quả từ XML', 'check', 'success'],
    ['THỜI GIAN', state.run ? duration(state.run.status === 'running' ? (Date.now() - Date.parse(state.run.startedAt)) / 1000 : state.run.duration) : '—', state.run?.source === 'import' ? 'Thời gian khai báo trong XML' : 'Thời gian toàn bộ lần chạy', 'clock', ''],
  ].map(([label, value, note, glyph, color]) => `<div class="metric"><span class="metric-label">${label}</span>${icon(glyph)}<span class="metric-value ${color}">${esc(value)}</span><span class="metric-note">${esc(note)}</span></div>`).join('');
}
function empty(title, description, glyph = 'lab', caption = '') {
  return `<div class="empty-state"><span class="empty-icon">${icon(glyph)}</span><h3>${esc(title)}</h3><p>${esc(description)}</p>${caption ? `<span class="empty-caption">${esc(caption)}</span>` : ''}</div>`;
}
function resultMarkup() {
  const run = state.run;
  if (!run) return empty('Sẵn sàng cho lần chạy đầu tiên', 'Chọn nhóm kiểm thử bên trái rồi bấm Chạy kiểm thử. Bạn cũng có thể nhập báo cáo XML đã có.', 'lab', 'SELENIUM + VITEST');
  let markup = run.source === 'import' ? '<div class="notice">Báo cáo XML được nhập để xem lại. Đây không phải kết quả chạy mới từ công cụ; thời điểm hiển thị là thời điểm nhập.</div>' : '';
  if (run.error) markup += `<div class="notice error">${esc(run.error)}</div>`;
  if (run.status === 'running') return markup + empty('Đang thực thi bộ kiểm thử…', 'Mở tab Nhật ký để theo dõi tiến trình. Kết quả chi tiết xuất hiện sau khi trình chạy hoàn tất.', 'clock');
  if (!run.report) return markup + empty('Chưa có báo cáo kiểm thử', 'Xem nhật ký để tìm lỗi khởi động, dependency hoặc nguyên nhân chưa tạo được XML.', 'code');
  const summary = run.report.summary;
  if (run.report.warnings.length) markup += `<div class="notice error">${esc(run.report.warnings.join('\n'))}</div>`;
  const cases = run.report.cases.filter(test => state.caseFilter === 'all' || (state.caseFilter === 'issues' ? ['failed', 'error'].includes(test.status) : test.status === state.caseFilter));
  markup += `<div class="case-toolbar"><div class="case-counts"><span>${summary.passed} PASS</span><span>${summary.failed} FAIL</span><span>${summary.error} lỗi</span><span>${summary.skipped} bỏ qua</span></div><select id="case-filter" aria-label="Lọc kết quả ca kiểm thử">${[['all', 'Tất cả ca'], ['issues', 'Chỉ ca có lỗi'], ['passed', 'PASS'], ['failed', 'FAIL'], ['error', 'Lỗi'], ['skipped', 'Bỏ qua']].map(([value, label]) => `<option value="${value}" ${state.caseFilter === value ? 'selected' : ''}>${label}</option>`).join('')}</select></div>`;
  markup += `<div class="case-list">${cases.length ? cases.map(test => `<details class="case"><summary>${badge(test.status)}<span class="case-name">${esc(test.name)}</span><span class="case-time">${duration(test.duration)}</span></summary><div class="case-body"><p>${esc(test.suite)}${test.classname ? ` · ${esc(test.classname)}` : ''}</p>${test.message ? `<pre class="issue">${esc(test.message)}</pre>` : ''}${test.details ? `<pre class="issue">${esc(test.details)}</pre>` : ''}${test.output ? `<pre class="output">${esc(test.output)}</pre>` : ''}${!test.message && !test.details && !test.output ? 'XML không có thông tin bổ sung cho ca này.' : ''}</div></details>`).join('') : '<div class="table-empty">Không có ca phù hợp với bộ lọc.</div>'}</div>`;
  return markup;
}
function aiMarkup() {
  if (!state.run) return empty('Phân tích bắt đầu từ một kết quả', 'Chạy test hoặc nhập XML để có dữ liệu phân tích.', 'spark');
  const run = state.run;
  let markup = `<div class="ai-intro">${icon('spark')}<div><h3>Hiểu lỗi cùng Gemini</h3><p>Giải thích bằng chứng và gợi ý bước kiểm tra. Các nguyên nhân AI đề xuất cần được xác minh.</p></div></div>`;
  if (run.analysis) return markup + `<div class="ai-meta">${esc(run.analysis.model)} · ${esc(date(run.analysis.createdAt))}</div><div class="notice">Phân tích tham khảo. Trạng thái kiểm thử được giữ theo kết quả của trình chạy và XML.</div><div class="ai-result">${esc(run.analysis.explanation)}</div>`;
  if (!state.config.gemini.configured) return markup + '<div class="notice">Chưa có GEMINI_API_KEY. Phần chạy test, XML và lịch sử vẫn hoạt động bình thường.</div><p class="field-help">Tạo ai-test-tool/.env từ .env.example, bổ sung key rồi khởi động lại công cụ. Xem hướng dẫn để biết thêm.</p><button class="button secondary" data-view="guide">Mở hướng dẫn</button>';
  if (run.status === 'running') return markup + '<div class="notice">Đợi test hoàn tất để phân tích lỗi.</div>';
  if (['passed', 'skipped'].includes(run.status)) return markup + '<div class="notice">Lần chạy này không có lỗi cần Gemini phân tích.</div>';
  markup += '<div class="notice">Khi bấm phân tích, công cụ gửi tối đa 15 ca lỗi cùng phần cuối nhật ký đã rút gọn tới Gemini. Một số thông tin nhạy cảm phổ biến được che tự động. Kiểm tra nội dung lỗi trước khi gửi.</div>';
  return markup + `<button class="button primary" id="analyze-button" ${state.analyzing || run.analyzing ? 'disabled' : ''}>${state.analyzing || run.analyzing ? '<span class="spinner"></span>Đang phân tích…' : `${icon('spark')}Phân tích lỗi bằng Gemini`}</button>`;
}
function renderContent() {
  for (const button of document.querySelectorAll('[data-tab]')) {
    button.classList.toggle('active', button.dataset.tab === state.tab);
    button.setAttribute('aria-selected', String(button.dataset.tab === state.tab));
  }
  $('#result-content').setAttribute('aria-labelledby', `tab-${state.tab}`);
  $('#result-content').innerHTML = state.tab === 'results' ? resultMarkup() : state.tab === 'ai' ? aiMarkup() : state.run ? `<div class="command">${esc(state.run.command || 'Báo cáo XML nhập từ tệp; không có lệnh chạy.')}</div><pre class="log" tabindex="0">${esc(state.log || (state.run.source === 'import' ? 'Báo cáo nhập không kèm nhật ký tiến trình. Mở chi tiết từng ca để xem lỗi trong XML.' : 'Chưa có nhật ký từ tiến trình.'))}</pre>` : empty('Nhật ký thực thi', 'Chọn một lần chạy để xem đầu ra từ Vitest hoặc pytest.', 'code');
}
function renderRun() { renderHeader(); renderMetrics(); renderContent(); }
function tableMarkup(runs) {
  if (!runs.length) return '<div class="table-empty">Chưa có lần chạy hoặc báo cáo phù hợp. Kết quả sẽ xuất hiện tại đây.</div>';
  return `<table><thead><tr><th>NHÓM KIỂM THỬ / BÁO CÁO</th><th>TRẠNG THÁI</th><th>KẾT QUẢ</th><th>THỜI GIAN</th><th>THỜI ĐIỂM</th></tr></thead><tbody>${runs.map(run => `<tr><td><button class="run-link" data-run="${run.id}">${esc(run.name)}<small>${run.source === 'import' ? 'XML nhập vào' : run.engine === 'vitest' ? 'Vitest · chạy trực tiếp' : 'Selenium · chạy trực tiếp'}</small></button></td><td>${badge(run.status)}</td><td>${run.summary ? `${run.summary.passed}/${run.summary.total} đạt` : '—'}</td><td>${run.status === 'running' ? 'Đang chạy' : duration(run.duration)}</td><td>${esc(date(run.startedAt))}</td></tr>`).join('')}</tbody></table>`;
}
function renderHistory() {
  $('#recent-runs').innerHTML = tableMarkup(state.runs.slice(0, 5));
  const query = $('#history-search').value.toLocaleLowerCase('vi-VN');
  const status = $('#history-status').value;
  $('#history-runs').innerHTML = tableMarkup(state.runs.filter(run => run.name.toLocaleLowerCase('vi-VN').includes(query) && (status === 'all' || run.status === status)));
}
async function selectRun(id) {
  state.selected = id;
  state.run = null;
  state.log = '';
  state.caseFilter = 'all';
  state.detailVersion = '';
  showView('workspace');
  await loadRun(true);
}
async function loadRun(force = false) {
  if (!state.selected) { renderRun(); return; }
  const id = state.selected;
  const [run, { log }] = await Promise.all([api(`/api/runs/${id}`), api(`/api/runs/${id}/log`)]);
  if (state.selected !== id) return;
  state.run = run;
  state.log = log;
  const version = JSON.stringify([run.status, run.analysis, run.analyzing, run.error, !!run.report, state.tab === 'log' ? log : '']);
  if (force || version !== state.detailVersion) { renderRun(); state.detailVersion = version; }
  else if (run.status === 'running') renderMetrics();
}
async function refresh() {
  if (state.polling) return;
  state.polling = true;
  try {
    const [config, runs] = await Promise.all([api('/api/config'), api('/api/runs')]);
    state.config = config;
    const changed = JSON.stringify(state.runs) !== JSON.stringify(runs);
    state.runs = runs;
    renderConfig();
    if (changed) renderHistory();
    if (!state.selected && runs.length) state.selected = config.activeRunId || runs[0].id;
    await loadRun();
  } finally { state.polling = false; }
}

document.addEventListener('click', async event => {
  const target = event.target.closest('button');
  if (!target) return;
  try {
    if (target.dataset.view) showView(target.dataset.view);
    if (target.dataset.engine && state.config) { state.engine = target.dataset.engine; renderGroups(); }
    if (target.dataset.tab) { state.tab = target.dataset.tab; renderContent(); }
    if (target.dataset.run) await selectRun(target.dataset.run);
    if (target.classList.contains('import-button')) $('#xml-file').click();
    if (target.id === 'run-button') {
      const timeoutSeconds = Number($('#timeout').value);
      if (!Number.isInteger(timeoutSeconds) || timeoutSeconds < 10 || timeoutSeconds > 7200) throw new Error('Giới hạn thời gian phải từ 10 đến 7200 giây.');
      state.loading = true;
      renderConfig();
      try {
        const run = await api('/api/runs', { method: 'POST', body: JSON.stringify({ groupId: $('#group').value, timeoutSeconds }) });
        state.tab = 'results';
        await selectRun(run.id);
        toast('Đã bắt đầu chạy kiểm thử.');
        await refresh();
      } finally { state.loading = false; renderConfig(); }
    }
    if (target.id === 'cancel-button') {
      target.disabled = true;
      await api(`/api/runs/${state.selected}/cancel`, { method: 'POST', body: '{}' });
      toast('Đã gửi yêu cầu dừng tiến trình test.');
      await refresh();
    }
    if (target.id === 'analyze-button') {
      const id = state.selected;
      state.analyzing = true;
      renderContent();
      try {
        await api(`/api/runs/${id}/analysis`, { method: 'POST', body: '{}' });
        if (state.selected === id) await loadRun(true);
        toast('Đã lưu phân tích Gemini vào lịch sử lần chạy.');
      } finally { state.analyzing = false; renderContent(); }
    }
  } catch (error) { toast(error.message); }
});
$('#group').addEventListener('change', updateGroup);
$('#history-search').addEventListener('input', renderHistory);
$('#history-status').addEventListener('change', renderHistory);
document.addEventListener('change', event => {
  if (event.target.id === 'case-filter') { state.caseFilter = event.target.value; renderContent(); }
});
$('#xml-file').addEventListener('change', async event => {
  const file = event.target.files?.[0];
  if (!file) return;
  try {
    if (file.size > 8 * 1024 * 1024) throw new Error('Tệp XML vượt giới hạn 8 MB.');
    const run = await api('/api/import', { method: 'POST', body: JSON.stringify({ filename: file.name, xml: await file.text() }) });
    state.tab = 'results';
    await selectRun(run.id);
    await refresh();
    toast('Đã nhập XML và lưu vào lịch sử.');
  } catch (error) { toast(error.message); }
  finally { event.target.value = ''; }
});

async function init() {
  renderRun();
  renderHistory();
  try {
    state.config = await api('/api/config');
    renderGroups();
    await refresh();
    setInterval(() => { void refresh().catch(() => { /* Kết nối sẽ được thử lại ở nhịp tiếp theo. */ }); }, 1500);
  } catch (error) {
    toast(`Không tải được công cụ: ${error.message}. Kiểm tra backend rồi tải lại trang.`);
    $('#run-button').disabled = true;
  }
}
void init();
