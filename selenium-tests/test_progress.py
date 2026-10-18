import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_progress_empty_for_new_account():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    case_id = "PROGRESS-01"
    base_url = "http://localhost:3000"
    email = f"progress.empty.{uuid.uuid4().hex[:12]}@example.com"

    def visible_text(tag, text):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
            ))
        )

    try:
        # Tạo tài khoản mới, chưa học hoặc tạo thẻ.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Tiến độ mới")

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

        # Chờ các request khởi tạo trang tiến độ kết thúc
        # trước khi kết luận các giá trị 0 là dữ liệu đã tải.
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                window.__progressReads = {};
                const originalFetch = window.fetch;

                window.fetch = async function(...args) {
                    const input = args[0];
                    const rawUrl = typeof input === "string"
                        ? input
                        : input.url;
                    const url = new URL(rawUrl, location.href);
                    const tracked = [
                        "/api/progress/lesson",
                        "/api/progress/gate",
                        "/api/review"
                    ].includes(url.pathname);

                    const response = await originalFetch.apply(this, args);

                    if (tracked) {
                        const copy = response.clone();
                        try {
                            const body = await copy.json();
                            window.__progressReads[url.pathname] = {
                                status: response.status,
                                body: body
                            };
                        } catch {
                            window.__progressReads[url.pathname] = {
                                status: response.status,
                                invalidJson: true
                            };
                        }
                    }

                    return response;
                };
            """
        })

        driver.get(f"{base_url}/progress")
        visible_text("h1", "Tiến độ học")

        def initial_data_loaded(browser):
            data = browser.execute_script(
                "return window.__progressReads || {};"
            )
            paths = (
                "/api/progress/lesson",
                "/api/progress/gate",
                "/api/review",
            )

            for path in paths:
                if path not in data:
                    return False

                assert data[path]["status"] == 200, (
                    f"{path} trả {data[path]['status']}"
                )
                assert not data[path].get("invalidJson"), (
                    f"{path} không trả JSON hợp lệ."
                )

            return data

        loaded_data = wait.until(initial_data_loaded)

        # Đối chiếu trạng thái tài khoản mới từ dữ liệu server.
        assert loaded_data[
            "/api/progress/lesson"
        ]["body"]["lessons"] == []

        assert loaded_data[
            "/api/progress/gate"
        ]["body"]["gates"] == []

        review_data = loaded_data["/api/review"]["body"]
        assert review_data["cards"] == []
        assert review_data["allCards"] == []

        def summary_value(label):
            return driver.find_element(
                By.XPATH,
                f'//p[normalize-space(.)="{label}"]/../'
                'p[contains(@class,"text-2xl")]',
            ).text.strip()

        for label in (
            "Bài hoàn thành",
            "Đang ôn SM-2",
            "Cần ôn hôm nay",
            "Kiểm tra đạt",
        ):
            wait.until(
                lambda browser, name=label: summary_value(name) == "0"
            )

        visible_text("h2", "Tiến độ từng cấp độ")

        # Mỗi cấp có 0/15 bài và 0%.
        for level in range(1, 8):
            label = visible_text("p", f"HSK {level}")

            level_card = label.find_element(
                By.XPATH,
                './ancestor::div[contains(@class,"rounded-2xl")][1]',
            )

            assert level_card.find_element(
                By.XPATH,
                './/p[normalize-space(.)="0/15 bài"]',
            ).is_displayed()

            assert level_card.find_element(
                By.XPATH,
                './/span[normalize-space(.)="0%"]',
            ).is_displayed()

            bar = level_card.find_element(
                By.CSS_SELECTOR,
                "div.h-full.rounded-full.transition-all",
            )
            assert bar.value_of_css_property("width") == "0px"

            link = level_card.find_element(
                By.XPATH,
                './/a[normalize-space(.)="Học tiếp"]',
            )
            assert link.get_attribute("href") == (
                f"{base_url}/vocabulary"
            )

        visible_text(
            "p",
            "Bạn chưa hoàn thành bài học nào. Bắt đầu từ HSK 1 nhé!",
        )

        assert not driver.find_elements(
            By.XPATH,
            '//a[normalize-space(.)="Ôn ngay"]',
        ), "Hiển thị Ôn ngay dù chưa có từ đến hạn."

        start_link = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//a[normalize-space(.)="Bắt đầu học"]',
            ))
        )

        driver.save_screenshot("PROGRESS-01-empty.png")
        start_link.click()

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
            f"\n{case_id}: dữ liệu server đã tải; "
            "4 chỉ số tổng bằng 0; "
            "HSK 1–7 đều 0/15 bài, 0%; "
            "không có Ôn ngay; Bắt đầu học về đúng Từ vựng"
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