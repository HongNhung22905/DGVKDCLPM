import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    "case_id", ["REVIEW-05", "REVIEW-06"]
)
def test_review_repeated_card(case_id):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    base_url = "http://localhost:3000"
    email = f"review.repeat.{uuid.uuid4().hex[:12]}@example.com"

    def visible_text(tag, text):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
            ))
        )

    def current_word():
        return wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-4",
            ))
        ).text.strip()

    def rate_card(label):
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Lật thẻ"]',
            ))
        ).click()

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f'//button[.//p[normalize-space(.)="{label}"]]',
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
        ).send_keys("Kiểm thử Ôn lại từ")

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

        # Đọc tập từ để đối chiếu.
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
        assert len(lesson_words) == 20

        # Khởi tạo thẻ qua giao diện Flashcard.
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

        visible_text("span", "0/20 từ")
        first_word = current_word()
        assert first_word in lesson_words

        # Từ đầu chọn Chưa thuộc.
        rate_card("Chưa thuộc")

        visible_text("span", "1/20 từ")
        visible_text("span", "✓ 0 đúng")
        visible_text("span", "✗ 1 cần ôn lại")

        seen_words = {first_word}

        # 19 từ còn lại chọn Đã thuộc.
        for reviewed_before in range(1, 20):
            visible_text("span", f"{reviewed_before}/20 từ")

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Lật thẻ"]',
                ))
            )

            word = current_word()
            assert word in lesson_words
            assert word not in seen_words, (
                f"Từ {word} lặp trước khi hết 20 từ gốc."
            )
            seen_words.add(word)

            rate_card("Đã thuộc")
            visible_text(
                "span", f"{reviewed_before + 1}/20 từ"
            )

        assert seen_words == lesson_words

        # Từ chưa thuộc phải xuất hiện lại cuối hàng đợi.
        visible_text("span", "100%")
        visible_text("span", "20/20 từ")
        visible_text("span", "0 còn lại")
        visible_text("span", "✓ 19 đúng")
        visible_text("span", "✗ 1 cần ôn lại")

        wait.until(
            lambda browser: browser.find_element(
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-4",
            ).text.strip() == first_word
        )

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//div[contains(normalize-space(.), '
                '"Ôn lại — từ chưa nhớ") '
                'and not(.//div[contains(normalize-space(.), '
                '"Ôn lại — từ chưa nhớ")])]',
            ))
        )

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Lật thẻ"]',
            ))
        )

        assert not driver.find_elements(
            By.XPATH,
            '//h2[normalize-space(.)="Ôn tập xong!"]',
        )

        if case_id == "REVIEW-06":
            driver.save_screenshot(
                "REVIEW-06-before-final-rating.png"
            )

            # Đánh giá lại từ đầu là Đã thuộc.
            rate_card("Đã thuộc")

            heading = visible_text("h2", "Ôn tập xong!")
            summary_panel = heading.find_element(By.XPATH, "..")

            def get_stat(label):
                return summary_panel.find_element(
                    By.XPATH,
                    f'.//p[normalize-space(.)="{label}"]/../p[1]',
                ).text.strip()

            assert get_stat("Từ ôn") == "20"
            assert get_stat("Nhớ đúng") == "20"
            assert get_stat("Tỉ lệ") == "100%"

            visible_text(
                "p",
                "Tuyệt vời! Bạn nhớ tất cả 20 từ hôm nay 🎉",
            )

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Ôn lại từ đầu"]',
                ))
            )

            study_link = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//a[normalize-space(.)="Học bài mới"]',
                ))
            )
            assert study_link.get_attribute("href") == (
                f"{base_url}/vocabulary"
            )

            # Không còn từ chưa thuộc sau đánh giá cuối cùng.
            assert not driver.find_elements(
                By.XPATH,
                '//button[contains(normalize-space(.), '
                '"từ chưa nhớ") or contains(normalize-space(.), '
                '"Chơi game với")]',
            )

            assert not driver.find_elements(
                By.XPATH,
                '//p[contains(normalize-space(.), "từ cần ôn thêm")]',
            )

            assert not driver.find_elements(
                By.XPATH,
                '//button[normalize-space(.)="Lật thẻ"]',
            )

            message = (
                f"đánh giá lại {first_word} là Đã thuộc; "
                "hoàn thành sau 21 lượt đánh giá; "
                "tổng 20 từ gốc, nhớ đúng 20, tỷ lệ 100%; "
                "không còn danh sách hoặc nút ôn từ chưa nhớ"
            )

        else:
            message = (
                f"từ {first_word} chọn Chưa thuộc "
                "xuất hiện lại sau 20 từ gốc; "
                "có nhãn Ôn lại — từ chưa nhớ; "
                "19 đúng, 1 cần ôn lại; "
                "chưa kết thúc phiên dù tiến độ từ gốc là 100%"
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