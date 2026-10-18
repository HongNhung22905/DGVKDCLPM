import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_progress_with_due_cards():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(15)
    wait = WebDriverWait(driver, 30)

    case_id = "PROGRESS-02"
    base_url = "http://localhost:3000"
    email = f"progress.cards.{uuid.uuid4().hex[:12]}@example.com"

    def visible_text(tag, text):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
            ))
        )

    def summary_value(label):
        return driver.find_element(
            By.XPATH,
            f'//p[normalize-space(.)="{label}"]/../'
            'p[contains(@class,"text-2xl")]',
        ).text.strip()

    try:
        # Tạo tài khoản mới chưa có bài hoàn thành.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Thống kê thẻ")

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

        # Khởi tạo thẻ bằng Flashcard, không đánh giá hoặc hoàn thành bài.
        driver.get(
            f"{base_url}/vocabulary/flashcard/new-1-lesson-1"
        )

        visible_text("span", "1/20")

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Lật thẻ"]',
            ))
        )

        today = driver.execute_script(
            """
            const now = new Date();
            const pad = value => String(value).padStart(2, "0");
            return now.getFullYear() + "-"
                + pad(now.getMonth() + 1) + "-"
                + pad(now.getDate());
            """
        )

        # Đọc server để xác nhận dữ liệu chuẩn bị đã lưu.
        # Không tạo hoặc sửa dữ liệu bằng API.
        def cards_saved(browser):
            response = browser.execute_async_script(
                """
                const date = arguments[0];
                const done = arguments[arguments.length - 1];

                fetch("/api/review?date=" + encodeURIComponent(date), {
                    credentials: "include",
                    cache: "no-store"
                })
                    .then(async response => done({
                        status: response.status,
                        body: await response.json()
                    }))
                    .catch(error => done({
                        error: String(error)
                    }));
                """,
                today,
            )

            assert "error" not in response, response
            assert response["status"] == 200, response

            data = response["body"]
            if (
                len(data.get("cards", [])) == 20
                and len(data.get("allCards", [])) == 20
            ):
                return data

            return False

        review_data = wait.until(cards_saved)

        assert len({
            card["wordId"] for card in review_data["allCards"]
        }) == 20

        assert all(
            card["nextReview"] <= today
            for card in review_data["cards"]
        )

        driver.get(f"{base_url}/progress")
        visible_text("h1", "Tiến độ học")

        expected_stats = {
            "Bài hoàn thành": "0",
            "Đang ôn SM-2": "20",
            "Cần ôn hôm nay": "20",
            "Kiểm tra đạt": "0",
        }

        for label, expected in expected_stats.items():
            wait.until(
                lambda browser, name=label, value=expected:
                summary_value(name) == value
            )

        # Có thẻ SM-2 không đồng nghĩa đã hoàn thành bài học.
        for level in range(1, 8):
            label = visible_text("p", f"HSK {level}")
            panel = label.find_element(
                By.XPATH,
                './ancestor::div[contains(@class,"rounded-2xl")][1]',
            )

            assert panel.find_element(
                By.XPATH,
                './/p[normalize-space(.)="0/15 bài"]',
            ).is_displayed()

            assert panel.find_element(
                By.XPATH,
                './/span[normalize-space(.)="0%"]',
            ).is_displayed()

        visible_text("p", "20 từ cần ôn hôm nay!")

        review_link = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//a[normalize-space(.)="Ôn ngay"]',
            ))
        )

        assert review_link.get_attribute("href") == (
            f"{base_url}/review"
        )

        driver.save_screenshot("PROGRESS-02-stats.png")
        review_link.click()

        wait.until(
            EC.url_to_be(f"{base_url}/review")
        )

        visible_text("span", "0/20 từ")
        visible_text("span", "20 còn lại")
        visible_text("span", "✓ 0 đúng")

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Lật thẻ"]',
            ))
        )

        driver.save_screenshot(f"{case_id}-pass.png")

        print(
            f"\n{case_id}: 20 thẻ SM-2, 20 từ đến hạn; "
            "0 bài hoàn thành, 0 kiểm tra đạt; "
            "HSK 1–7 vẫn 0/15 bài; "
            "Ôn ngay mở đúng lượt ôn 20 từ"
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