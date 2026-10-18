import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_progress_after_completing_flashcards():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(15)
    wait = WebDriverWait(driver, 30)

    case_id = "PROGRESS-03"
    base_url = "http://localhost:3000"
    lesson_id = "new-1-lesson-1"
    email = f"progress.done.{uuid.uuid4().hex[:12]}@example.com"

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
        # Tạo tài khoản mới.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Bài hoàn thành")

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

        # Hoàn thành 20 thẻ bằng giao diện Flashcard.
        driver.get(
            f"{base_url}/vocabulary/flashcard/{lesson_id}"
        )

        session_date = driver.execute_script(
            """
            const now = new Date();
            const pad = value => String(value).padStart(2, "0");
            return now.getFullYear() + "-"
                + pad(now.getMonth() + 1) + "-"
                + pad(now.getDate());
            """
        )

        for position in range(1, 21):
            visible_text("span", f"{position}/20")

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Lật thẻ"]',
                ))
            ).click()

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[contains(normalize-space(.), "Nhớ rồi")]',
                ))
            ).click()

        visible_text("h2", "Xong rồi!")

        # Chờ lưu bài và lịch ôn trên server.
        # Chỉ đọc API, không ghi tiến độ bằng script.
        def progress_saved(browser):
            response = browser.execute_async_script(
                """
                const date = arguments[0];
                const lessonId = arguments[1];
                const done = arguments[arguments.length - 1];

                Promise.all([
                    fetch("/api/progress/lesson", {
                        credentials: "include",
                        cache: "no-store"
                    }).then(async r => ({
                        status: r.status,
                        body: await r.json()
                    })),
                    fetch(
                        "/api/review?date=" + encodeURIComponent(date),
                        {
                            credentials: "include",
                            cache: "no-store"
                        }
                    ).then(async r => ({
                        status: r.status,
                        body: await r.json()
                    }))
                ])
                    .then(([lessons, review]) => {
                        done({
                            lessons: lessons,
                            review: review
                        });
                    })
                    .catch(error => done({error: String(error)}));
                """,
                session_date,
                lesson_id,
            )

            assert "error" not in response, response
            assert response["lessons"]["status"] == 200
            assert response["review"]["status"] == 200

            lessons = response["lessons"]["body"].get("lessons", [])
            review = response["review"]["body"]

            return (
                any(
                    item["lessonId"] == lesson_id
                    and item["completed"] is True
                    for item in lessons
                )
                and len(review.get("allCards", [])) == 20
                and len(review.get("cards", [])) == 0
            )

        wait.until(progress_saved)

        driver.get(f"{base_url}/progress")
        visible_text("h1", "Tiến độ học")

        expected_stats = {
            "Bài hoàn thành": "1",
            "Đang ôn SM-2": "20",
            "Cần ôn hôm nay": "0",
            "Kiểm tra đạt": "0",
        }

        for label, expected in expected_stats.items():
            wait.until(
                lambda browser, name=label, value=expected:
                summary_value(name) == value
            )

        # Bài hoàn thành thuộc HSK 1.
        for level in range(1, 8):
            label = visible_text("p", f"HSK {level}")

            panel = label.find_element(
                By.XPATH,
                './ancestor::div[contains(@class,"rounded-2xl")][1]',
            )

            expected_count = "1/15 bài" if level == 1 else "0/15 bài"
            expected_percent = "7%" if level == 1 else "0%"

            assert panel.find_element(
                By.XPATH,
                f'.//p[normalize-space(.)="{expected_count}"]',
            ).is_displayed()

            assert panel.find_element(
                By.XPATH,
                f'.//span[normalize-space(.)="{expected_percent}"]',
            ).is_displayed()

        # Đã hoàn thành bài thì không còn lời mời bắt đầu từ số 0.
        assert not driver.find_elements(
            By.XPATH,
            '//p[normalize-space(.)='
            '"Bạn chưa hoàn thành bài học nào. Bắt đầu từ HSK 1 nhé!"]',
        )

        assert not driver.find_elements(
            By.XPATH,
            '//a[normalize-space(.)="Bắt đầu học"]',
        )

        assert not driver.find_elements(
            By.XPATH,
            '//a[normalize-space(.)="Ôn ngay"]',
        ), "Vẫn hiển thị Ôn ngay dù không có thẻ đến hạn."

        driver.save_screenshot(f"{case_id}-pass.png")

        print(
            f"\n{case_id}: hoàn thành 1 bài Flashcard; "
            "HSK 1 = 1/15 bài, 7%; HSK 2–7 = 0%; "
            "20 thẻ SM-2, 0 từ đến hạn, 0 kiểm tra đạt; "
            "không còn Bắt đầu học hoặc Ôn ngay"
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