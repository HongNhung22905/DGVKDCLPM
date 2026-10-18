import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_stats_empty_for_new_account():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    case_id = "STATS-01"
    base_url = "http://localhost:3000"
    email = f"stats.empty.{uuid.uuid4().hex[:12]}@example.com"

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

    try:
        # Tạo tài khoản mới, chưa học hoặc ôn tập.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Thống kê rỗng")

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

        # Quan sát request của trang, không sửa response.
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    window.__statsHistoryRead = null;
                    const originalFetch = window.fetch;

                    window.fetch = async function(...args) {
                        const input = args[0];
                        const rawUrl = typeof input === "string"
                            ? input
                            : input.url;
                        const url = new URL(rawUrl, location.href);

                        const response = await originalFetch.apply(
                            this, args
                        );

                        if (url.pathname === "/api/review/history") {
                            try {
                                const body = await response.clone().json();
                                window.__statsHistoryRead = {
                                    status: response.status,
                                    body: body
                                };
                            } catch {
                                window.__statsHistoryRead = {
                                    status: response.status,
                                    invalidJson: true
                                };
                            }
                        }

                        return response;
                    };
                """
            },
        )

        driver.get(f"{base_url}/stats")
        visible_text("h1", "Thống kê ôn tập")

        def history_loaded(browser):
            result = browser.execute_script(
                "return window.__statsHistoryRead;"
            )

            if result is None:
                return False

            assert result["status"] == 200, result
            assert not result.get("invalidJson"), result
            return result["body"]

        history = wait.until(history_loaded)

        assert history["daily"] == []
        for key in (
            "streak",
            "totalSessions",
            "totalCards",
            "avgScore",
            "activeDays",
            "allCards",
            "dueToday",
        ):
            assert history["stats"][key] == 0, (
                f"API: {key} khác 0."
            )

        expected_stats = {
            "Chuỗi ngày": "0 ngày",
            "Từ đã ôn": "0",
            "Điểm TB": "0%",
            "Ngày đã học": "0 ngày",
            "Tổng thẻ đang ôn": "0",
            "Cần ôn hôm nay": "0",
            "Đã ôn ngày mai trở đi": "0",
        }

        for label, expected in expected_stats.items():
            wait.until(
                lambda browser, name=label, value=expected:
                stat_value(name) == value
            )

        visible_text("h2", "Bộ thẻ SM-2 hiện tại")
        visible_text("h2", "Lịch học theo ngày")
        visible_text("h2", "30 ngày gần nhất")

        for label in ("4 tháng", "6 tháng", "1 năm"):
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f'//button[normalize-space(.)="{label}"]',
                ))
            )

        # 30 cột dữ liệu phải đều có số từ và điểm bằng 0.
        chart_heading = visible_text("h2", "30 ngày gần nhất")
        chart_panel = chart_heading.find_element(By.XPATH, "..")

        bars = chart_panel.find_elements(
            By.CSS_SELECTOR, "div[title]"
        )
        assert len(bars) == 30, (
            f"Số cột thực tế: {len(bars)}"
        )

        for bar in bars:
            title = bar.get_attribute("title")
            assert title.endswith(": 0 từ, 0%"), title

        visible_text("p", "Chưa có dữ liệu ôn tập")
        visible_text(
            "p",
            "Học flashcard và ôn tập để thấy thống kê tại đây",
        )

        assert not driver.find_elements(
            By.XPATH,
            '//h2[normalize-space(.)="Lịch sử phiên ôn tập"]',
        )

        assert not driver.find_elements(
            By.XPATH,
            '//a[starts-with(normalize-space(.), "Ôn ") '
            'and contains(normalize-space(.), "từ ngay bây giờ")]',
        )

        # Tài khoản đã đăng nhập không được nhận lời mời đăng nhập.
        assert not driver.find_elements(
            By.XPATH,
            '//p[normalize-space(.)='
            '"Đăng nhập để lưu lịch sử ôn tập theo ngày lên cloud"]',
        )

        study_link = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//a[normalize-space(.)="Học từ vựng"]',
            ))
        )
        assert study_link.get_attribute("href") == (
            f"{base_url}/vocabulary"
        )

        # Chỉ chọn liên kết Ôn tập trong khối trạng thái rỗng,
        # tránh nhầm mục Ôn tập ở navbar.
        empty_message = visible_text(
            "p", "Chưa có dữ liệu ôn tập"
        )
        empty_panel = empty_message.find_element(By.XPATH, "..")

        review_link = empty_panel.find_element(
            By.XPATH,
            './/a[normalize-space(.)="Ôn tập"]',
        )
        assert review_link.is_displayed()
        assert review_link.get_attribute("href") == (
            f"{base_url}/review"
        )

        driver.save_screenshot("STATS-01-empty.png")

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
            f"\n{case_id}: API lịch sử tải thành công, chưa có phiên; "
            "7 chỉ số bằng 0; 30 ngày không có lượt ôn; "
            "hiển thị trạng thái rỗng, không có bảng lịch sử; "
            "Học từ vựng dẫn đúng trang"
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