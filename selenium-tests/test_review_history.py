import time
import uuid

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_review_history_saved_once():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(15)
    wait = WebDriverWait(driver, 30)

    case_id = "REVIEW-08"
    base_url = "http://localhost:3000"
    email = f"review.history.{uuid.uuid4().hex[:12]}@example.com"

    def visible_text(tag, text):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
            ))
        )

    def browser_today():
        return driver.execute_script(
            """
            const now = new Date();
            const pad = value => String(value).padStart(2, "0");
            return now.getFullYear() + "-"
                + pad(now.getMonth() + 1) + "-"
                + pad(now.getDate());
            """
        )

    def read_history(date):
        response = driver.execute_async_script(
            """
            const date = arguments[0];
            const done = arguments[arguments.length - 1];

            fetch(
                "/api/review/history?days=90&date="
                    + encodeURIComponent(date),
                {
                    credentials: "include",
                    cache: "no-store"
                }
            )
                .then(async response => done({
                    status: response.status,
                    body: await response.json()
                }))
                .catch(error => done({
                    error: String(error)
                }));
            """,
            date,
        )

        assert "error" not in response, response
        assert response["status"] == 200, response
        return response["body"]

    try:
        # Chuẩn bị tài khoản mới.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Lịch sử ôn tập")

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
        session_date = browser_today()

        # Tài khoản mới phải chưa có lịch sử.
        initial_history = read_history(session_date)
        assert initial_history["daily"] == []
        assert initial_history["stats"]["totalSessions"] == 0

        # Khởi tạo 20 thẻ bằng giao diện Flashcard.
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

        review_started = time.monotonic()
        driver.get(f"{base_url}/review")

        visible_text("span", "0/20 từ")

        # Hoàn thành 20 thẻ, tất cả chọn Đã thuộc.
        seen_words = set()

        for reviewed_before in range(20):
            visible_text("span", f"{reviewed_before}/20 từ")

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Lật thẻ"]',
                ))
            )

            word = driver.find_element(
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-4",
            ).text.strip()

            assert word
            assert word not in seen_words
            seen_words.add(word)

            driver.find_element(
                By.XPATH,
                '//button[normalize-space(.)="Lật thẻ"]',
            ).click()

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[.//p[normalize-space(.)="Đã thuộc"]]',
                ))
            ).click()

        visible_text("h2", "Ôn tập xong!")
        assert len(seen_words) == 20

        assert browser_today() == session_date, (
            "Ngày local đổi trong lúc chạy; cần chạy lại."
        )

        # Chờ lịch sử được ứng dụng lưu nền.
        # Test chỉ GET để kiểm tra, không POST tạo phiên.
        def saved_history(browser):
            history = read_history(session_date)
            count = history["stats"]["totalSessions"]

            assert count <= 1, (
                f"Ứng dụng đã lưu trùng: {count} phiên."
            )

            return history if count == 1 else False

        history = wait.until(saved_history)

        def check_history(data):
            stats = data["stats"]
            daily = data["daily"]

            assert stats["totalSessions"] == 1
            assert stats["totalCards"] == 20
            assert stats["avgScore"] == 100
            assert stats["activeDays"] == 1
            assert stats["streak"] == 1
            assert stats["allCards"] == 20

            assert len(daily) == 1
            entry = daily[0]

            assert entry["date"] == session_date
            assert entry["sessions"] == 1
            assert entry["totalCards"] == 20
            assert entry["correctCards"] == 20
            assert entry["score"] == 100

            duration = entry["durationSec"]
            assert type(duration) is int
            assert 0 <= duration <= (
                time.monotonic() - review_started + 5
            ), f"Thời lượng không hợp lý: {duration}"

        check_history(history)
        saved_duration = history["daily"][0]["durationSec"]

        driver.save_screenshot("REVIEW-08-summary.png")

        # Tải lại không được tạo thêm một phiên hoàn thành.
        driver.refresh()

        visible_text("h2", "Xong rồi!")

        def remains_one_session(browser):
            current_history = read_history(session_date)
            check_history(current_history)

            assert (
                current_history["daily"][0]["durationSec"]
                == saved_duration
            ), "Thời lượng lịch sử thay đổi sau tải lại."

            return False

        # Theo dõi thêm 2 giây để bắt thao tác lưu phát sinh trễ.
        try:
            WebDriverWait(
                driver, 2, poll_frequency=0.2
            ).until(remains_one_session)
        except TimeoutException:
            pass

        # Kiểm tra lần cuối sau khoảng theo dõi.
        final_history = read_history(session_date)
        check_history(final_history)
        assert (
            final_history["daily"][0]["durationSec"]
            == saved_duration
        )

        driver.save_screenshot(f"{case_id}-pass.png")

        print(
            f"\n{case_id}: lịch sử ngày {session_date} có đúng 1 phiên; "
            "20 từ, 20 đúng, điểm 100%; "
            f"thời lượng {saved_duration}s hợp lệ; "
            "tải lại và theo dõi thêm 2 giây không tạo phiên trùng"
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