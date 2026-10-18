import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_complete_game_mixed_answers():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    case_id = "GAME-08"
    lesson_id = "new-1-lesson-1"
    email = f"game.mixed.{uuid.uuid4().hex[:12]}@example.com"

    option_selector = "button.w-full.text-left"
    target_correct = 12
    target_wrong = 8

    try:
        # Chuẩn bị tài khoản mới.
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Kiểm thử Game Đúng Sai")

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

        # Lấy dữ liệu bài học để chọn đáp án đúng/sai theo nội dung.
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
        assert target_correct + target_wrong == total_words

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

            assert character
            assert meaning
            assert character not in lesson_words

            lesson_words[character] = meaning

        lesson_title = driver.find_element(
            By.TAG_NAME, "h1"
        ).text.strip()

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'a[href="/vocabulary/game/{lesson_id}"]'
            ))
        ).click()

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[.//p[normalize-space(.)="Nghĩa từ"]]'
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

        seen_questions = set()
        expected_correct = 0
        expected_wrong = 0

        for position in range(1, total_words + 1):
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//span[normalize-space(.)="Câu {position}/{total_words}"]'
                ))
            )

            options = wait.until(options_ready)

            # Bộ đếm trước mỗi câu phải khớp các câu đã trả lời.
            assert driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="✓ {expected_correct}"]'
            ).is_displayed()

            assert driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="✗ {expected_wrong}"]'
            ).is_displayed()

            question = driver.find_element(
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-3"
            ).text.strip()

            assert question in lesson_words
            assert question not in seen_questions, (
                f"Câu hỏi bị lặp: {question}"
            )
            seen_questions.add(question)

            expected_answer = lesson_words[question]

            correct_options = [
                option
                for option in options
                if option.text.strip() == expected_answer
            ]
            assert len(correct_options) == 1, (
                f"Câu {position}: không xác định duy nhất đáp án đúng."
            )

            # 12 câu đầu chọn đúng, 8 câu cuối chọn sai.
            if position <= target_correct:
                selected_option = correct_options[0]
                expected_correct += 1
                answer_type = "đúng"

            else:
                wrong_options = [
                    option
                    for option in options
                    if option.text.strip() != expected_answer
                ]
                assert wrong_options

                selected_option = wrong_options[0]
                expected_wrong += 1
                answer_type = "sai"

            selected_option.click()

            print(
                f"Câu {position}/{total_words}: "
                f"chọn {answer_type} cho {question}"
            )

        # Chờ kết thúc phản hồi câu cuối.
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Chơi lại"]'
            ))
        )

        result_heading = wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "h2"))
        )

        assert result_heading.text.startswith("Khá"), (
            result_heading.text
        )

        result_panel = result_heading.find_element(By.XPATH, "..")

        assert result_panel.find_element(
            By.CSS_SELECTOR, "p.text-sm.mb-6"
        ).text.strip() == f"{lesson_title} · Nghĩa từ"

        def get_stat(label):
            return result_panel.find_element(
                By.XPATH,
                f'.//p[normalize-space(.)="{label}"]/../p[1]'
            ).text.strip()

        assert get_stat("Điểm") == "60%", (
            f"Điểm thực tế: {get_stat('Điểm')}"
        )
        assert get_stat("Đúng/20") == "12"
        assert get_stat("Sai") == "8"

        assert (
            int(get_stat("Đúng/20")) + int(get_stat("Sai"))
            == total_words
        )

        time_text = get_stat("Thời gian")
        assert time_text.endswith("s")
        assert time_text[:-1].isdigit()

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

        driver.save_screenshot(f"{case_id}-pass.png")

        print(
            f"\n{case_id}: hoàn thành 20 câu không lặp; "
            "12 đúng, 8 sai; Điểm = 60%; xếp loại Khá; "
            "tổng đúng + sai = 20"
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