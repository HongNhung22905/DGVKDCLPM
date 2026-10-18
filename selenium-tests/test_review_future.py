import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_future_cards_excluded_after_reload():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(15)
    wait = WebDriverWait(driver, 30)

    case_id = "REVIEW-07"
    base_url = "http://localhost:3000"
    email = f"review.future.{uuid.uuid4().hex[:12]}@example.com"

    def visible_text(tag, text):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
            ))
        )

    def click_button(label):
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f'//button[normalize-space(.)="{label}"]',
            ))
        ).click()

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
        ).send_keys("Kiểm thử Lọc thẻ tương lai")

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

        # Khởi tạo 20 thẻ qua giao diện Flashcard.
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

        # Đánh giá toàn bộ 20 thẻ là Đã thuộc.
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
            assert word not in seen_words, (
                f"Thẻ lặp dù tất cả đều chọn Đã thuộc: {word}"
            )
            seen_words.add(word)

            click_button("Lật thẻ")

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[.//p[normalize-space(.)="Đã thuộc"]]',
                ))
            ).click()

        visible_text("h2", "Ôn tập xong!")
        assert len(seen_words) == 20

        # Tránh kết luận sai nếu lần chạy đi qua nửa đêm.
        assert local_today() == session_date, (
            "Ngày local đã đổi trong lúc chạy; cần chạy lại "
            "để kiểm tra cùng một ngày."
        )

        # Chờ các thao tác lưu nền hoàn thành.
        # Chỉ đọc dữ liệu; không sửa lịch ôn bằng API.
        def all_cards_scheduled_in_future(browser):
            return browser.execute_async_script(
                """
                const date = arguments[0];
                const done = arguments[arguments.length - 1];

                fetch("/api/review?date=" + encodeURIComponent(date), {
                    credentials: "include",
                    cache: "no-store"
                })
                    .then(async response => {
                        if (!response.ok) {
                            done(false);
                            return;
                        }

                        const data = await response.json();
                        const allCards = data.allCards;
                        const dueCards = data.cards;

                        done(
                            Array.isArray(allCards)
                            && Array.isArray(dueCards)
                            && allCards.length === 20
                            && dueCards.length === 0
                            && new Set(
                                allCards.map(card => card.wordId)
                            ).size === 20
                            && allCards.every(card =>
                                typeof card.nextReview === "string"
                                && card.nextReview > date
                            )
                        );
                    })
                    .catch(() => done(false));
                """,
                session_date,
            ) is True

        wait.until(all_cards_scheduled_in_future)

        driver.save_screenshot("REVIEW-07-before-reload.png")

        # Tải lại để ứng dụng nạp lại danh sách từ server.
        driver.refresh()

        heading = visible_text("h2", "Xong rồi!")
        panel = heading.find_element(By.XPATH, "..")

        message = panel.find_element(
            By.CSS_SELECTOR, "p.text-sm.mb-6"
        ).text

        assert (
            f"Không có từ nào cần ôn hôm nay ({session_date})."
            in message
        ), message

        assert not driver.find_elements(
            By.CSS_SELECTOR,
            "p.hanzi.font-bold.mb-4",
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

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//a[normalize-space(.)="Học bài mới"]',
            ))
        )

        driver.save_screenshot(f"{case_id}-pass.png")

        print(
            f"\n{case_id}: đánh giá Đã thuộc đủ 20 thẻ; "
            "server giữ 20 thẻ có nextReview sau hôm nay, "
            "danh sách đến hạn rỗng; tải lại hiển thị "
            "không có từ cần ôn, không còn thẻ đánh giá"
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