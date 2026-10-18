import re
import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_review_empty_for_new_account():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    case_id = "REVIEW-01"
    base_url = "http://localhost:3000"
    email = f"review.empty.{uuid.uuid4().hex[:12]}@example.com"

    try:
        # Chuẩn bị tài khoản mới, chưa mở Flashcard để tạo thẻ.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Ôn tập rỗng")

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

        driver.get(f"{base_url}/review")

        heading = wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//h2[normalize-space(.)="Xong rồi!"]',
            ))
        )

        panel = heading.find_element(By.XPATH, "..")
        message = panel.find_element(
            By.CSS_SELECTOR, "p.text-sm.mb-6"
        ).text

        assert "Không có từ nào cần ôn hôm nay" in message
        assert "Hãy học bài mới để thêm từ vào lịch ôn tập." in message

        date_match = re.search(
            r"hôm nay \((\d{4}-\d{2}-\d{2})\)",
            message,
        )
        assert date_match, (
            f"Thông báo thiếu ngày đúng định dạng: {message}"
        )

        # Lấy ngày local từ trình duyệt, không dùng ngày UTC.
        browser_today = driver.execute_script(
            """
            const now = new Date();
            const pad = value => String(value).padStart(2, "0");
            return now.getFullYear() + "-"
                + pad(now.getMonth() + 1) + "-"
                + pad(now.getDate());
            """
        )

        assert date_match.group(1) == browser_today, (
            f"Ngày hiển thị {date_match.group(1)} "
            f"khác ngày trình duyệt {browser_today}."
        )

        # Tài khoản mới không được có vùng thẻ hoặc nút đánh giá.
        assert not driver.find_elements(
            By.CSS_SELECTOR, "p.hanzi.font-bold.mb-4"
        )

        assert not driver.find_elements(
            By.XPATH,
            '//button[normalize-space(.)="Lật thẻ"]',
        )

        for label in ("Chưa thuộc", "Đã thuộc"):
            assert not driver.find_elements(
                By.XPATH,
                f'//button[.//p[normalize-space(.)="{label}"]]',
            )

        # Chưa có từ đã học thì không có game từ chưa thuộc.
        assert not panel.find_elements(
            By.XPATH,
            './/button[contains(normalize-space(.), "Chơi game với")]',
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

        driver.save_screenshot("REVIEW-01-empty-state.png")

        # Liên kết phải đưa về đúng trang Từ vựng.
        study_link.click()

        wait.until(
            EC.url_to_be(f"{base_url}/vocabulary")
        )

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[.//p[normalize-space(.)="HSK 1"]]',
            ))
        )

        driver.save_screenshot(f"{case_id}-pass.png")

        print(
            f"\n{case_id}: tài khoản mới không có từ cần ôn; "
            f"ngày hiển thị {browser_today} đúng ngày trình duyệt; "
            "không có thẻ, nút đánh giá hoặc game; "
            "Học bài mới về đúng trang Từ vựng"
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