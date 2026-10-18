import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_stats_after_one_review_session():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(15)
    wait = WebDriverWait(driver, 30)

    case_id = "STATS-02"
    base_url = "http://localhost:3000"
    email = f"stats.session.{uuid.uuid4().hex[:12]}@example.com"

    def visible_text(tag, text):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
            ))
        )

    def stat_value(label):
        return driver.find_element(
            By.XPATH,
            f'//p[normalize-space(.)="{label}"]/../'
            'p[contains(@class,"text-2xl")]',
        ).text.strip()

    def local_today():
        return driver.execute_script(
            """
            const now = new Date();
            const pad = value => String(value).padStart(2, "0");
            return now.getFullYear() + "-"
                + pad(now.getMonth() + 1) + "-"
                + pad(now.getDate());
            """
        )

    try:
        # Chuẩn bị tài khoản mới.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Thống kê phiên ôn")

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

        # Khởi tạo 20 thẻ, chưa đánh giá trên Flashcard.
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

        driver.get(f"{base_url}/review")
        visible_text("span", "0/20 từ")
        session_date = local_today()

        # Hoàn thành phiên ôn: tất cả chọn Đã thuộc.
        seen_words = set()

        for reviewed_before in range(20):
            visible_text("span", f"{reviewed_before}/20 từ")

            flip_button = wait.until(
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

            flip_button.click()

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[.//p[normalize-space(.)="Đã thuộc"]]',
                ))
            ).click()

        visible_text("h2", "Ôn tập xong!")
        assert len(seen_words) == 20
        assert local_today() == session_date, (
            "Ngày local đổi trong lúc chạy; cần chạy lại."
        )

        # Chờ lịch sử và cập nhật thẻ được lưu nền.
        # Chỉ đọc API để đối chiếu, không tạo phiên qua POST.
        def session_saved(browser):
            response = browser.execute_async_script(
                """
                const date = arguments[0];
                const done = arguments[arguments.length - 1];

                fetch(
                    "/api/review/history?days=119&date="
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
                session_date,
            )

            assert "error" not in response, response
            assert response["status"] == 200

            data = response["body"]
            stats = data["stats"]

            assert stats["totalSessions"] <= 1, (
                "Tài khoản mới có lịch sử phiên bị lưu trùng."
            )

            if (
                stats["totalSessions"] == 1
                and stats["allCards"] == 20
                and stats["dueToday"] == 0
            ):
                return data

            return False

        history = wait.until(session_saved)

        assert len(history["daily"]) == 1
        daily = history["daily"][0]

        assert daily["date"] == session_date
        assert daily["totalCards"] == 20
        assert daily["correctCards"] == 20
        assert daily["sessions"] == 1
        assert daily["score"] == 100

        driver.get(f"{base_url}/stats")
        visible_text("h1", "Thống kê ôn tập")

        expected_stats = {
            "Chuỗi ngày": "1 ngày",
            "Từ đã ôn": "20",
            "Điểm TB": "100%",
            "Ngày đã học": "1 ngày",
            "Tổng thẻ đang ôn": "20",
            "Cần ôn hôm nay": "0",
            "Đã ôn ngày mai trở đi": "20",
        }

        for label, expected in expected_stats.items():
            wait.until(
                lambda browser, name=label, value=expected:
                stat_value(name) == value
            )

        assert not driver.find_elements(
            By.XPATH,
            '//p[normalize-space(.)="Chưa có dữ liệu ôn tập"]',
        )

        # Lịch sử hiển thị một dòng tổng hợp theo ngày.
        history_heading = visible_text(
            "h2", "Lịch sử phiên ôn tập"
        )
        history_panel = history_heading.find_element(
            By.XPATH,
            './ancestor::div[contains(@class,"rounded-2xl")][1]',
        )

        rows = history_panel.find_elements(
            By.CSS_SELECTOR,
            "div.flex.items-center.px-5.py-3",
        )
        assert len(rows) == 1

        row = rows[0]
        date_label = driver.execute_script(
            """
            return new Date(arguments[0]).toLocaleDateString(
                "vi-VN",
                { day: "2-digit", month: "2-digit" }
            );
            """,
            session_date,
        )

        print(
            f"\nNgày mong đợi: {date_label!r}; "
            f"Dòng lịch sử thực tế: {row.text!r}"
        )

        assert row.find_element(
            By.XPATH,
            f'.//p[normalize-space(.)="{date_label}"]',
        ).is_displayed()

        for value in ("20 từ", "100%", "20/20"):
            assert row.find_element(
                By.XPATH,
                f'.//span[normalize-space(.)="{value}"]',
            ).is_displayed()

        # Đối chiếu thời lượng hiển thị nếu phiên dài hơn 0 giây.
        seconds = daily["durationSec"]
        if seconds > 0:
            if seconds < 60:
                duration_text = f"{seconds}s"
            else:
                minutes, remaining_seconds = divmod(seconds, 60)
                duration_text = (
                    f"{minutes}p {remaining_seconds}s"
                    if remaining_seconds
                    else f"{minutes}p"
                )

            assert row.find_element(
                By.XPATH,
                f'.//span[normalize-space(.)="{duration_text}"]',
            ).is_displayed()

        # Biểu đồ 30 ngày: đúng một ngày có dữ liệu.
        chart_heading = visible_text("h2", "30 ngày gần nhất")
        chart_panel = chart_heading.find_element(By.XPATH, "..")
        bars = chart_panel.find_elements(
            By.CSS_SELECTOR, "div[title]"
        )

        assert len(bars) == 30
        active_titles = [
            bar.get_attribute("title")
            for bar in bars
            if not bar.get_attribute("title").endswith(": 0 từ, 0%")
        ]

        today_chart_label = (
            f"{int(session_date[8:10])}/"
            f"{int(session_date[5:7])}: 20 từ, 100%"
        )
        assert active_titles == [today_chart_label], active_titles

        assert not driver.find_elements(
            By.XPATH,
            '//a[starts-with(normalize-space(.), "Ôn ") '
            'and contains(normalize-space(.), "từ ngay bây giờ")]',
        )

        driver.save_screenshot(f"{case_id}-pass.png")
        print(
            f"\n{case_id}: chuỗi 1 ngày, 20 từ đã ôn, "
            "điểm TB 100%, 1 ngày học; "
            "20 thẻ lên lịch tương lai, 0 đến hạn; "
            "lịch sử một ngày hiển thị 20/20; "
            "biểu đồ 30 ngày có đúng dữ liệu hôm nay"
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