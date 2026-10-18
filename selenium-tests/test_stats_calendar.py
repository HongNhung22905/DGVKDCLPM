import uuid

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_stats_calendar_and_ranges():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(15)
    wait = WebDriverWait(driver, 30)

    case_id = "STATS-03"
    base_url = "http://localhost:3000"
    email = f"stats.calendar.{uuid.uuid4().hex[:12]}@example.com"

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
        # Tạo tài khoản mới.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Lịch ôn")

        driver.find_element(
            By.CSS_SELECTOR,
            'input[type="email"]',
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]',
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR,
            'button[type="submit"]',
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        # Mở Flashcard để khởi tạo 20 thẻ đến hạn.
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

        # Chờ thẻ được lưu trước khi mở phiên ôn.
        session_date = local_today()

        def cards_ready(browser):
            response = browser.execute_async_script(
                """
                const date = arguments[0];
                const done = arguments[arguments.length - 1];

                fetch(
                    "/api/review?date=" + encodeURIComponent(date),
                    { credentials: "include", cache: "no-store" }
                )
                    .then(async r => done({
                        status: r.status,
                        body: await r.json()
                    }))
                    .catch(error => done({error: String(error)}));
                """,
                session_date,
            )

            assert "error" not in response, response
            assert response["status"] == 200, response

            data = response["body"]
            return (
                len(data.get("allCards", [])) == 20
                and len(data.get("cards", [])) == 20
            )

        wait.until(cards_ready)

        driver.get(f"{base_url}/review")
        visible_text("span", "0/20 từ")

        # Hoàn thành phiên ôn bằng giao diện.
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
        assert local_today() == session_date, (
            "Ngày local đổi trong lúc chạy; cần chạy lại."
        )

        # Chỉ đọc API để chờ dữ liệu được lưu.
        def session_saved(browser):
            response = browser.execute_async_script(
                """
                const date = arguments[0];
                const done = arguments[arguments.length - 1];

                fetch(
                    "/api/review/history?days=119&date="
                        + encodeURIComponent(date),
                    { credentials: "include", cache: "no-store" }
                )
                    .then(async r => done({
                        status: r.status,
                        body: await r.json()
                    }))
                    .catch(error => done({error: String(error)}));
                """,
                session_date,
            )

            assert "error" not in response, response
            assert response["status"] == 200, response

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

        # Đối chiếu dòng lịch sử trước khi kiểm tra lịch lưới.
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

        assert row.find_element(
            By.XPATH,
            f'.//p[normalize-space(.)="{date_label}"]',
        ).is_displayed()

        for value in ("20 từ", "100%", "20/20"):
            assert row.find_element(
                By.XPATH,
                f'.//span[normalize-space(.)="{value}"]',
            ).is_displayed()

        # Kiểm tra lịch dạng lưới.
        calendar_heading = visible_text(
            "h2", "Lịch học theo ngày"
        )
        calendar_panel = calendar_heading.find_element(
            By.XPATH,
            './ancestor::div[contains(@class,"rounded-2xl")][1]',
        )

        expected_tooltip_date = driver.execute_script(
            """
            return new Date(arguments[0]).toLocaleDateString(
                "vi-VN",
                {
                    weekday: "short",
                    year: "numeric",
                    month: "short",
                    day: "numeric"
                }
            );
            """,
            session_date,
        )

        def calendar_cells():
            # Ô ngày: 14 × 14 px; ô chú thích màu: 12 × 12 px.
            return calendar_panel.find_elements(
                By.CSS_SELECTOR,
                'div[style*="width: 14px"][style*="height: 14px"]',
            )

        calendar_errors = []

        for label, weeks in (
            ("4 tháng", 17),
            ("6 tháng", 26),
            ("1 năm", 52),
            ("4 tháng", 17),
        ):
            range_button = calendar_panel.find_element(
                By.XPATH,
                f'.//button[normalize-space(.)="{label}"]',
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                range_button,
            )
            range_button.click()

            wait.until(
                lambda browser: len(calendar_cells()) == weeks * 7
            )

            wait.until(
    lambda browser:
    calendar_panel.find_element(
        By.XPATH,
        f'.//button[normalize-space(.)="{label}"]',
    ).value_of_css_property("background-color")
    == "rgba(180, 83, 9, 1)",
    message=f"Nút {label} chưa hiển thị trạng thái được chọn.",
)

            cells = calendar_cells()
            active_cells = [
                cell for cell in cells
                if cell.value_of_css_property("cursor") == "pointer"
            ]

            print(
                f"\n{label}: {len(cells)} ô ngày; "
                f"{len(active_cells)} ô có dữ liệu"
            )

            screenshot_label = {
                "4 tháng": "4-months",
                "6 tháng": "6-months",
                "1 năm": "1-year",
            }[label]

            # Ghi nhận lỗi nhưng vẫn kiểm tra các khoảng còn lại.
            if len(active_cells) != 1:
                calendar_errors.append(
                    f"{label}: mong đợi 1 ô chứa phiên hôm nay "
                    f"({session_date}), thực tế có "
                    f"{len(active_cells)} ô có dữ liệu."
                )

                driver.save_screenshot(
                    f"{case_id}-{screenshot_label}-fail.png"
                )

            else:
                active_cell = active_cells[0]
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    active_cell,
                )

                ActionChains(driver).move_to_element(
                    active_cell
                ).perform()

                tooltip = wait.until(
                    EC.visibility_of_element_located((
                        By.CSS_SELECTOR,
                        "div.fixed.z-50.pointer-events-none",
                    ))
                )

                assert tooltip.find_element(
                    By.XPATH,
                    f'.//p[normalize-space(.)='
                    f'"{expected_tooltip_date}"]',
                ).is_displayed(), (
                    f"{label}: tooltip không ghi đúng ngày hôm nay."
                )

                assert tooltip.find_element(
                    By.XPATH,
                    './/p[normalize-space(.)='
                    '"20 từ ôn · 100% đúng"]',
                ).is_displayed()

                driver.save_screenshot(
                    f"{case_id}-{screenshot_label}.png"
                )

                ActionChains(driver).move_to_element(
                    calendar_heading
                ).perform()

                wait.until(
                    EC.invisibility_of_element_located((
                        By.CSS_SELECTOR,
                        "div.fixed.z-50.pointer-events-none",
                    ))
                )

            # Các chỉ số phải giữ nguyên sau khi đổi khoảng.
            for stat_label, expected in expected_stats.items():
                wait.until(
                    lambda browser, name=stat_label, value=expected:
                    stat_value(name) == value
                )

            assert local_today() == session_date, (
                "Ngày local đổi trong lúc chạy; cần chạy lại."
            )

        assert not calendar_errors, (
            "API và dòng lịch sử xác nhận hôm nay có 20 từ, "
            "nhưng lịch dạng lưới không hiển thị đúng:\n"
            + "\n".join(calendar_errors)
        )

        driver.save_screenshot(f"{case_id}-pass.png")

        print(
            f"\n{case_id}: chuyển 4 tháng, 6 tháng, 1 năm "
            "và quay lại 4 tháng thành công; "
            "số ô ngày đúng; mỗi khoảng có một ô phiên hôm nay; "
            "tooltip đúng ngày, 20 từ, 100%; "
            "các chỉ số giữ nguyên"
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