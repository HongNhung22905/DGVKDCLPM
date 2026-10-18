import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    "case_id", ["GAME-01", "GAME-02", "GAME-03"]
)
def test_open_game(case_id):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    lesson_id = "new-1-lesson-1"
    email = f"game.{uuid.uuid4().hex[:12]}@example.com"
    option_selector = "button.w-full.text-left"

    try:
        # Chuẩn bị tài khoản mới.
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Kiểm thử Game")

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

        # Lấy dữ liệu bài học để đối chiếu đáp án.
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
                By.CSS_SELECTOR,
                "p.line-clamp-1"
            ).text.strip()

            assert character
            assert meaning
            lesson_words[character] = meaning

        lesson_title = driver.find_element(
            By.TAG_NAME, "h1"
        ).text.strip()

        # Mở Game từ chi tiết bài học.
        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'a[href="/vocabulary/game/{lesson_id}"]'
            ))
        ).click()

        wait.until(
            EC.url_contains(f"/vocabulary/game/{lesson_id}")
        )

        heading = wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )

        assert heading.text.strip() == (
            f"Game từ vựng · {lesson_title}"
        ), heading.text

        for label in ("Nghĩa từ", "Pinyin", "Chữ Hán"):
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f'//button[.//p[normalize-space(.)="{label}"]]'
                ))
            )

        assert driver.find_element(
            By.XPATH,
            f'//p[normalize-space(.)="{total_words} câu hỏi · 4 lựa chọn"]'
        ).is_displayed()

        if case_id == "GAME-01":
            driver.save_screenshot("GAME-01-mode-select.png")

        # Bắt đầu chế độ Nghĩa từ.
        driver.find_element(
            By.XPATH,
            '//button[.//p[normalize-space(.)="Nghĩa từ"]]'
        ).click()

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//span[normalize-space(.)="Câu 1/{total_words}"]'
            ))
        )

        assert driver.find_element(
            By.XPATH,
            '//span[normalize-space(.)="Nghĩa từ"]'
        ).is_displayed()

        assert driver.find_element(
            By.XPATH,
            '//p[normalize-space(.)="Nghĩa của từ này là gì?"]'
        ).is_displayed()

        question = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-3"
            ))
        ).text.strip()

        # Câu hỏi được xáo trộn, không giả định thứ tự cố định.
        assert question in lesson_words, (
            f"Câu hỏi không thuộc bài học: {question}"
        )

        options = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR,
                option_selector
            ))
        )

        assert len(options) == 4
        assert all(option.is_enabled() for option in options)
        assert all(option.text.strip() for option in options)

        expected_answer = lesson_words[question]

        matching_options = [
            option
            for option in options
            if option.text.strip() == expected_answer
        ]

        assert matching_options, (
            f"Không có nghĩa đúng của {question} trong lựa chọn."
        )

        def check_counters(correct, wrong):
            assert driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="✓ {correct}"]'
            ).is_displayed()

            assert driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="✗ {wrong}"]'
            ).is_displayed()

        check_counters(0, 0)

        if case_id in ("GAME-02", "GAME-03"):
            assert len(matching_options) == 1, (
                "Có nhiều lựa chọn cùng nghĩa; cần kiểm tra dữ liệu "
                "trước khi xác định đáp án theo nội dung hiển thị."
            )

            correct_option = matching_options[0]

            if case_id == "GAME-02":
                selected_option = correct_option
                expected_correct = 1
                expected_wrong = 0
            else:
                wrong_options = [
                    option
                    for option in options
                    if option.text.strip() != expected_answer
                ]
                assert wrong_options, "Không tìm thấy lựa chọn sai."

                selected_option = wrong_options[0]
                expected_correct = 0
                expected_wrong = 1

            selected_option.click()

            # Phản hồi tồn tại khoảng 1 giây trước khi chuyển câu.
            feedback_wait = WebDriverWait(
                driver, 5, poll_frequency=0.05
            )

            def feedback_ready(browser):
                current_options = browser.find_elements(
                    By.CSS_SELECTOR, option_selector
                )

                locked = (
                    len(current_options) == 4
                    and all(
                        not option.is_enabled()
                        for option in current_options
                    )
                )

                counters_ready = (
                    browser.find_elements(
                        By.XPATH,
                        f'//span[normalize-space(.)="✓ {expected_correct}"]'
                    )
                    and browser.find_elements(
                        By.XPATH,
                        f'//span[normalize-space(.)="✗ {expected_wrong}"]'
                    )
                )

                if case_id == "GAME-02":
                    colors_ready = (
                        selected_option.value_of_css_property(
                            "background-color"
                        ) == "rgba(220, 252, 231, 1)"
                    )
                else:
                    colors_ready = (
                        selected_option.value_of_css_property(
                            "background-color"
                        ) == "rgba(254, 226, 226, 1)"
                        and correct_option.value_of_css_property(
                            "background-color"
                        ) == "rgba(254, 249, 195, 1)"
                    )

                return locked and counters_ready and colors_ready

            feedback_wait.until(feedback_ready)

            suffix = (
                "correct-feedback"
                if case_id == "GAME-02"
                else "wrong-feedback"
            )
            driver.save_screenshot(f"{case_id}-{suffix}.png")

            # Tự chuyển sang câu thứ hai.
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//span[normalize-space(.)="Câu 2/{total_words}"]'
                ))
            )

            def next_question_ready(browser):
                current_options = browser.find_elements(
                    By.CSS_SELECTOR, option_selector
                )

                return (
                    len(current_options) == 4
                    and all(
                        option.is_enabled()
                        for option in current_options
                    )
                )

            wait.until(next_question_ready)

            second_question = driver.find_element(
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-3"
            ).text.strip()

            assert second_question in lesson_words
            assert second_question != question

            check_counters(expected_correct, expected_wrong)

            if case_id == "GAME-02":
                message = (
                    f"chọn đúng nghĩa của {question}; "
                    "đáp án phản hồi màu xanh; khóa 4 lựa chọn; "
                    f"tự chuyển Câu 2/{total_words}; "
                    "đúng = 1, sai = 0; mở lại lựa chọn"
                )
            else:
                message = (
                    f"chọn sai nghĩa của {question}; "
                    "lựa chọn sai màu đỏ, đáp án đúng màu vàng; "
                    "khóa 4 lựa chọn; "
                    f"tự chuyển Câu 2/{total_words}; "
                    "đúng = 0, sai = 1; mở lại lựa chọn"
                )

        else:
            message = (
                f"đủ 3 chế độ; mở Nghĩa từ; Câu 1/{total_words}; "
                f"câu hỏi {question} thuộc bài; "
                "4 lựa chọn có nghĩa đúng; đúng/sai đều bằng 0"
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