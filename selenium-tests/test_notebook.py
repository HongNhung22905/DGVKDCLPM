import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE = 'http://localhost:3000'
GRID = 'div.grid.grid-cols-1.sm\\:grid-cols-2.gap-3 > div'


@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(15)
    wait = WebDriverWait(driver, 30)
    try:
        driver.get(BASE + '/register')
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
            'input[placeholder="Nguyễn Văn A"]'))).send_keys('Kiem thu So tay')
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(
            f'notebook.{uuid.uuid4().hex[:12]}@example.com')
        driver.find_element(By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]').send_keys('1234567')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        wait.until(EC.url_contains('/vocabulary'))
        # Quan sát các request lưu thật, không sửa request/response.
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                window.__notebookWrites = [];
                const original = window.fetch;
                window.fetch = async function(...args) {
                    const raw = typeof args[0] === 'string' ? args[0] : args[0].url;
                    const url = new URL(raw, location.href);
                    const method = (args[1]?.method || args[0]?.method || 'GET').toUpperCase();
                    const response = await original.apply(this,args);
                    if (url.pathname === '/api/user/notebook' && method !== 'GET') {
                        window.__notebookWrites.push({method, status:response.status});
                    }
                    return response;
                };
            '''
        })
        yield driver
    finally:
        driver.quit()


def wait(driver):
    return WebDriverWait(driver, 30)


def visible(driver, tag, text):
    return wait(driver).until(EC.visibility_of_element_located((
        By.XPATH, f'//{tag}[normalize-space(.)="{text}"]')))


def entries(driver):
    result = driver.execute_async_script('''
        const done = arguments[arguments.length-1];
        fetch('/api/user/notebook', {credentials:'include',cache:'no-store'})
            .then(async r=>done({status:r.status,body:await r.json()}))
            .catch(e=>done({error:String(e)}));
    ''')
    assert 'error' not in result, result
    assert result['status'] == 200, result
    assert isinstance(result['body'].get('entries'), list), result
    return result['body']['entries']


def target(driver):
    for card in driver.find_elements(By.CSS_SELECTOR, GRID):
        if card.find_element(By.CSS_SELECTOR, 'span.font-black').text.strip() == '的':
            return card
    return False


def open_search(driver):
    driver.get(BASE + '/search?q=的')
    wait(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
        'input[placeholder="Ví dụ: 你好, nihao, xin chào..."]')))
    return wait(driver).until(target)


def write_count(driver):
    return driver.execute_script('return window.__notebookWrites.length;')


def wait_write(driver, method, since):
    def complete(browser):
        records = browser.execute_script('return window.__notebookWrites;')
        for record in records[since:]:
            if record['method'] == method:
                assert 200 <= record['status'] < 300, record
                return True
        return False
    wait(driver).until(complete, message=f'Không nhận response lưu {method}.')


def save_from_search(driver):
    card = wait(driver).until(target)
    button = card.find_element(By.CSS_SELECTOR, 'button[title="Lưu vào sổ tay"]')
    since = write_count(driver)
    button.click()
    wait_write(driver, 'POST', since)
    wait(driver).until(lambda b: target(b).find_element(By.CSS_SELECTOR,
        'button[title="Bỏ lưu"]').is_displayed())
    wait(driver).until(lambda b: len(entries(b)) == 1)
    data = entries(driver)
    assert data[0]['simplified'] == '的'
    return data[0]


def open_notebook(driver, empty=False):
    driver.get(BASE + '/notebook')
    wait(driver).until(EC.visibility_of_element_located((By.XPATH,
        '//h1[normalize-space(.)="Sổ tay của tôi"]')))
    wait(driver).until(EC.invisibility_of_element_located((By.CSS_SELECTOR,
        'svg.animate-spin')))
    if empty:
        visible(driver, 'p', 'Sổ tay trống')
        assert not driver.find_elements(By.CSS_SELECTOR, GRID)
        return None
    card = wait(driver).until(target)
    assert len(driver.find_elements(By.CSS_SELECTOR, GRID)) == 1
    visible(driver, 'p', '1 từ đã lưu · ghi chú cá nhân · ôn tập nhanh')
    return card


def edit_note(driver, text):
    card = wait(driver).until(target)
    card.find_element(By.CSS_SELECTOR, 'button[title="Ghi chú"]').click()
    area = wait(driver).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
        'textarea[placeholder="Thêm ghi chú, ví dụ, ngữ cảnh..."]')))
    area.clear()
    area.send_keys(text)
    since = write_count(driver)
    card.find_element(By.XPATH, './/button[normalize-space(.)="Lưu"]').click()
    wait_write(driver, 'PATCH', since)
    wait(driver).until(lambda b: len(entries(b)) == 1 and entries(b)[0].get('note') == text)
    note = wait(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
        'div.grid div.border-l-2')))
    assert note.text == text


@pytest.mark.parametrize('case_id', ['NOTE-01','NOTE-02','NOTE-03','NOTE-04','NOTE-05'],
                         ids=lambda value: value)
def test_notebook(browser, case_id):
    driver = browser
    try:
        open_search(driver)
        assert entries(driver) == [], 'Tài khoản mới có sẵn dữ liệu sổ tay.'

        if case_id == 'NOTE-02':
            # Hai trang cùng thấy trạng thái chưa lưu, rồi lần lượt lưu
            # cùng một từ bằng UI. Không dùng nút Bỏ lưu như thao tác thêm.
            first_tab = driver.current_window_handle
            driver.switch_to.new_window('tab')
            second_tab = driver.current_window_handle
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                window.__notebookWrites = [];
                const original = window.fetch;
                window.fetch = async function(...args) {
                    const raw = typeof args[0] === 'string' ? args[0] : args[0].url;
                    const url = new URL(raw, location.href);
                    const method = (args[1]?.method || args[0]?.method || 'GET').toUpperCase();
                    const response = await original.apply(this,args);
                    if (url.pathname === '/api/user/notebook' && method !== 'GET') {
                        window.__notebookWrites.push({method, status:response.status});
                    }
                    return response;
                };
            '''
            })
            open_search(driver)
            target(driver).find_element(By.CSS_SELECTOR, 'button[title="Lưu vào sổ tay"]')
            driver.switch_to.window(first_tab)
            original = save_from_search(driver)
            driver.switch_to.window(second_tab)
            save_from_search(driver)
            data = entries(driver)
            assert len(data) == 1
            assert data[0]['wordId'] == original['wordId']
            open_notebook(driver)
            driver.refresh()
            wait(driver).until(target)
            assert len(entries(driver)) == 1
            assert len(driver.find_elements(By.CSS_SELECTOR, GRID)) == 1
            message = 'Lưu cùng từ từ hai trang không tạo bản ghi trùng.'

        else:
            original = save_from_search(driver)
            card = open_notebook(driver)
            assert card.find_element(By.CSS_SELECTOR, 'p.text-base.font-semibold').text.strip() == original['pinyin']

            if case_id == 'NOTE-01':
                driver.refresh()
                wait(driver).until(target)
                assert len(entries(driver)) == 1
                assert entries(driver)[0]['wordId'] == original['wordId']
                message = 'Thêm từ 的 thành công; tải lại vẫn có đúng một từ.'

            elif case_id == 'NOTE-03':
                edit_note(driver, 'Ghi chú ban đầu')
                revised = 'Ghi chú đã sửa: của tôi — 我的'
                edit_note(driver, revised)
                driver.refresh()
                card = wait(driver).until(target)
                note = wait(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                    'div.grid div.border-l-2')))
                assert note.text == revised
                assert entries(driver)[0]['note'] == revised
                card.find_element(By.CSS_SELECTOR, 'button[title="Ghi chú"]').click()
                area = wait(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'textarea')))
                assert area.get_attribute('value') == revised
                card.find_element(By.XPATH, './/button[normalize-space(.)="Huỷ"]').click()
                message = 'Sửa ghi chú; server và giao diện giữ nội dung sau tải lại.'

            elif case_id == 'NOTE-04':
                since = write_count(driver)
                card.find_element(By.CSS_SELECTOR, 'button[title="Xóa khỏi sổ tay"]').click()
                wait_write(driver, 'DELETE', since)
                wait(driver).until(lambda b: entries(b) == [])
                visible(driver, 'p', 'Sổ tay trống')
                open_notebook(driver, empty=True)
                assert entries(driver) == []
                open_search(driver)
                assert target(driver).find_element(By.CSS_SELECTOR,
                    'button[title="Lưu vào sổ tay"]').is_displayed()
                driver.get(BASE + '/notebook')
                visible(driver, 'p', 'Sổ tay trống')
                message = 'Xóa từ; tải trang lại vẫn trống; trang tra từ trở về chưa lưu.'

            else:
                payload = '<img src=x onerror="window.__noteExecuted=1"><script>window.__noteExecuted=1</script>'
                edit_note(driver, payload)
                for reload_page in (False, True):
                    if reload_page:
                        driver.refresh()
                    card = wait(driver).until(target)
                    note = wait(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                        'div.grid div.border-l-2')))
                    assert note.text == payload
                    assert not note.find_elements(By.CSS_SELECTOR, 'img,script')
                    assert driver.execute_script('return window.__noteExecuted || 0;') == 0
                    assert entries(driver)[0]['note'] == payload
                message = 'Chuỗi HTML/script hiện nguyên văn; không tạo thẻ hay thực thi trước/sau tải lại.'

        driver.save_screenshot(f'{case_id}-pass.png')
        print(f'\n{case_id}: PASS — {message}')
    except Exception:
        try:
            driver.save_screenshot(f'{case_id}-fail.png')
        except Exception as error:
            print(f'Không chụp được ảnh: {error}')
        raise
