import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_stats_persist_after_reload_and_login():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(15)
    wait = WebDriverWait(driver, 30)

    case_id = "STATS-04"
    base_url = "http://localhost:3000"
    account_name = "Kiểm thử Lưu thống kê"
    email = f"stats.persist.{uuid.uuid4().hex[:12]}@example.com"
    password = "1234567"

    expected_stats = {
        "Chuỗi ngày": "1 ngày",
        "Từ đã ôn": "20",
        "Điểm TB": "100%",
        "Ngày đã học": "1 ngày",
        "Tổng thẻ đang ôn": "20",
        "Cần ôn hôm nay": "0",
        "Đã ôn ngày mai trở đi": "20",
    }

    def visible_text(tag, text):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
            ))
        )

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

    def read_api(path):
        result = driver.execute_async_script(
            """
            const path = arguments[0];
            const done = arguments[arguments.length - 1];

            fetch(path, {
                credentials: "include",
                cache: "no-store"
            })
                .then(async response => done({
                    status: response.status,
                    body: await response.json()
                }))
                .catch(error => done({error: String(error)}));
            """,
            path,
        )

        assert "error" not in result, result
        assert result["status"] == 200, result
        return result["body"]

    def user_menu():
        return wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//nav//button[.//span[normalize-space(.)='
                f'"{account_name}"]]',
            ))
        )

    def check_stats(stage):
        visible_text("h1", "Thống kê ôn tập")

        assert local_today() == session_date, (
            "Ngày local đổi trong lúc chạy; cần chạy lại."
        )

        for label, expected in expected_stats.items():
            locator = (
                By.XPATH,
                f'//p[normalize-space(.)="{label}"]/../'
                'p[contains(@class,"text-2xl")]',
            )

            wait.until(
                lambda browser, loc=locator, value=expected:
                browser.find_element(*loc).text.strip() == value,
                message=f"{stage}: chỉ số {label} không đúng.",
            )

        heading = visible_text("h2", "Lịch sử phiên ôn tập")
        panel = heading.find_element(
            By.XPATH,
            './ancestor::div[contains(@class,"rounded-2xl")][1]',
        )

        rows = panel.find_elements(
            By.CSS_SELECTOR,
            "div.flex.items-center.px-5.py-3",
        )
        assert len(rows) == 1, (
            f"{stage}: mong đợi một dòng lịch sử, "
            f"thực tế có {len(rows)}."
        )

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

        assert row.find_element(
            By.XPATH,
            f'.//p[normalize-space(.)="{date_label}"]',
        ).is_displayed()

        for value in ("20 từ", "100%", "20/20"):
            assert row.find_element(
                By.XPATH,
                f'.//span[normalize-space(.)="{value}"]',
            ).is_displayed()

        assert not driver.find_elements(
            By.XPATH,
            '//p[normalize-space(.)="Chưa có dữ liệu ôn tập"]',
        )

        # Đối chiếu dữ liệu server, không ghi bằng script.
        history = read_api(
            "/api/review/history?days=119&date=" + session_date
        )

        assert history["stats"]["totalSessions"] == 1
        assert history["stats"]["totalCards"] == 20
        assert history["stats"]["allCards"] == 20
        assert history["stats"]["dueToday"] == 0
        assert len(history["daily"]) == 1
        assert history["daily"][0] == saved_daily, (
            f"{stage}: dữ liệu phiên ôn thay đổi."
        )

        driver.save_screenshot(f"{case_id}-{stage}.png")
        print(
            f"\n{case_id} — {stage}: 7 chỉ số đúng; "
            "một dòng lịch sử 20/20; dữ liệu server giữ nguyên"
        )

    try:
        # 1. Tạo tài khoản mới.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys(account_name)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[type="email"]',
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]',
        ).send_keys(password)

        driver.find_element(
            By.CSS_SELECTOR,
            'button[type="submit"]',
        ).click()

        wait.until(EC.url_contains("/vocabulary"))
        user_menu()

        session_date = local_today()

        # 2. Khởi tạo thẻ qua trang Flashcard.
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

        def cards_ready(browser):
            data = read_api(
                "/api/review?date=" + session_date
            )
            return (
                len(data.get("allCards", [])) == 20
                and len(data.get("cards", [])) == 20
            )

        wait.until(cards_ready)

        # 3. Hoàn thành phiên ôn qua giao diện.
        driver.get(f"{base_url}/review")
        visible_text("span", "0/20 từ")

        seen_words = set()

        for position in range(20):
            visible_text("span", f"{position}/20 từ")

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

            assert word, "Thẻ không hiển thị từ."
            assert word not in seen_words, (
                f"Từ bị lặp trong phiên ôn: {word}"
            )
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

        def session_saved(browser):
            data = read_api(
                "/api/review/history?days=119&date="
                + session_date
            )

            stats = data["stats"]
            assert stats["totalSessions"] <= 1, (
                "Phiên ôn bị lưu trùng."
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

        saved_daily = history["daily"][0]
        assert saved_daily["date"] == session_date
        assert saved_daily["totalCards"] == 20
        assert saved_daily["correctCards"] == 20
        assert saved_daily["sessions"] == 1
        assert saved_daily["score"] == 100

        # 4. Kiểm tra trước khi tải lại.
        driver.get(f"{base_url}/stats")
        check_stats("before-reload")

        # 5. Tải lại trang: phiên đăng nhập và dữ liệu còn đúng.
        driver.refresh()
        user_menu()
        check_stats("after-reload")

        # 6. Đăng xuất bằng menu tài khoản.
        user_menu().click()

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//nav//button[normalize-space(.)="Đăng xuất"]',
            ))
        ).click()

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//nav//a[@href="/login" '
                'and normalize-space(.)="Đăng nhập"]',
            ))
        )

        # 7. Đăng nhập lại bằng chính tài khoản vừa tạo.
        driver.get(f"{base_url}/login")
        visible_text("h1", "Đăng nhập")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'form input[type="email"]',
            ))
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'form input[type="password"]',
        ).send_keys(password)

        driver.find_element(
            By.CSS_SELECTOR,
            'form button[type="submit"]',
        ).click()

        wait.until(
            lambda browser:
            not browser.current_url.split("?")[0].rstrip(
                "/"
            ).endswith("/login")
        )
        user_menu()

        # Xác nhận đúng tài khoản.
        user_menu().click()
        visible_text("p", email)
        user_menu().click()

        # 8. Dữ liệu sau đăng nhập lại phải giữ nguyên.
        driver.get(f"{base_url}/stats")
        check_stats("after-login")

        driver.save_screenshot(f"{case_id}-pass.png")

        print(
            f"\n{case_id}: PASS — tải lại trang và "
            "đăng xuất/đăng nhập lại không làm mất thống kê; "
            "20 từ đã ôn, 100%, 1 ngày học; "
            "20 thẻ SM-2, 0 đến hạn; "
            "lịch sử giữ nguyên một phiên 20/20"
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