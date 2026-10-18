import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_account_data_isolation():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(15)
    wait = WebDriverWait(driver, 30)
    base = 'http://localhost:3000'
    case_id = 'DATA-UI-01'
    suffix = uuid.uuid4().hex[:12]
    password = '1234567'
    accounts = {
        'A': (f'isolation.a.{suffix}@example.com', 'Kiem thu Tai khoan A'),
        'B': (f'isolation.b.{suffix}@example.com', 'Kiem thu Tai khoan B'),
    }

    def visible(tag, text):
        return wait.until(EC.visibility_of_element_located((
            By.XPATH, f'//{tag}[normalize-space(.)="{text}"]',
        )))

    def click(xpath):
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    def today():
        return driver.execute_script('''
            const d = new Date(), pad = n => String(n).padStart(2, '0');
            return d.getFullYear() + '-' + pad(d.getMonth()+1)
                + '-' + pad(d.getDate());
        ''')

    def api(path):
        r = driver.execute_async_script('''
            const done = arguments[arguments.length-1];
            fetch(arguments[0], {credentials:'include', cache:'no-store'})
                .then(async r => done({status:r.status, body:await r.json()}))
                .catch(e => done({error:String(e)}));
        ''', path)
        assert 'error' not in r, r
        assert r['status'] == 200, r
        return r['body']

    def menu(key):
        name = accounts[key][1]
        return f'//nav//button[.//span[normalize-space(.)="{name}"]]'

    def register(key):
        email, name = accounts[key]
        driver.get(base + '/register')
        wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, 'input[placeholder="Nguyễn Văn A"]',
        ))).send_keys(name)
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(email)
        driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Ít nhất 6 ký tự"]').send_keys(password)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        wait.until(EC.url_contains('/vocabulary'))
        wait.until(EC.element_to_be_clickable((By.XPATH, menu(key))))

    def logout(key):
        click(menu(key))
        click('//nav//button[normalize-space(.)="Đăng xuất"]')
        wait.until(EC.visibility_of_element_located((
            By.XPATH, '//nav//a[@href="/login" and normalize-space(.)="Đăng nhập"]',
        )))

    def check_stats(key, populated):
        driver.get(base + '/stats')
        visible('h1', 'Thống kê ôn tập')
        expected = {
            'Chuỗi ngày': '1 ngày' if populated else '0 ngày',
            'Từ đã ôn': '20' if populated else '0',
            'Điểm TB': '100%' if populated else '0%',
            'Ngày đã học': '1 ngày' if populated else '0 ngày',
            'Tổng thẻ đang ôn': '20' if populated else '0',
            'Cần ôn hôm nay': '0',
            'Đã ôn ngày mai trở đi': '20' if populated else '0',
        }
        for label, value in expected.items():
            locator = (By.XPATH, f'//p[normalize-space(.)="{label}"]/../p[contains(@class,"text-2xl")]')
            wait.until(lambda browser, loc=locator, val=value:
                       browser.find_element(*loc).text.strip() == val,
                       message=f'{key}: sai chỉ số {label}')
        data = api('/api/review/history?days=119&date=' + session_date)
        assert data['stats']['totalSessions'] == (1 if populated else 0), data
        assert data['stats']['allCards'] == (20 if populated else 0), data
        if populated:
            assert data['daily'] == saved_daily, 'Lịch sử A bị thay đổi.'
            heading = visible('h2', 'Lịch sử phiên ôn tập')
            panel = heading.find_element(By.XPATH, './ancestor::div[contains(@class,"rounded-2xl")][1]')
            rows = panel.find_elements(By.CSS_SELECTOR, 'div.flex.items-center.px-5.py-3')
            assert len(rows) == 1
            for value in ('20 từ', '100%', '20/20'):
                assert rows[0].find_element(By.XPATH, f'.//span[normalize-space(.)="{value}"]').is_displayed()
        else:
            assert data['daily'] == [], 'B nhận lịch sử của tài khoản khác.'
            visible('p', 'Chưa có dữ liệu ôn tập')
            assert not driver.find_elements(By.XPATH, '//h2[normalize-space(.)="Lịch sử phiên ôn tập"]')
        click(menu(key))
        visible('p', accounts[key][0])
        click(menu(key))
        assert today() == session_date, 'Ngày thay đổi trong khi chạy; cần chạy lại.'
        driver.save_screenshot(f'{case_id}-{key}-stats.png')
        print(f'\n{case_id}: tài khoản {key} có đúng dữ liệu riêng')

    try:
        register('A')
        session_date = today()
        driver.get(base + '/vocabulary/flashcard/new-1-lesson-1')
        visible('span', '1/20')

        def ready(browser):
            data = api('/api/review?date=' + session_date)
            return len(data.get('cards', [])) == 20

        wait.until(ready)
        driver.get(base + '/review')
        seen = set()
        for i in range(20):
            visible('span', f'{i}/20 từ')
            flip = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//button[normalize-space(.)="Lật thẻ"]',
            )))
            word = driver.find_element(By.CSS_SELECTOR, 'p.hanzi.font-bold.mb-4').text.strip()
            assert word and word not in seen
            seen.add(word)
            flip.click()
            click('//button[.//p[normalize-space(.)="Đã thuộc"]]')
        visible('h2', 'Ôn tập xong!')

        def saved(browser):
            data = api('/api/review/history?days=119&date=' + session_date)
            assert data['stats']['totalSessions'] <= 1
            return data if (data['stats']['totalSessions'] == 1
                            and data['stats']['allCards'] == 20
                            and data['stats']['dueToday'] == 0) else False

        history = wait.until(saved)
        saved_daily = history['daily']
        assert len(saved_daily) == 1
        assert saved_daily[0]['date'] == session_date
        assert saved_daily[0]['totalCards'] == 20
        assert saved_daily[0]['correctCards'] == 20
        assert saved_daily[0]['score'] == 100
        check_stats('A', True)
        logout('A')

        register('B')
        check_stats('B', False)
        driver.refresh()
        visible('p', 'Chưa có dữ liệu ôn tập')
        logout('B')

        driver.get(base + '/login')
        visible('h1', 'Đăng nhập')
        driver.find_element(By.CSS_SELECTOR, 'form input[type="email"]').send_keys(accounts['A'][0])
        driver.find_element(By.CSS_SELECTOR, 'form input[type="password"]').send_keys(password)
        driver.find_element(By.CSS_SELECTOR, 'form button[type="submit"]').click()
        wait.until(EC.element_to_be_clickable((By.XPATH, menu('A'))))
        wait.until(lambda browser: browser.current_url.split('?')[0].rstrip('/') != base + '/login')
        check_stats('A', True)
        driver.save_screenshot(f'{case_id}-pass.png')
        print(f'\n{case_id}: PASS — A có phiên 20/20; B có 0 thẻ và không có lịch sử; quay lại A vẫn giữ dữ liệu')
    except Exception:
        try:
            driver.save_screenshot(f'{case_id}-fail.png')
        except Exception as error:
            print(f'Không chụp được ảnh: {error}')
        raise
    finally:
        driver.quit()
