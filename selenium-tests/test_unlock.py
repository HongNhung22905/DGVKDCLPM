import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_start_first_group_test():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    case_id = "UNLOCK-01"
    email = f"unlock.{uuid.uuid4().hex[:12]}@example.com"
    set_id = "new-1-set-1"

    try:
        # Chuẩn bị tài khoản mới chưa có tiến độ.
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Kiểm thử Mở khóa")

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

        # Lấy dữ liệu 3 bài của nhóm 1 để đối chiếu.
        lesson_titles = []
        pool_meanings = {}
        total_words = 0

        for lesson_number in range(1, 4):
            driver.get(
                "http://localhost:3000/vocabulary/lesson/"
                f"new-1-lesson-{lesson_number}"
            )

            words = wait.until(
                EC.visibility_of_all_elements_located((
                    By.CSS_SELECTOR,
                    "span.hanzi.text-2xl.font-bold"
                ))
            )

            lesson_titles.append(
                driver.find_element(By.TAG_NAME, "h1").text.strip()
            )
            total_words += len(words)

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
                pool_meanings.setdefault(character, set()).add(meaning)

        # Trở lại danh sách và chọn HSK 1.
        driver.get("http://localhost:3000/vocabulary")

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[.//p[normalize-space(.)="HSK 1"]]'
            ))
        ).click()

        # Nhóm 1 cho phép truy cập kiểm tra với tài khoản mới.
        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'a[href="/vocabulary/test/{set_id}"]'
            ))
        ).click()

        wait.until(
            EC.url_contains(f"/vocabulary/test/{set_id}")
        )

        heading = wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//h2[normalize-space(.)="Bài kiểm tra nhóm 1"]'
            ))
        )

        intro_card = heading.find_element(
            By.XPATH,
            './ancestor::div[contains(@class,"max-w-md")][1]'
        )

        assert intro_card.find_element(
            By.XPATH,
            './/p[normalize-space(.)="HSK 1 · Bài 1–3"]'
        ).is_displayed()

        # Intro phải liệt kê đủ ba bài của nhóm.
        displayed_titles = [
            element.text.strip()
            for element in intro_card.find_elements(By.TAG_NAME, "span")
        ]
        for title in lesson_titles:
            assert title in displayed_titles, (
                f"Thiếu bài trong phần giới thiệu: {title}"
            )

        def get_intro_stat(label):
            return intro_card.find_element(
                By.XPATH,
                f'.//span[normalize-space(.)="{label}"]/../span[1]'
            ).text.strip()

        assert get_intro_stat("Từ vựng") == str(total_words)
        assert get_intro_stat("Câu hỏi") == "20"
        assert get_intro_stat("Điểm qua") == "80%"

        for description in (
            "Nhìn chữ → chọn nghĩa",
            "Nhìn nghĩa → chọn chữ Hán",
            "Điền Pinyin (Levenshtein ±1)",
        ):
            assert intro_card.find_element(
                By.XPATH,
                f'.//span[normalize-space(.)="{description}"]'
            ).is_displayed()

        driver.save_screenshot("UNLOCK-01-intro.png")

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Bắt đầu kiểm tra"]'
            ))
        ).click()

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//span[normalize-space(.)="1/20"]'
            ))
        )

        for text in (
            "HSK 1 · Nhóm 1",
            "Chọn nghĩa đúng",
            "Cần ≥80% để qua",
        ):
            assert driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="{text}"]'
            ).is_displayed()

        question = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-3"
            ))
        ).text.strip()

        assert question in pool_meanings, (
            f"Câu hỏi không thuộc ba bài của nhóm 1: {question}"
        )

        options = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR,
                "button.w-full.text-left"
            ))
        )

        assert len(options) == 4
        assert all(option.is_enabled() for option in options)

        option_texts = {option.text.strip() for option in options}
        assert all(option_texts)
        assert pool_meanings[question] & option_texts, (
            "Các lựa chọn không có nghĩa khớp từ đang hỏi."
        )

        driver.save_screenshot(f"{case_id}-pass.png")
        print(
            f"\n{case_id}: tài khoản mới mở kiểm tra nhóm 1; "
            f"intro đủ 3 bài, {total_words} từ, 20 câu, ngưỡng 80%; "
            f"bắt đầu 1/20, câu hỏi {question} thuộc nhóm; "
            "4 lựa chọn có nghĩa khớp bài"
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