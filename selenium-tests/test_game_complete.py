import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    "case_id", ["GAME-04", "GAME-05", "GAME-06"]
)
def test_complete_game_all_correct(case_id):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    lesson_id = "new-1-lesson-1"
    email = f"game.complete.{uuid.uuid4().hex[:12]}@example.com"
    option_selector = "button.w-full.text-left"

    try:
        # Chuẩn bị tài khoản mới.
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Kiểm thử Hoàn thành Game")

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        # Lấy nghĩa và Pinyin từ bài học để đối chiếu.
        driver.get(
            f"http://localhost:3000/vocabulary/lesson/{lesson_id}"
        )

        words = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR,
                "span.hanzi.text-2xl.font-bold"
            ))
        )

        total_words = len(words)
        assert total_words == 20

        lesson_words = {}

        for word in words:
            row = word.find_element(
                By.XPATH,
                './ancestor::div[contains(@class,"cursor-pointer")][1]'
            )

            character = word.text.strip()
            meaning = row.find_element(
                By.CSS_SELECTOR, "p.line-clamp-1"
            ).text.strip()
            pinyin = row.find_element(
                By.CSS_SELECTOR, "p.font-medium"
            ).text.strip()

            assert character
            assert meaning
            assert pinyin
            assert character not in lesson_words, (
                f"Chữ Hán trùng trong dữ liệu đối chiếu: {character}"
            )

            lesson_words[character] = {
                "meaning": meaning,
                "pinyin": pinyin,
            }

        lesson_title = driver.find_element(
            By.TAG_NAME, "h1"
        ).text.strip()

        def click_button(label):
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f'//button[normalize-space(.)="{label}"]'
                ))
            ).click()

        def select_mode(label):
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f'//button[.//p[normalize-space(.)="{label}"]]'
                ))
            ).click()

        def options_ready(browser):
            options = browser.find_elements(
                By.CSS_SELECTOR, option_selector
            )

            if (
                len(options) == 4
                and all(
                    option.is_displayed() and option.is_enabled()
                    for option in options
                )
            ):
                return options

            return False

        def check_counters(correct, wrong):
            assert driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="✓ {correct}"]'
            ).is_displayed()

            assert driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="✗ {wrong}"]'
            ).is_displayed()

        # Mở game, hoàn thành lượt Nghĩa từ.
        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'a[href="/vocabulary/game/{lesson_id}"]'
            ))
        ).click()

        select_mode("Nghĩa từ")
        seen_questions = set()

        for position in range(1, total_words + 1):
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//span[normalize-space(.)="Câu {position}/{total_words}"]'
                ))
            )

            options = wait.until(options_ready)

            question = driver.find_element(
                By.CSS_SELECTOR, "p.hanzi.font-bold.mb-3"
            ).text.strip()

            assert question in lesson_words
            assert question not in seen_questions, (
                f"Câu hỏi bị lặp: {question}"
            )
            seen_questions.add(question)

            expected_answer = lesson_words[question]["meaning"]
            correct_options = [
                option
                for option in options
                if option.text.strip() == expected_answer
            ]

            assert len(correct_options) == 1, (
                f"Câu {position}, từ {question}: "
                f"có {len(correct_options)} lựa chọn khớp nghĩa."
            )

            correct_options[0].click()
            print(
                f"Câu {position}/{total_words}: "
                f"chọn đúng nghĩa của {question}"
            )

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Chơi lại"]'
            ))
        )

        result_heading = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h2"))
        )
        assert result_heading.text.startswith("Xuất sắc!")

        result_panel = result_heading.find_element(By.XPATH, "..")

        assert result_panel.find_element(
            By.CSS_SELECTOR, "p.text-sm.mb-6"
        ).text.strip() == f"{lesson_title} · Nghĩa từ"

        def get_stat(label):
            return result_panel.find_element(
                By.XPATH,
                f'.//p[normalize-space(.)="{label}"]/../p[1]'
            ).text.strip()

        assert get_stat("Điểm") == "100%"
        assert get_stat(f"Đúng/{total_words}") == "20"
        assert get_stat("Sai") == "0"

        time_text = get_stat("Thời gian")
        assert time_text.endswith("s"), time_text
        assert time_text[:-1].isdigit(), time_text

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Đổi chế độ"]'
            ))
        )

        assert seen_questions == set(lesson_words)
        assert not driver.find_elements(
            By.CSS_SELECTOR, option_selector
        )

        if case_id in ("GAME-05", "GAME-06"):
            if case_id == "GAME-05":
                driver.save_screenshot("GAME-05-before-restart.png")
                click_button("Chơi lại")
                mode = "Nghĩa từ"
                prompt = "Nghĩa của từ này là gì?"
                answer_key = "meaning"

            else:
                # Trở về màn hình chọn chế độ.
                click_button("Đổi chế độ")

                heading = wait.until(
                    EC.visibility_of_element_located((By.TAG_NAME, "h1"))
                )
                assert heading.text.strip() == (
                    f"Game từ vựng · {lesson_title}"
                )

                for label in ("Nghĩa từ", "Pinyin", "Chữ Hán"):
                    wait.until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            f'//button[.//p[normalize-space(.)="{label}"]]'
                        ))
                    )

                assert not driver.find_elements(
                    By.CSS_SELECTOR, option_selector
                )

                driver.save_screenshot("GAME-06-mode-select.png")

                select_mode("Pinyin")
                mode = "Pinyin"
                prompt = "Pinyin của từ này là gì?"
                answer_key = "pinyin"

            # Lượt mới phải đặt lại câu và bộ đếm.
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//span[normalize-space(.)="Câu 1/{total_words}"]'
                ))
            )

            options = wait.until(options_ready)
            check_counters(0, 0)

            assert driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="{mode}"]'
            ).is_displayed()

            assert driver.find_element(
                By.XPATH,
                f'//p[normalize-space(.)="{prompt}"]'
            ).is_displayed()

            new_question = driver.find_element(
                By.CSS_SELECTOR, "p.hanzi.font-bold.mb-3"
            ).text.strip()
            assert new_question in lesson_words

            option_texts = [
                option.text.strip() for option in options
            ]
            assert all(option_texts)
            assert lesson_words[new_question][answer_key] in option_texts

            if case_id == "GAME-06":
                # Mỗi lựa chọn phải hiển thị bằng nhãn Pinyin.
                assert all(
                    option.find_elements(
                        By.CSS_SELECTOR, "span.font-mono"
                    )
                    for option in options
                )

                valid_pinyin = {
                    item["pinyin"] for item in lesson_words.values()
                }
                assert all(
                    text in valid_pinyin for text in option_texts
                ), "Có lựa chọn Pinyin không thuộc bài học."

            assert not driver.find_elements(
                By.XPATH,
                '//button[normalize-space(.)="Chơi lại"]'
            ), "Màn hình kết quả chưa đóng."

            if case_id == "GAME-05":
                message = (
                    "Chơi lại bắt đầu Câu 1/20; "
                    "giữ chế độ Nghĩa từ; đúng = 0, sai = 0; "
                    "4 lựa chọn được mở và có đáp án đúng"
                )
            else:
                message = (
                    "Đổi chế độ trở về đủ 3 chế độ; "
                    "chọn Pinyin bắt đầu Câu 1/20; "
                    "câu hỏi và 4 lựa chọn đúng dạng Pinyin; "
                    "có đáp án khớp bài; đúng = 0, sai = 0"
                )

        else:
            message = (
                f"hoàn thành {total_words} câu không lặp; "
                "Điểm = 100%, Đúng/20 = 20, Sai = 0; "
                "hiển thị Xuất sắc, thời gian, Chơi lại và Đổi chế độ"
            )

        driver.save_screenshot(f"{case_id}-pass.png")
        print(f"\n{case_id}: {message}")

    except Exception:
        try:
            driver.save_screenshot(f"{case_id}-fail.png")
        except Exception as error:
            print(f"\nKhông chụp được ảnh: {error}")
        raise

    finally:
        try:
            driver.quit()
        except Exception:
            pass