"""Đối chiếu Vitest bằng lệnh và bằng UI. Không kết nối database HSK."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

tool = Path(__file__).resolve().parents[1]
repo = tool.parent
evidence = tool / 'experiments' / '2026-10-19'
evidence.mkdir(parents=True, exist_ok=True)
frontend = repo / 'hsk-app' / 'frontend'
before = hashlib.sha256((frontend / '.env.local').read_bytes()).hexdigest()
def read_api(route):
    with urllib.request.urlopen('http://localhost:4317' + route, timeout=20) as response:
        return json.load(response)

def reference(xml):
    cases = []
    for case in ET.fromstring(xml).iter('testcase'):
        status = 'error' if case.find('error') is not None else 'failed' if case.find('failure') is not None else 'skipped' if case.find('skipped') is not None else 'passed'
        cases.append({'name': case.get('name', ''), 'classname': case.get('classname', ''), 'status': status})
    return sorted(cases, key=lambda item: (item['classname'], item['name'], item['status']))

cli_xml = evidence / 'vitest-cli.xml'
args = ['node', str(frontend / 'node_modules' / 'vitest' / 'vitest.mjs'), 'run', '--config', str(frontend / 'vitest.config.mts'), 'tests/whitebox/core.test.ts', 'tests/whitebox/gate.test.ts', '--reporter=default', '--reporter=junit', f'--outputFile={cli_xml}']
started = time.perf_counter()
result = subprocess.run(args, cwd=frontend, capture_output=True, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
cli_seconds = time.perf_counter() - started
(evidence / 'vitest-cli.log').write_text(result.stdout + result.stderr, encoding='utf-8')
assert result.returncode == 0
cli_cases = reference(cli_xml.read_text(encoding='utf-8'))

os.environ['SE_CACHE_PATH'] = str(tool / 'data' / 'selenium-cache')
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--window-size=1440,1000')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 60)
try:
    driver.get('http://localhost:4317')
    wait.until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, '#group option')) == 3)
    previous = {run['id'] for run in read_api('/api/runs')}
    interaction_start = time.perf_counter()
    Select(driver.find_element(By.ID, 'group')).select_by_value('vitest-all')
    driver.find_element(By.ID, 'run-button').click()
    select_click_seconds = time.perf_counter() - interaction_start
    def complete(_):
        matches = [run for run in read_api('/api/runs') if run['id'] not in previous and run['groupId'] == 'vitest-all']
        if matches and matches[0]['status'] != 'running':
            return matches[0]
        return False
    summary = wait.until(complete)
    run = read_api('/api/runs/' + summary['id'])
    wait.until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, '.case')) == 22)
    completed_seconds = time.perf_counter() - interaction_start
    collection_start = time.perf_counter()
    dom_cases = sorted([{'name': case.find_element(By.CSS_SELECTOR, '.case-name').text, 'status': case.find_element(By.CSS_SELECTOR, '.badge').text} for case in driver.find_elements(By.CSS_SELECTOR, '.case')], key=lambda item:item['name'])
    collection_seconds = time.perf_counter() - collection_start
    xml = (tool / 'data' / 'runs' / run['id'] / 'report.xml').read_text(encoding='utf-8')
    (evidence / 'vitest-ui.xml').write_text(xml, encoding='utf-8')
    (evidence / 'vitest-ui.log').write_text(read_api('/api/runs/' + run['id'] + '/log')['log'], encoding='utf-8')
    ui_cases = reference(xml)
    api_cases = sorted([{key:case[key] for key in ['name','classname','status']} for case in run['report']['cases']], key=lambda item:(item['classname'], item['name'], item['status']))
    assert cli_cases == ui_cases == api_cases
    assert all(case['status'] == 'PASS' for case in dom_cases)
    assert sorted(case['name'] for case in dom_cases) == sorted(case['name'] for case in ui_cases)
    assert run['report']['summary'] == {'total':22,'passed':22,'failed':0,'error':0,'skipped':0}
    driver.save_screenshot(str(evidence / 'vitest-ui.png'))
    after = hashlib.sha256((frontend / '.env.local').read_bytes()).hexdigest()
    assert before == after
    outcome = {
      'checkedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'group':'vitest-all', 'databaseRequired':False,
      'cli':{'exitCode':result.returncode,'processWallSeconds':cli_seconds,'reportedTestSeconds':float(ET.fromstring(cli_xml.read_text(encoding='utf-8')).get('time','0')),'total':len(cli_cases),'passed':sum(c['status']=='passed' for c in cli_cases)},
      'ui':{'runId':run['id'],'runnerWallSeconds':run['duration'],'reportedTestSeconds':run['report']['duration'],'automatedSelectAndClickSeconds':select_click_seconds,'automatedUntilDisplayedSeconds':completed_seconds,'automatedCollectDomSeconds':collection_seconds,'summary':run['report']['summary']},
      'perCaseResultsIdentical':True,'independentXmlParser':'Python ElementTree','uiMatchesOriginalXml':True,'websiteEnvUnchanged':before==after,
      'timingLimit':'Một lần mỗi cách, không đo thời gian thao tác của người dùng. Khác biệt có thể do cache, khởi động và chu kỳ polling; không kết luận giao diện làm test nhanh hơn.',
    }
    (evidence / 'cli-ui-comparison.json').write_text(json.dumps(outcome, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(outcome,ensure_ascii=False))
finally:
    driver.quit()
