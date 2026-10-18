import uuid

from selenium import webdriver
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_complete_one_character():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(60)
    wait = WebDriverWait(driver, 30)

    case_id = "WRITE-07"
    email = f"writing.complete.{uuid.uuid4().hex[:12]}@example.com"

    def click_button(label):
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f'//button[normalize-space(.)="{label}"]'
            ))
        ).click()

    try:
        # Chuẩn bị tài khoản mới.
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Kiểm thử Viết đúng")

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        # Lấy hai từ đầu làm dữ liệu đối chiếu.
        driver.get(
            "http://localhost:3000/vocabulary/lesson/new-1-lesson-1"
        )

        words = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR,
                "span.hanzi.text-2xl.font-bold"
            ))
        )
        assert len(words) == 20

        first_word = words[0].text.strip()
        second_word = words[1].text.strip()
        character = first_word[0]

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'a[href="/vocabulary/writing/new-1-lesson-1"]'
            ))
        ).click()

        click_button("Kiểm tra nét")

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Tự viết"]'
            ))
        )

        WebDriverWait(driver, 60).until(
            lambda browser: any(
                path.get_attribute("d")
                for path in browser.find_elements(
                    By.CSS_SELECTOR,
                    'svg[width="260"][height="260"] path'
                )
            )
        )

        # Tải dữ liệu chuẩn bị đường đi của chuột.
        result = driver.execute_async_script(
            """
            const character = arguments[0];
            const done = arguments[arguments.length - 1];
            const url =
                "https://cdn.jsdelivr.net/npm/hanzi-writer-data@latest/"
                + encodeURIComponent(character) + ".json";

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("HTTP " + response.status);
                    }
                    return response.json();
                })
                .then(data => done({data: data, url: url}))
                .catch(error => done({error: String(error)}));
            """,
            character
        )

        assert "error" not in result, (
            f"Không tải được dữ liệu chuẩn bị test: {result}"
        )

        data = result["data"]
        assert data.get("medians"), "Dữ liệu chữ thiếu medians."
        assert len(data["medians"]) == len(data["strokes"])

        click_button("Tự viết")

        canvas = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                'svg[width="260"][height="260"]'
            ))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView("
            "{block: 'center', inline: 'center', behavior: 'instant'});",
            canvas
        )

        # Chờ toàn bộ vùng vẽ nằm trong viewport.
        wait.until(
            lambda browser: browser.execute_script(
                """
                const r = arguments[0].getBoundingClientRect();
                return r.left >= 0 && r.top >= 0
                    && r.right <= window.innerWidth
                    && r.bottom <= window.innerHeight;
                """,
                canvas
            )
        )

        # Xác nhận dữ liệu đầu vào khớp dữ liệu chữ đang render.
        matches = driver.execute_script(
            """
            const paths = Array.from(
                arguments[0].querySelectorAll("path")
            );
            return paths.some(
                path => path.getAttribute("d") === arguments[1]
            );
            """,
            canvas,
            data["strokes"][0]
        )
        assert matches, "Dữ liệu nét tải về không khớp chữ trên giao diện."

        print(
            f"\n{case_id}: chuẩn bị vẽ chữ {character}, "
            f"{len(data['medians'])} nét"
        )

        for stroke_number, median in enumerate(data["medians"], start=1):
            assert len(median) >= 2

            # Hanzi Writer dùng hệ tọa độ dữ liệu 1024 đơn vị,
            # trục Y hướng lên và mốc trên tại Y=900.
            # Kích thước 260, padding 10 lấy từ WritingClient.
            points = driver.execute_script(
                """
                const svg = arguments[0];
                const median = arguments[1];
                const width = Number(svg.getAttribute("width"));
                const height = Number(svg.getAttribute("height"));
                const padding = 10;
                const scale = Math.min(
                    width - 2 * padding,
                    height - 2 * padding
                ) / 1024;

                const offsetX = (width - 1024 * scale) / 2;
                const offsetY = (height - 1024 * scale) / 2;
                const matrix = svg.getScreenCTM();
                const rect = svg.getBoundingClientRect();

                return median.map(([x, y]) => {
                    const point = svg.createSVGPoint();
                    point.x = offsetX + x * scale;
                    point.y = offsetY + (900 - y) * scale;

                    const screen = point.matrixTransform(matrix);
                    const px = Math.round(screen.x);
                    const py = Math.round(screen.y);

                    if (
                        px <= rect.left || px >= rect.right
                        || py <= rect.top || py >= rect.bottom
                        || px < 0 || px >= window.innerWidth
                        || py < 0 || py >= window.innerHeight
                    ) {
                        throw new Error(
                            "Điểm vẽ ngoài vùng hợp lệ: " + px + "," + py
                        );
                    }

                    return [px, py];
                });
                """,
                canvas,
                median
            )

            # Di chuyển chuột bằng tọa độ tuyệt đối trong viewport.
            actions = ActionBuilder(driver, duration=80)
            pointer = actions.pointer_action

            pointer.move_to_location(points[0][0], points[0][1])
            pointer.pointer_down()

            for x, y in points[1:]:
                pointer.move_to_location(x, y)

            pointer.pointer_up()
            pointer.pause(0.3)
            actions.perform()

            print(f"Đã vẽ nét {stroke_number}/{len(data['medians'])}")

        # Kiểm tra kết quả qua giao diện, không sửa tiến độ.
        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//span[normalize-space(.)="1/20"]'
            ))
        )

        wait.until(
            lambda browser: browser.find_element(
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-2"
            ).text.strip() == second_word
        )

        assert driver.find_element(
            By.XPATH,
            '//button[normalize-space(.)="Trước"]'
        ).is_enabled()

        driver.save_screenshot(f"{case_id}-pass.png")

        print(
            f"\n{case_id}: vẽ {len(data['medians'])} nét của {character}; "
            f"hoàn thành 1/20; tự chuyển sang {second_word}"
        )
        print(f"Dữ liệu nét dùng cho test: {result['url']}")

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