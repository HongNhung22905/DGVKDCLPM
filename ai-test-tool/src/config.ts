import { fileURLToPath } from 'node:url';
import path from 'node:path';
import type { Group } from './types.ts';

export const toolRoot = fileURLToPath(new URL('../', import.meta.url));
export const repoRoot = path.resolve(toolRoot, '..');
export const frontendRoot = path.join(repoRoot, 'hsk-app', 'frontend');
export const seleniumRoot = path.join(repoRoot, 'selenium-tests');
export const dataRoot = path.join(toolRoot, 'data', 'runs');
export const publicRoot = path.join(toolRoot, 'public');
export const MAX_XML_BYTES = 8 * 1024 * 1024;
export const MAX_LOG_BYTES = 1024 * 1024;

const selenium = (id: string, name: string, description: string, files: string[]): Group => ({
  id, name, description, files: files.map(file => `${file}.py`), engine: 'selenium', timeoutSeconds: 1800,
});
export const groups: Group[] = [
  { id: 'vitest-all', name: 'Toàn bộ kiểm thử hộp trắng', engine: 'vitest', description: '22 ca có sẵn: SM-2, mở khóa, ngưỡng điểm và bảo toàn kết quả.', files: ['tests/whitebox/core.test.ts', 'tests/whitebox/gate.test.ts'], timeoutSeconds: 120 },
  { id: 'vitest-core', name: 'SM-2 và mở khóa bài', engine: 'vitest', description: '17 ca trong core.test.ts, kiểm tra lịch ôn và quyền truy cập bài học.', files: ['tests/whitebox/core.test.ts'], timeoutSeconds: 120 },
  { id: 'vitest-gate', name: 'Ngưỡng điểm và bảo toàn kết quả', engine: 'vitest', description: '5 ca trong gate.test.ts, gồm các biên 79 / 80 / 81 điểm.', files: ['tests/whitebox/gate.test.ts'], timeoutSeconds: 120 },
  selenium('selenium-auth', 'Đăng ký, đăng nhập và đăng xuất', 'Kiểm tra các luồng xác thực bằng Chrome.', ['test_register', 'test_login', 'test_logout']),
  selenium('selenium-vocabulary', 'Từ vựng và flashcard', 'Cấp HSK, bài học, lật thẻ và đánh giá từ.', ['test_vocabulary', 'test_flashcard']),
  selenium('selenium-unlock', 'Mở khóa nhóm bài', 'Ngưỡng điểm, thử lại, pinyin và khôi phục phiên.', ['test_unlock', 'test_unlock_score', 'test_unlock_retry', 'test_unlock_pinyin', 'test_unlock_session']),
  selenium('selenium-review', 'Ôn tập SM-2', 'Thẻ đến hạn, chưa đến hạn, đánh giá và lịch sử ôn.', ['test_review', 'test_review_due', 'test_review_future', 'test_review_rate', 'test_review_repeat', 'test_review_history']),
  selenium('selenium-progress', 'Tiến độ, thống kê và dữ liệu', 'Tiến độ học, lịch thống kê, lưu phiên và cách ly tài khoản.', ['test_progress', 'test_progress_cards', 'test_progress_completed', 'test_stats', 'test_stats_calendar', 'test_stats_persistence', 'test_stats_session', 'test_data_isolation']),
  selenium('selenium-writing', 'Luyện viết chữ Hán', 'Luyện viết, kiểm tra nét và hoàn thành chữ.', ['test_writing', 'test_writing_quiz', 'test_writing_complete']),
  selenium('selenium-game', 'Trò chơi học tập', 'Chế độ chữ Hán, hỗn hợp và hoàn thành trò chơi.', ['test_game', 'test_game_hanzi', 'test_game_mixed', 'test_game_complete']),
  selenium('selenium-notebook', 'Tra từ và sổ tay', 'Tìm từ và thao tác sổ tay.', ['test_search', 'test_notebook']),
];
groups.push(selenium('selenium-all', 'Toàn bộ Selenium', 'Chạy tất cả các nhóm Selenium hiện có; có thể mất nhiều thời gian.', [...new Set(groups.filter(g => g.engine === 'selenium').flatMap(g => g.files.map(f => f.slice(0, -3))))]));
groups.at(-1)!.timeoutSeconds = 7200;
