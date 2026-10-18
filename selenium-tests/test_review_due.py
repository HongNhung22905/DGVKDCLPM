import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_new_cards_are_due_today():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    case_id = "REVIEW-02"
    base_url = "http://localhost:3000"
    lesson_id = "new-1-lesson-1"
    email = f"review.due.{uuid.uuid4().hex[:12]}@example.com"

    def visible_text(tag, text):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
            ))
        )

    try:
        # Chuẩn bị tài khoản mới.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Thẻ đến hạn")

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

        # Lấy nội dung bài học làm dữ liệu đối chiếu.
        driver.get(
            f"{base_url}/vocabulary/lesson/{lesson_id}"
        )

        words = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR,
                "span.hanzi.text-2xl.font-bold",
            ))
        )

        assert len(words) == 20
        lesson_words = {}

        for word in words:
            row = word.find_element(
                By.XPATH,
                './ancestor::div[contains(@class,"cursor-pointer")][1]',
            )

            character = word.text.strip()
            pinyin = row.find_element(
                By.CSS_SELECTOR, "p.font-medium"
            ).text.strip()
            meaning = row.find_element(
                By.CSS_SELECTOR, "p.line-clamp-1"
            ).text.strip()

            assert character
            assert pinyin
            assert meaning

            lesson_words[character] = {
                "pinyin": pinyin,
                "meaning": meaning,
            }

        # Mở Flashcard để ứng dụng tự khởi tạo thẻ mới.
        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'a[href="/vocabulary/flashcard/{lesson_id}"]',
            ))
        ).click()

        visible_text("span", "1/20")

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Lật thẻ"]',
            ))
        )

        # Không đánh giá thẻ, chuyển sang Ôn tập.
        driver.get(f"{base_url}/review")

        visible_text("span", "Ôn tập hôm nay")
        visible_text("span", "0%")
        visible_text("span", "✓ 0 đúng")
        visible_text("span", "✗ 0 cần ôn lại")
        visible_text("span", "20 còn lại")
        visible_text("span", "0/20 từ")

        front = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-4",
            ))
        )
        current_word = front.text.strip()

        assert current_word in lesson_words, (
            f"Thẻ ôn không thuộc bài vừa khởi tạo: {current_word}"
        )

        assert not driver.find_elements(
            By.XPATH,
            '//h2[normalize-space(.)="Xong rồi!"]',
        )

        game_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[contains(normalize-space(.), '
                '"Game 20 từ chưa thuộc")]',
            ))
        )
        assert game_button.is_displayed()

        # Trước khi lật chưa có nút đánh giá.
        for label in ("Chưa thuộc", "Đã thuộc"):
            assert not driver.find_elements(
                By.XPATH,
                f'//button[.//p[normalize-space(.)="{label}"]]',
            )

        driver.save_screenshot("REVIEW-02-due-front.png")

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Lật thẻ"]',
            ))
        ).click()

        for label in ("Chưa thuộc", "Đã thuộc"):
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f'//button[.//p[normalize-space(.)="{label}"]]',
                ))
            )

        wait.until(
            lambda browser: browser.find_elements(
                By.CSS_SELECTOR,
                'div[style*="preserve-3d"][style*="rotateY(180deg)"]',
            )
        )

        # Đọc textContent vì hai mặt thẻ cùng tồn tại trong DOM.
        back_word = driver.find_element(
            By.CSS_SELECTOR, "p.hanzi.text-5xl.font-bold.mb-1"
        )
        assert back_word.get_attribute("textContent").strip() == current_word

        back_panel = back_word.find_element(By.XPATH, "..")

        actual_pinyin = back_panel.find_element(
            By.CSS_SELECTOR, "p.text-xl.font-semibold.mb-4"
        ).get_attribute("textContent").strip()

        actual_meaning = back_panel.find_element(
            By.CSS_SELECTOR, "p.font-bold.text-base.mb-2"
        ).get_attribute("textContent").strip()

        assert actual_pinyin == lesson_words[current_word]["pinyin"]
        assert actual_meaning == lesson_words[current_word]["meaning"]

        # Lật thẻ không được tự tăng tiến độ.
        visible_text("span", "0/20 từ")
        visible_text("span", "20 còn lại")

        driver.save_screenshot(f"{case_id}-pass.png")
        print(
            f"\n{case_id}: khởi tạo 20 thẻ mới qua Flashcard; "
            "Ôn tập hiển thị 20 từ cần ôn, tiến độ 0/20; "
            f"thẻ {current_word} thuộc bài, "
            "Pinyin và nghĩa khớp; lật thẻ chưa tăng tiến độ"
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