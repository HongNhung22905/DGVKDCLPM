import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    "case_id", ["REVIEW-03", "REVIEW-04"]
)
def test_rate_review_card(case_id):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    base_url = "http://localhost:3000"
    email = f"review.rate.{uuid.uuid4().hex[:12]}@example.com"

    def visible_text(tag, text):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
            ))
        )

    def click_button(label):
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f'//button[normalize-space(.)="{label}"]',
            ))
        ).click()

    try:
        # Chuẩn bị tài khoản mới.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Đánh giá ôn tập")

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]',
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        # Lấy tập từ để đối chiếu thẻ ôn.
        driver.get(
            f"{base_url}/vocabulary/lesson/new-1-lesson-1"
        )

        words = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR,
                "span.hanzi.text-2xl.font-bold",
            ))
        )

        assert len(words) == 20
        lesson_words = {word.text.strip() for word in words}

        # Khởi tạo 20 thẻ mới, chưa đánh giá.
        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'a[href="/vocabulary/flashcard/new-1-lesson-1"]',
            ))
        ).click()

        visible_text("span", "1/20")

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Lật thẻ"]',
            ))
        )

        driver.get(f"{base_url}/review")

        visible_text("span", "0%")
        visible_text("span", "0/20 từ")
        visible_text("span", "20 còn lại")
        visible_text("span", "✓ 0 đúng")
        visible_text("span", "✗ 0 cần ôn lại")

        first_word = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-4",
            ))
        ).text.strip()

        assert first_word in lesson_words

        click_button("Lật thẻ")

        rating_label = (
            "Đã thuộc"
            if case_id == "REVIEW-03"
            else "Chưa thuộc"
        )

        rating_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f'//button[.//p[normalize-space(.)="{rating_label}"]]',
            ))
        )

        driver.save_screenshot(f"{case_id}-before-rate.png")
        rating_button.click()

        # Tiến độ đếm số từ gốc đã đánh giá, kể cả đánh giá chưa thuộc.
        visible_text("span", "5%")
        visible_text("span", "1/20 từ")
        visible_text("span", "19 còn lại")

        expected_correct = 1 if case_id == "REVIEW-03" else 0
        expected_wrong = 0 if case_id == "REVIEW-03" else 1

        visible_text("span", f"✓ {expected_correct} đúng")
        visible_text("span", f"✗ {expected_wrong} cần ôn lại")

        wait.until(
            lambda browser: browser.find_element(
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-4",
            ).text.strip() != first_word
        )

        next_word = driver.find_element(
            By.CSS_SELECTOR,
            "p.hanzi.font-bold.mb-4",
        ).text.strip()

        assert next_word in lesson_words

        # Thẻ tiếp theo trở về mặt trước.
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Lật thẻ"]',
            ))
        )

        wait.until(
            lambda browser: browser.find_elements(
                By.CSS_SELECTOR,
                'div[style*="preserve-3d"][style*="rotateY(0deg)"]',
            )
        )

        for label in ("Chưa thuộc", "Đã thuộc"):
            assert not driver.find_elements(
                By.XPATH,
                f'//button[.//p[normalize-space(.)="{label}"]]',
            )

        assert not driver.find_elements(
            By.XPATH,
            '//h2[normalize-space(.)="Ôn tập xong!"]',
        )

        driver.save_screenshot(f"{case_id}-pass.png")

        print(
            f"\n{case_id}: {rating_label} thẻ {first_word}; "
            f"chuyển sang {next_word}, trở về mặt trước; "
            "tiến độ 5%, 1/20 từ, còn 19; "
            f"đúng = {expected_correct}, "
            f"cần ôn lại = {expected_wrong}"
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