# Truy vết yêu cầu → ca kiểm thử → kết quả → minh chứng

Đề tài: **Kiểm thử tự động website hỗ trợ học tiếng Trung và xây dựng công cụ tích hợp AI hỗ trợ phân tích kết quả.** Website HSK là đối tượng đánh giá chính; phần công cụ là minh chứng cho sản phẩm hỗ trợ. [Bảng chốt minh chứng, phiên bản và môi trường](EVIDENCE-BASELINE.md).

Cập nhật tài liệu **20/10/2026**, nguồn thực nghiệm **19/10/2026**. Bảng được sinh từ XML, mã test và nhật ký đã lưu, không chạy test mới. Mã yêu cầu là nhãn truy vết của báo cáo, không thay thế đặc tả nghiệp vụ hoặc chứng minh độ bao phủ toàn website.

Chạy `python ai-test-tool/experiments/build-traceability.py --check` để đối chiếu bảng với nguồn; bỏ `--check` để sinh lại sau khi rà soát. Script dừng nếu số liệu mốc hoặc kết quả từng ca không khớp.

## 1. Phân biệt các bộ kết quả

| Bộ | Kết quả | Nguồn chuẩn |
| --- | --- | --- |
| Selenium lượt đầy đủ | 85 ca: 75 PASS, 10 FAIL, 0 ERROR/SKIP | [XML gốc](../experiments/2026-10-19/selenium-all-122951/report.xml), run ID `04d381c9-e06b-453e-9601-2a698141b34a` |
| Logic HSK (Vitest) | 22/22 PASS mỗi cách CLI/UI | [XML UI](../experiments/2026-10-19/vitest-ui.xml), [đối chiếu](../experiments/2026-10-19/cli-ui-comparison.json) |
| Selenium nhóm nhỏ, lượt khác | UI 10/10 PASS; CLI 10/10 PASS | [Đối chiếu nhóm nhỏ](../experiments/2026-10-19/selenium-cli-ui-comparison.json) |
| Công cụ | 21/21 đạt | [Nhật ký 21 ca](../experiments/2026-10-19/tool-tests-after-selenium.log) |
| Nhập XML lịch sử | 70/70 tệp khớp, 115 bản ghi testcase có trùng giữa các lượt | [Đối chiếu XML](../experiments/2026-10-19/xml-compatibility.json) |
| AI, đánh giá sơ bộ | 10 mẫu: 7 đúng, 3 đúng một phần; chưa chấm độc lập | [Điểm sơ bộ](../experiments/2026-10-19/ai-judgements.json), [phiếu độc lập trống](AI-INDEPENDENT-REVIEW.md) |

Không cộng các dòng thành một tổng ca đạt. Mốc 18/18 công cụ là mốc cũ, đã được thay bằng bộ 21 ca. Nhóm nhỏ là tập con chạy ở lượt khác; NOTE-04 PASS ở nhóm nhỏ không thay FAIL của lượt đầy đủ. 70 XML không phải 70 lượt chạy mới. 7/10 mẫu AI không phải độ chính xác chung.

## 2. Yêu cầu HSK và kết quả Selenium

Đây là hành vi được các test có sẵn kiểm tra. Mỗi file thuộc đúng một nhóm dưới đây; 9 lựa chọn Selenium trên UI gồm 8 nhóm chức năng và 1 lựa chọn toàn bộ, không phải 9 bộ độc lập.

| Yêu cầu HSK | Tiêu chí mong đợi | Test tương ứng (tên file, bỏ tiền tố test_) | Tổng | PASS | FAIL | Lỗi |
| --- | --- | --- | ---: | ---: | ---: | --- |
| HSK-AUTH | Đầu vào hợp lệ tạo/đăng nhập được; email trùng và đầu vào sai bị từ chối, gồm tên rỗng sau trim; đăng xuất kết thúc phiên | [register](../../selenium-tests/test_register.py), [login](../../selenium-tests/test_login.py), [logout](../../selenium-tests/test_logout.py) | 18 | 17 | 1 | HSK-001 |
| HSK-VOC | Chọn HSK 1…7, hiển thị bài/hành động học đúng và quay lại được; khóa bài ban đầu, điều hướng từ và flashcard đúng kỳ vọng từng ca | [vocabulary](../../selenium-tests/test_vocabulary.py), [flashcard](../../selenium-tests/test_flashcard.py) | 17 | 10 | 7 | HSK-002 |
| HSK-UNLOCK | Đạt ngưỡng thì mở, chưa đạt thì khóa; thử lại thấp hơn không mất quyền đã đạt; xử lý pinyin và khôi phục quyền ở trình duyệt mới đúng | [unlock](../../selenium-tests/test_unlock.py), [unlock_score](../../selenium-tests/test_unlock_score.py), [unlock_retry](../../selenium-tests/test_unlock_retry.py), [unlock_pinyin](../../selenium-tests/test_unlock_pinyin.py), [unlock_session](../../selenium-tests/test_unlock_session.py) | 9 | 9 | 0 | — |
| HSK-REVIEW | Tài khoản mới rỗng; thẻ đến hạn xuất hiện, thẻ tương lai bị loại; đánh giá/lặp thẻ và lưu lịch sử một lần đúng assertion | [review](../../selenium-tests/test_review.py), [review_due](../../selenium-tests/test_review_due.py), [review_future](../../selenium-tests/test_review_future.py), [review_rate](../../selenium-tests/test_review_rate.py), [review_repeat](../../selenium-tests/test_review_repeat.py), [review_history](../../selenium-tests/test_review_history.py) | 8 | 8 | 0 | — |
| HSK-PROGRESS | Tiến độ/thống kê phản ánh dữ liệu học, giữ sau tải lại/đăng nhập; lịch chứa hoạt động hôm nay; dữ liệu hai tài khoản không lẫn | [progress](../../selenium-tests/test_progress.py), [progress_cards](../../selenium-tests/test_progress_cards.py), [progress_completed](../../selenium-tests/test_progress_completed.py), [stats](../../selenium-tests/test_stats.py), [stats_calendar](../../selenium-tests/test_stats_calendar.py), [stats_persistence](../../selenium-tests/test_stats_persistence.py), [stats_session](../../selenium-tests/test_stats_session.py), [data_isolation](../../selenium-tests/test_data_isolation.py) | 8 | 7 | 1 | HSK-003 |
| HSK-WRITE | Mở đúng chế độ luyện viết; nét sai không tính hoàn thành; hoàn thành chữ được ghi nhận theo ca hiện có | [writing](../../selenium-tests/test_writing.py), [writing_quiz](../../selenium-tests/test_writing_quiz.py), [writing_complete](../../selenium-tests/test_writing_complete.py) | 7 | 7 | 0 | — |
| HSK-GAME | Mở/chơi được các chế độ; đáp án đúng/sai, điểm và kết thúc trò chơi thống nhất với ca hiện có | [game](../../selenium-tests/test_game.py), [game_hanzi](../../selenium-tests/test_game_hanzi.py), [game_mixed](../../selenium-tests/test_game_mixed.py), [game_complete](../../selenium-tests/test_game_complete.py) | 8 | 8 | 0 | — |
| HSK-NOTE | Tìm/lọc từ đúng; thêm/lưu không trùng, sửa ghi chú và xóa được; API và UI thống nhất, xóa hết hiển thị sổ tay trống | [search](../../selenium-tests/test_search.py), [notebook](../../selenium-tests/test_notebook.py) | 10 | 9 | 1 | HSK-004 |
| **Tổng lượt chính** | | | **85** | **75** | **10** | **4 nhóm phát hiện** |

Các tiêu chí trên được rút từ hành vi mong đợi của test có sẵn, không phải đặc tả đã được chủ sản phẩm duyệt lại. Ví dụ ngưỡng số cụ thể xem assertion và WB-GATE bên dưới. Các kiểm tra API trong Selenium cùng thuộc ca gốc, không cộng thành số ca API độc lập. Việc 8 nhóm có test không phải code coverage hoặc tỷ lệ bao phủ toàn bộ yêu cầu HSK.

### Từng ca của lượt chính

Nguồn trạng thái cho toàn bộ bảng: [report.xml](../experiments/2026-10-19/selenium-all-122951/report.xml), đối chiếu với [run.json](../experiments/2026-10-19/selenium-all-122951/run.json) và [DOM lịch sử](../experiments/2026-10-19/selenium-dom-verification.json). Tên ca giữ nguyên từ XML; các ID S-xxx chỉ để tra cứu trong báo cáo. Ảnh và cách tái hiện theo mã lỗi ở [bảng lỗi](DEFECT-REGISTER.md).

| ID | Yêu cầu | Ca gốc | Trạng thái | Mã lỗi | Nguồn test |
| --- | --- | --- | --- | --- | --- |
| S-001 | HSK-AUTH | `test_register_valid[REG-01]` | PASS | — | [test_register.py](../../selenium-tests/test_register.py) |
| S-002 | HSK-AUTH | `test_register_valid[REG-06]` | PASS | — | [test_register.py](../../selenium-tests/test_register.py) |
| S-003 | HSK-AUTH | `test_register_password_5_chars` | PASS | — | [test_register.py](../../selenium-tests/test_register.py) |
| S-004 | HSK-AUTH | `test_register_invalid_input[REG-02]` | PASS | — | [test_register.py](../../selenium-tests/test_register.py) |
| S-005 | HSK-AUTH | `test_register_invalid_input[REG-03]` | PASS | — | [test_register.py](../../selenium-tests/test_register.py) |
| S-006 | HSK-AUTH | `test_register_invalid_input[REG-04]` | PASS | — | [test_register.py](../../selenium-tests/test_register.py) |
| S-007 | HSK-AUTH | `test_register_invalid_input[REG-08]` | PASS | — | [test_register.py](../../selenium-tests/test_register.py) |
| S-008 | HSK-AUTH | `test_register_duplicate_email` | PASS | — | [test_register.py](../../selenium-tests/test_register.py) |
| S-009 | HSK-AUTH | `test_register_whitespace_name` | FAIL | HSK-001 | [test_register.py](../../selenium-tests/test_register.py) |
| S-010 | HSK-AUTH | `test_login_valid[LOGIN-01]` | PASS | — | [test_login.py](../../selenium-tests/test_login.py) |
| S-011 | HSK-AUTH | `test_login_valid[LOGIN-07]` | PASS | — | [test_login.py](../../selenium-tests/test_login.py) |
| S-012 | HSK-AUTH | `test_login_valid[LOGIN-08]` | PASS | — | [test_login.py](../../selenium-tests/test_login.py) |
| S-013 | HSK-AUTH | `test_login_invalid_credentials[LOGIN-02]` | PASS | — | [test_login.py](../../selenium-tests/test_login.py) |
| S-014 | HSK-AUTH | `test_login_invalid_credentials[LOGIN-03]` | PASS | — | [test_login.py](../../selenium-tests/test_login.py) |
| S-015 | HSK-AUTH | `test_login_invalid_input[LOGIN-04]` | PASS | — | [test_login.py](../../selenium-tests/test_login.py) |
| S-016 | HSK-AUTH | `test_login_invalid_input[LOGIN-05]` | PASS | — | [test_login.py](../../selenium-tests/test_login.py) |
| S-017 | HSK-AUTH | `test_login_invalid_input[LOGIN-06]` | PASS | — | [test_login.py](../../selenium-tests/test_login.py) |
| S-018 | HSK-AUTH | `test_logout` | PASS | — | [test_logout.py](../../selenium-tests/test_logout.py) |
| S-019 | HSK-VOC | `test_select_level_and_return[HSK-1]` | FAIL | HSK-002 | [test_vocabulary.py](../../selenium-tests/test_vocabulary.py) |
| S-020 | HSK-VOC | `test_select_level_and_return[HSK-2]` | FAIL | HSK-002 | [test_vocabulary.py](../../selenium-tests/test_vocabulary.py) |
| S-021 | HSK-VOC | `test_select_level_and_return[HSK-3]` | FAIL | HSK-002 | [test_vocabulary.py](../../selenium-tests/test_vocabulary.py) |
| S-022 | HSK-VOC | `test_select_level_and_return[HSK-4]` | FAIL | HSK-002 | [test_vocabulary.py](../../selenium-tests/test_vocabulary.py) |
| S-023 | HSK-VOC | `test_select_level_and_return[HSK-5]` | FAIL | HSK-002 | [test_vocabulary.py](../../selenium-tests/test_vocabulary.py) |
| S-024 | HSK-VOC | `test_select_level_and_return[HSK-6]` | FAIL | HSK-002 | [test_vocabulary.py](../../selenium-tests/test_vocabulary.py) |
| S-025 | HSK-VOC | `test_select_level_and_return[HSK-7]` | FAIL | HSK-002 | [test_vocabulary.py](../../selenium-tests/test_vocabulary.py) |
| S-026 | HSK-VOC | `test_initial_lesson_locks` | PASS | — | [test_vocabulary.py](../../selenium-tests/test_vocabulary.py) |
| S-027 | HSK-VOC | `test_open_lesson_detail` | PASS | — | [test_vocabulary.py](../../selenium-tests/test_vocabulary.py) |
| S-028 | HSK-VOC | `test_study_word_navigation` | PASS | — | [test_vocabulary.py](../../selenium-tests/test_vocabulary.py) |
| S-029 | HSK-VOC | `test_open_flashcard[FC-01]` | PASS | — | [test_flashcard.py](../../selenium-tests/test_flashcard.py) |
| S-030 | HSK-VOC | `test_open_flashcard[FC-02]` | PASS | — | [test_flashcard.py](../../selenium-tests/test_flashcard.py) |
| S-031 | HSK-VOC | `test_open_flashcard[FC-03]` | PASS | — | [test_flashcard.py](../../selenium-tests/test_flashcard.py) |
| S-032 | HSK-VOC | `test_open_flashcard[FC-04]` | PASS | — | [test_flashcard.py](../../selenium-tests/test_flashcard.py) |
| S-033 | HSK-VOC | `test_open_flashcard[FC-05]` | PASS | — | [test_flashcard.py](../../selenium-tests/test_flashcard.py) |
| S-034 | HSK-VOC | `test_open_flashcard[FC-06]` | PASS | — | [test_flashcard.py](../../selenium-tests/test_flashcard.py) |
| S-035 | HSK-VOC | `test_open_flashcard[FC-07]` | PASS | — | [test_flashcard.py](../../selenium-tests/test_flashcard.py) |
| S-036 | HSK-UNLOCK | `test_start_first_group_test` | PASS | — | [test_unlock.py](../../selenium-tests/test_unlock.py) |
| S-037 | HSK-UNLOCK | `test_group_unlock_by_score[UNLOCK-02]` | PASS | — | [test_unlock_score.py](../../selenium-tests/test_unlock_score.py) |
| S-038 | HSK-UNLOCK | `test_group_unlock_by_score[UNLOCK-03]` | PASS | — | [test_unlock_score.py](../../selenium-tests/test_unlock_score.py) |
| S-039 | HSK-UNLOCK | `test_group_unlock_by_score[UNLOCK-04]` | PASS | — | [test_unlock_score.py](../../selenium-tests/test_unlock_score.py) |
| S-040 | HSK-UNLOCK | `test_lower_retry_preserves_unlock` | PASS | — | [test_unlock_retry.py](../../selenium-tests/test_unlock_retry.py) |
| S-041 | HSK-UNLOCK | `test_pinyin_validation[UNLOCK-06]` | PASS | — | [test_unlock_pinyin.py](../../selenium-tests/test_unlock_pinyin.py) |
| S-042 | HSK-UNLOCK | `test_pinyin_validation[UNLOCK-07]` | PASS | — | [test_unlock_pinyin.py](../../selenium-tests/test_unlock_pinyin.py) |
| S-043 | HSK-UNLOCK | `test_pinyin_validation[UNLOCK-08]` | PASS | — | [test_unlock_pinyin.py](../../selenium-tests/test_unlock_pinyin.py) |
| S-044 | HSK-UNLOCK | `test_unlock_restored_in_new_browser` | PASS | — | [test_unlock_session.py](../../selenium-tests/test_unlock_session.py) |
| S-045 | HSK-REVIEW | `test_review_empty_for_new_account` | PASS | — | [test_review.py](../../selenium-tests/test_review.py) |
| S-046 | HSK-REVIEW | `test_new_cards_are_due_today` | PASS | — | [test_review_due.py](../../selenium-tests/test_review_due.py) |
| S-047 | HSK-REVIEW | `test_future_cards_excluded_after_reload` | PASS | — | [test_review_future.py](../../selenium-tests/test_review_future.py) |
| S-048 | HSK-REVIEW | `test_rate_review_card[REVIEW-03]` | PASS | — | [test_review_rate.py](../../selenium-tests/test_review_rate.py) |
| S-049 | HSK-REVIEW | `test_rate_review_card[REVIEW-04]` | PASS | — | [test_review_rate.py](../../selenium-tests/test_review_rate.py) |
| S-050 | HSK-REVIEW | `test_review_repeated_card[REVIEW-05]` | PASS | — | [test_review_repeat.py](../../selenium-tests/test_review_repeat.py) |
| S-051 | HSK-REVIEW | `test_review_repeated_card[REVIEW-06]` | PASS | — | [test_review_repeat.py](../../selenium-tests/test_review_repeat.py) |
| S-052 | HSK-REVIEW | `test_review_history_saved_once` | PASS | — | [test_review_history.py](../../selenium-tests/test_review_history.py) |
| S-053 | HSK-PROGRESS | `test_progress_empty_for_new_account` | PASS | — | [test_progress.py](../../selenium-tests/test_progress.py) |
| S-054 | HSK-PROGRESS | `test_progress_with_due_cards` | PASS | — | [test_progress_cards.py](../../selenium-tests/test_progress_cards.py) |
| S-055 | HSK-PROGRESS | `test_progress_after_completing_flashcards` | PASS | — | [test_progress_completed.py](../../selenium-tests/test_progress_completed.py) |
| S-056 | HSK-PROGRESS | `test_stats_empty_for_new_account` | PASS | — | [test_stats.py](../../selenium-tests/test_stats.py) |
| S-057 | HSK-PROGRESS | `test_stats_calendar_and_ranges` | FAIL | HSK-003 | [test_stats_calendar.py](../../selenium-tests/test_stats_calendar.py) |
| S-058 | HSK-PROGRESS | `test_stats_persist_after_reload_and_login` | PASS | — | [test_stats_persistence.py](../../selenium-tests/test_stats_persistence.py) |
| S-059 | HSK-PROGRESS | `test_stats_after_one_review_session` | PASS | — | [test_stats_session.py](../../selenium-tests/test_stats_session.py) |
| S-060 | HSK-PROGRESS | `test_account_data_isolation` | PASS | — | [test_data_isolation.py](../../selenium-tests/test_data_isolation.py) |
| S-061 | HSK-WRITE | `test_open_writing[WRITE-01]` | PASS | — | [test_writing.py](../../selenium-tests/test_writing.py) |
| S-062 | HSK-WRITE | `test_open_writing[WRITE-02]` | PASS | — | [test_writing.py](../../selenium-tests/test_writing.py) |
| S-063 | HSK-WRITE | `test_open_writing[WRITE-03]` | PASS | — | [test_writing.py](../../selenium-tests/test_writing.py) |
| S-064 | HSK-WRITE | `test_open_writing[WRITE-04]` | PASS | — | [test_writing.py](../../selenium-tests/test_writing.py) |
| S-065 | HSK-WRITE | `test_open_writing[WRITE-05]` | PASS | — | [test_writing.py](../../selenium-tests/test_writing.py) |
| S-066 | HSK-WRITE | `test_wrong_stroke_not_completed` | PASS | — | [test_writing_quiz.py](../../selenium-tests/test_writing_quiz.py) |
| S-067 | HSK-WRITE | `test_complete_one_character` | PASS | — | [test_writing_complete.py](../../selenium-tests/test_writing_complete.py) |
| S-068 | HSK-GAME | `test_open_game[GAME-01]` | PASS | — | [test_game.py](../../selenium-tests/test_game.py) |
| S-069 | HSK-GAME | `test_open_game[GAME-02]` | PASS | — | [test_game.py](../../selenium-tests/test_game.py) |
| S-070 | HSK-GAME | `test_open_game[GAME-03]` | PASS | — | [test_game.py](../../selenium-tests/test_game.py) |
| S-071 | HSK-GAME | `test_hanzi_mode_correct_answer` | PASS | — | [test_game_hanzi.py](../../selenium-tests/test_game_hanzi.py) |
| S-072 | HSK-GAME | `test_complete_game_mixed_answers` | PASS | — | [test_game_mixed.py](../../selenium-tests/test_game_mixed.py) |
| S-073 | HSK-GAME | `test_complete_game_all_correct[GAME-04]` | PASS | — | [test_game_complete.py](../../selenium-tests/test_game_complete.py) |
| S-074 | HSK-GAME | `test_complete_game_all_correct[GAME-05]` | PASS | — | [test_game_complete.py](../../selenium-tests/test_game_complete.py) |
| S-075 | HSK-GAME | `test_complete_game_all_correct[GAME-06]` | PASS | — | [test_game_complete.py](../../selenium-tests/test_game_complete.py) |
| S-076 | HSK-NOTE | `test_search[SEARCH-01]` | PASS | — | [test_search.py](../../selenium-tests/test_search.py) |
| S-077 | HSK-NOTE | `test_search[SEARCH-02]` | PASS | — | [test_search.py](../../selenium-tests/test_search.py) |
| S-078 | HSK-NOTE | `test_search[SEARCH-03]` | PASS | — | [test_search.py](../../selenium-tests/test_search.py) |
| S-079 | HSK-NOTE | `test_search[SEARCH-04]` | PASS | — | [test_search.py](../../selenium-tests/test_search.py) |
| S-080 | HSK-NOTE | `test_search[SEARCH-05]` | PASS | — | [test_search.py](../../selenium-tests/test_search.py) |
| S-081 | HSK-NOTE | `test_notebook[NOTE-01]` | PASS | — | [test_notebook.py](../../selenium-tests/test_notebook.py) |
| S-082 | HSK-NOTE | `test_notebook[NOTE-02]` | PASS | — | [test_notebook.py](../../selenium-tests/test_notebook.py) |
| S-083 | HSK-NOTE | `test_notebook[NOTE-03]` | PASS | — | [test_notebook.py](../../selenium-tests/test_notebook.py) |
| S-084 | HSK-NOTE | `test_notebook[NOTE-04]` | FAIL | HSK-004 | [test_notebook.py](../../selenium-tests/test_notebook.py) |
| S-085 | HSK-NOTE | `test_notebook[NOTE-05]` | PASS | — | [test_notebook.py](../../selenium-tests/test_notebook.py) |

## 3. Logic HSK — 22 ca Vitest

Nguồn: [XML UI](../experiments/2026-10-19/vitest-ui.xml), [XML CLI](../experiments/2026-10-19/vitest-cli.xml). Mỗi cách đều 22/22 PASS; 17 ca core và 5 ca gate là các tập con của 22 ca, không cộng lại. HSK-REVIEW gồm 10 ca SM-2; HSK-UNLOCK gồm 7 ca mở khóa và 5 ca ngưỡng/bảo toàn kết quả. Đây không phải kiểm định lại đặc tả SM-2.

| ID gốc | Yêu cầu | Tên ca trong XML | Trạng thái | Nguồn test |
| --- | --- | --- | --- | --- |
| WB-SM2-01 | HSK-REVIEW | SM-2 > WB-SM2-01: tao the moi | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-SM2-02 | HSK-REVIEW | SM-2 > WB-SM2-02: quality 2 dat lai chuoi nho | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-SM2-03 | HSK-REVIEW | SM-2 > WB-SM2-03: quality 3 vao nhanh nho | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-SM2-04 | HSK-REVIEW | SM-2 > WB-SM2-04: lan nho thu hai | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-SM2-05 | HSK-REVIEW | SM-2 > WB-SM2-05: lan ba nhan he so cu | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-SM2-06 | HSK-REVIEW | SM-2 > WB-SM2-06: he so toi thieu | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-SM2-07 | HSK-REVIEW | SM-2 > WB-SM2-07: lam tron khoang on | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-SM2-08 | HSK-REVIEW | SM-2 > WB-SM2-08: chuyen nam | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-SM2-09 | HSK-REVIEW | SM-2 > WB-SM2-09: nam nhuan | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-SM2-10 | HSK-REVIEW | SM-2 > WB-SM2-10: giu nguyen dau vao | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-UNLOCK-01 | HSK-UNLOCK | Mo khoa > WB-UNLOCK-01: bien bai 3 va 4 | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-UNLOCK-02 | HSK-UNLOCK | Mo khoa > WB-UNLOCK-02: nhom dau luon mo | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-UNLOCK-03 | HSK-UNLOCK | Mo khoa > WB-UNLOCK-03: thieu ket qua thi khoa | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-UNLOCK-04 | HSK-UNLOCK | Mo khoa > WB-UNLOCK-04: chua dat thi khoa | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-UNLOCK-05 | HSK-UNLOCK | Mo khoa > WB-UNLOCK-05: dat thi mo | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-UNLOCK-06 | HSK-UNLOCK | Mo khoa > WB-UNLOCK-06: khong lan cap HSK | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-UNLOCK-07 | HSK-UNLOCK | Mo khoa > WB-UNLOCK-07: khong mo vuot nhom | PASS | [core.test.ts](../../hsk-app/frontend/tests/whitebox/core.test.ts) |
| WB-GATE-01 | HSK-UNLOCK | Ngưỡng và bảo toàn kết quả kiểm tra > WB-GATE-01: điểm 79, passed=false | PASS | [gate.test.ts](../../hsk-app/frontend/tests/whitebox/gate.test.ts) |
| WB-GATE-02 | HSK-UNLOCK | Ngưỡng và bảo toàn kết quả kiểm tra > WB-GATE-02: điểm 80, passed=true | PASS | [gate.test.ts](../../hsk-app/frontend/tests/whitebox/gate.test.ts) |
| WB-GATE-03 | HSK-UNLOCK | Ngưỡng và bảo toàn kết quả kiểm tra > WB-GATE-03: điểm 81, passed=true | PASS | [gate.test.ts](../../hsk-app/frontend/tests/whitebox/gate.test.ts) |
| WB-GATE-04 | HSK-UNLOCK | Ngưỡng và bảo toàn kết quả kiểm tra > WB-GATE-04: đạt 80 rồi làm lại 60 vẫn giữ quyền và điểm | PASS | [gate.test.ts](../../hsk-app/frontend/tests/whitebox/gate.test.ts) |
| WB-GATE-05 | HSK-UNLOCK | Ngưỡng và bảo toàn kết quả kiểm tra > WB-GATE-05: từ chưa đạt lên đạt cập nhật điểm và số lần | PASS | [gate.test.ts](../../hsk-app/frontend/tests/whitebox/gate.test.ts) |

## 4. Yêu cầu công cụ và các ca kiểm tra

| Yêu cầu hỗ trợ | Tiêu chí mong đợi trong phạm vi test | Test/minh chứng tương ứng | Kết quả đã lưu |
| --- | --- | --- | --- |
| TOOL-01 | Chỉ chạy nhóm cấu hình sẵn, từ chối ID/lệnh tùy ý | T-RUN-06; lượt UI E-S01/E-S02 trong bảng minh chứng | Test kiểm soát đạt; UI chọn/chạy được |
| TOOL-02 | Chạy tối đa một nhóm, hủy/timeout dừng tiến trình và không báo PASS giả | T-RUN-01,03,04,06; E-F01 | Các ca tương ứng PASS; trạng thái hủy/timeout đúng |
| TOOL-03 | Đọc đúng tên/trạng thái; từ chối XML sai; thiếu XML/exit lỗi không thành PASS | T-XML-01…07, T-RUN-01,02; E-X01; E-S02 | Test đạt; 70/70 XML khớp; 85/85 ca khớp XML |
| TOOL-04 | Chọn/chạy/xem kết quả, nhật ký và mở lại lịch sử; nhập/tải XML qua API local | T-API-01; E-S01/E-S02/E-S03 | API test đạt; luồng UI và mở lại lịch sử hoạt động |
| TOOL-05 | Giữ kết quả sau khi mở store mới, khôi phục lượt bị gián đoạn | T-RUN-01,05; T-API-01; E-S02 | Test đạt; lịch sử 85 ca khớp nguồn |
| TOOL-06 | Không key vẫn chạy test; gọi AI theo yêu cầu, giữ kết quả test và che bí mật thông dụng | T-GEM-01…04; E-A01/E-A03 | Test đạt; HTTP 200 thật; chất lượng lời giải thích chỉ đánh giá sơ bộ |
| TOOL-07 | Từ chối cấu hình thiếu/endpoint website; chỉ dùng môi trường kiểm thử riêng | T-ENV-01…03; E-F01/E-S02 | Test cấu hình đạt; endpoint khác và hash cấu hình gốc giữ nguyên |

Mã TOOL-01…07 xem [yêu cầu trong báo cáo](EXPERIMENT-REPORT.md#2-yêu-cầu-và-thiết-kế). Các dòng dưới là 21 test top-level trong bộ công cụ. PASS được đối chiếu với tên ca và tổng trong nhật ký, không suy từ việc file mã nguồn tồn tại.

| ID truy vết | Yêu cầu | Ca gốc | Kết quả | Nguồn test |
| --- | --- | --- | --- | --- |
| T-GEM-01 | TOOL-06 | thiếu key trả hướng dẫn và không gọi mạng | PASS | [gemini.test.ts](../tests/gemini.test.ts) |
| T-GEM-02 | TOOL-06 | chỉ gửi ngữ cảnh lỗi và lưu phản hồi phân tích, không sửa trạng thái | PASS | [gemini.test.ts](../tests/gemini.test.ts) |
| T-GEM-03 | TOOL-06 | lỗi hạn mức được giải thích mà không trả nội dung API có thể chứa key | PASS | [gemini.test.ts](../tests/gemini.test.ts) |
| T-GEM-04 | TOOL-06 | ẩn bí mật thông dụng và giới hạn phần cuối nhật ký gửi tới Gemini | PASS | [gemini.test.ts](../tests/gemini.test.ts) |
| T-ENV-01 | TOOL-07 | môi trường HSK kiểm thử cần đủ cấu hình, không tự dùng database hiện tại | PASS | [hsk-test-environment.test.ts](../tests/hsk-test-environment.test.ts) |
| T-ENV-02 | TOOL-07 | từ chối cùng endpoint hiện tại dù khác role, database, hoặc dùng pooler | PASS | [hsk-test-environment.test.ts](../tests/hsk-test-environment.test.ts) |
| T-ENV-03 | TOOL-07 | chấp nhận endpoint Neon khác, kiểm tra host và SSL, không sửa môi trường tiến trình | PASS | [hsk-test-environment.test.ts](../tests/hsk-test-environment.test.ts) |
| T-XML-01 | TOOL-03 | đọc JUnit của Vitest: tên, thời gian và ký tự XML | PASS | [junit.test.ts](../tests/junit.test.ts) |
| T-XML-02 | TOOL-03 | đọc pytest: failure, error thu thập, skipped và CDATA | PASS | [junit.test.ts](../tests/junit.test.ts) |
| T-XML-03 | TOOL-03 | hỗ trợ root testsuite và suite lồng nhau, không đếm trùng | PASS | [junit.test.ts](../tests/junit.test.ts) |
| T-XML-04 | TOOL-03 | không báo PASS khi thiếu testcase, XML rỗng test, hoặc exit code khác 0 | PASS | [junit.test.ts](../tests/junit.test.ts) |
| T-XML-05 | TOOL-03 | không làm mất trạng thái FAIL khi có test thất bại | PASS | [junit.test.ts](../tests/junit.test.ts) |
| T-XML-06 | TOOL-03 | không bỏ qua lỗi tổng hợp của suite con trong pytest XML | PASS | [junit.test.ts](../tests/junit.test.ts) |
| T-XML-07 | TOOL-03 | từ chối XML hỏng, báo cáo sai định dạng và khai báo entity | PASS | [junit.test.ts](../tests/junit.test.ts) |
| T-RUN-01 | TOOL-02, TOOL-03, TOOL-05 | chạy tiến trình thật, đọc XML và giữ lịch sử sau khi mở store mới | PASS | [runner.test.ts](../tests/runner.test.ts) |
| T-RUN-02 | TOOL-03 | thoát 0 nhưng không có XML vẫn là lỗi thực thi | PASS | [runner.test.ts](../tests/runner.test.ts) |
| T-RUN-03 | TOOL-02 | giới hạn một lần chạy và dừng được tiến trình đang chạy | PASS | [runner.test.ts](../tests/runner.test.ts) |
| T-RUN-04 | TOOL-02 | hết thời gian dừng tiến trình và không ghi PASS | PASS | [runner.test.ts](../tests/runner.test.ts) |
| T-RUN-05 | TOOL-05 | khôi phục lần chạy bị gián đoạn khi khởi động lại | PASS | [runner.test.ts](../tests/runner.test.ts) |
| T-RUN-06 | TOOL-01, TOOL-02 | không thực thi nhóm tùy ý hoặc thời gian không hợp lệ | PASS | [runner.test.ts](../tests/runner.test.ts) |
| T-API-01 | TOOL-04, TOOL-05 | API local: nhập XML, xem chi tiết, tải lại XML, lịch sử và lỗi đầu vào | PASS | [server.test.ts](../tests/server.test.ts) |

Minh chứng bổ sung cho TOOL-01/02/04/05: [chạy nhóm nhỏ qua UI](../experiments/2026-10-19/selenium-notebook-122623/summary.json), [lịch sử 85 ca khớp XML](../experiments/2026-10-19/selenium-dom-verification.json), [ảnh lịch sử](../experiments/2026-10-19/selenium-history-result.png), [hủy/timeout/XML hỏng/kết nối lỗi](../experiments/2026-10-19/fault-scenarios.json). TOOL-06 còn có [Gemini thật HTTP 200](../experiments/2026-10-19/selenium-gemini-analysis.json); TOOL-07 có [chặn môi trường chưa cấu hình](../experiments/2026-10-19/ui-guard.json) và [hash cấu hình giữ nguyên](../experiments/2026-10-19/verification-final.json). Các minh chứng này không được tính thêm thành test top-level.

## 5. Giới hạn sử dụng bảng

Các yêu cầu ngoài bộ ca hiện có chưa được truy vết thành PASS. Những phần chưa kiểm thử và kết luận theo tiêu chí xem [mục 8 báo cáo](EXPERIMENT-REPORT.md#8-kết-luận-chất-lượng-theo-tiêu-chí-và-phạm-vi-chưa-kiểm-thử). Bảng không chứng minh code coverage, bảo mật toàn hệ thống, chất lượng nội dung học tập, hiệu năng hoặc hiệu quả thao tác người dùng.
