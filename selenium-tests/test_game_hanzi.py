import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_hanzi_mode_correct_answer():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    case_id = "GAME-07"
    lesson_id = "new-1-lesson-1"
    email = f"game.hanzi.{uuid.uuid4().hex[:12]}@example.com"
    option_selector = "button.w-full.text-left"

    try:
        # Chuẩn bị tài khoản mới.
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Kiểm thử Game Chữ Hán")

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

        # Lấy chữ Hán, nghĩa và Pinyin từ bài học.
        driver.get(
            f"http://localhost:3000/vocabulary/lesson/{lesson_id}"
        )

        words = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR,
                "span.hanzi.text-2xl.font-bold"
            ))
        )
        assert len(words) == 20

        lesson_words = []

        for word in words:
            row = word.find_element(
                By.XPATH,
                './ancestor::div[contains(@class,"cursor-pointer")][1]'
            )

            item = {
                "hanzi": word.text.strip(),
                "meaning": row.find_element(
                    By.CSS_SELECTOR, "p.line-clamp-1"
                ).text.strip(),
                "pinyin": row.find_element(
                    By.CSS_SELECTOR, "p.font-medium"
                ).text.strip(),
            }

            assert all(item.values())
            lesson_words.append(item)

        # Mở game và chọn Chữ Hán.
        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'a[href="/vocabulary/game/{lesson_id}"]'
            ))
        ).click()

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[.//p[normalize-space(.)="Chữ Hán"]]'
            ))
        ).click()

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//span[normalize-space(.)="Câu 1/20"]'
            ))
        )

        assert driver.find_element(
            By.XPATH,
            '//span[normalize-space(.)="Chữ Hán"]'
        ).is_displayed()

        prompt = wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//p[normalize-space(.)="Chữ Hán nào có nghĩa là:"]'
            ))
        )
        question_panel = prompt.find_element(By.XPATH, "..")

        meaning = question_panel.find_element(
            By.CSS_SELECTOR, "p.text-xl.font-semibold"
        ).text.strip()

        pinyin = question_panel.find_element(
            By.CSS_SELECTOR, "p.text-sm.mt-1"
        ).text.strip()

        # Xác định đáp án từ nghĩa và Pinyin hiển thị.
        matches = [
            item
            for item in lesson_words
            if item["meaning"] == meaning
            and item["pinyin"] == pinyin
        ]
        assert len(matches) == 1, (
            f"Không xác định duy nhất câu hỏi: "
            f"nghĩa={meaning!r}, Pinyin={pinyin!r}"
        )

        expected_hanzi = matches[0]["hanzi"]

        options = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR, option_selector
            ))
        )

        assert len(options) == 4
        assert all(option.is_enabled() for option in options)

        valid_hanzi = {item["hanzi"] for item in lesson_words}
        option_texts = [option.text.strip() for option in options]

        assert all(text in valid_hanzi for text in option_texts)
        assert all(
            option.find_elements(By.CSS_SELECTOR, "span.hanzi.text-2xl")
            for option in options
        )

        correct_options = [
            option
            for option in options
            if option.text.strip() == expected_hanzi
        ]
        assert len(correct_options) == 1

        for counter in ("✓ 0", "✗ 0"):
            assert driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="{counter}"]'
            ).is_displayed()

        driver.save_screenshot("GAME-07-before-answer.png")

        correct_option = correct_options[0]
        correct_option.click()

        # Kiểm tra phản hồi trước khi tự chuyển câu.
        def correct_feedback(browser):
            current_options = browser.find_elements(
                By.CSS_SELECTOR, option_selector
            )
            return (
                len(current_options) == 4
                and all(
                    not option.is_enabled()
                    for option in current_options
                )
                and correct_option.value_of_css_property(
                    "background-color"
                ) == "rgba(220, 252, 231, 1)"
                and browser.find_elements(
                    By.XPATH,
                    '//span[normalize-space(.)="✓ 1"]'
                )
                and browser.find_elements(
                    By.XPATH,
                    '//span[normalize-space(.)="✗ 0"]'
                )
            )

        WebDriverWait(
            driver, 5, poll_frequency=0.05
        ).until(correct_feedback)

        driver.save_screenshot("GAME-07-correct-feedback.png")

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//span[normalize-space(.)="Câu 2/20"]'
            ))
        )

        def next_question_ready(browser):
            current_options = browser.find_elements(
                By.CSS_SELECTOR, option_selector
            )
            return (
                len(current_options) == 4
                and all(
                    option.is_displayed() and option.is_enabled()
                    for option in current_options
                )
            )

        wait.until(next_question_ready)

        for counter in ("✓ 1", "✗ 0"):
            assert driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="{counter}"]'
            ).is_displayed()

        assert driver.find_element(
            By.XPATH,
            '//span[normalize-space(.)="Chữ Hán"]'
        ).is_displayed()

        driver.save_screenshot(f"{case_id}-pass.png")
        print(
            f"\n{case_id}: câu hỏi có nghĩa và Pinyin khớp bài; "
            f"4 lựa chọn Chữ Hán; chọn đúng {expected_hanzi}; "
            "phản hồi xanh, khóa lựa chọn; "
            "chuyển Câu 2/20, đúng = 1, sai = 0"
        )

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