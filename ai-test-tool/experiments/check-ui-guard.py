"""Kiểm tra UI từ chối Selenium trước khi có Neon test branch; không chạy HSK."""
import json
import os
from pathlib import Path
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

tool = Path(__file__).resolve().parents[1]
evidence = tool / 'experiments' / '2026-10-19'
evidence.mkdir(parents=True, exist_ok=True)
os.environ['SE_CACHE_PATH'] = str(tool / 'data' / 'selenium-cache')
def api(route):
    with urllib.request.urlopen('http://localhost:4317' + route) as response:
        return json.load(response)
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--window-size=1440,1000')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)
try:
    driver.get('http://localhost:4317')
    wait.until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, '#group option')) == 3)
    driver.find_element(By.CSS_SELECTOR, '[data-engine="selenium"]').click()
    Select(driver.find_element(By.ID, 'group')).select_by_value('selenium-notebook')
    before = {run['id'] for run in api('/api/runs')}
    driver.find_element(By.ID, 'run-button').click()
    def blocked(browser):
        runs = [run for run in api('/api/runs') if run['id'] not in before and run['groupId'] == 'selenium-notebook']
        if runs and runs[0]['status'] != 'running':
            return runs[0]
        return False
    summary = wait.until(blocked)
    run = api('/api/runs/' + summary['id'])
    wait.until(lambda browser: 'Chưa có môi trường HSK kiểm thử' in browser.find_element(By.ID, 'result-content').text)
    assert run['status'] == 'error' and 'report' not in run and 'command' not in run
    assert 'database website hiện tại' in run['error']
    driver.save_screenshot(str(evidence / 'selenium-test-environment-required.png'))
    invalid = evidence / 'invalid-junit.xml'
    invalid.write_text('<testsuite><testcase></testsuite>', encoding='utf-8')
    count = len(api('/api/runs'))
    driver.find_element(By.ID, 'xml-file').send_keys(str(invalid))
    wait.until(lambda browser: 'XML không hợp lệ' in browser.find_element(By.ID, 'toast').text)
    assert len(api('/api/runs')) == count
    output = {'checkedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()), 'selenium':{'runId':run['id'],'group':'selenium-notebook','actualStatus':run['status'],'expected':'Từ chối trước khi tạo tiến trình pytest khi chưa có HSK kiểm thử','passed':True,'pytestStarted':False,'websiteDatabaseTouched':False,'xmlCreated':False,'error':run['error'],'reasonForNotRunning85':'Chưa có URL Neon branch kiểm thử; không được phép dùng database website hiện tại.'}, 'invalidXml':{'expected':'Hiển thị lỗi, không thêm lịch sử giả','actual':'XML không hợp lệ; số lần chạy giữ nguyên','passed':True}}
    (evidence / 'ui-guard.json').write_text(json.dumps(output, ensure_ascii=False, indent=2),encoding='utf-8')
    print(json.dumps(output,ensure_ascii=False))
finally:
    driver.quit()
