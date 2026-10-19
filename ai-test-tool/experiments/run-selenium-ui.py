"""Chạy một nhóm Selenium qua UI trên HSK test đã có marker, lưu minh chứng."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

parser = argparse.ArgumentParser()
parser.add_argument('--group', choices=['selenium-notebook', 'selenium-all'], default='selenium-notebook')
args = parser.parse_args()
expected = 10 if args.group == 'selenium-notebook' else 85
tool = Path(__file__).resolve().parents[1]
repo = tool.parent
artifact = tool / 'experiments' / '2026-10-19' / (args.group + '-' + time.strftime('%H%M%S', time.gmtime()))
artifact.mkdir(parents=True, exist_ok=True)
env_hash = hashlib.sha256((repo / 'hsk-app' / 'frontend' / '.env.local').read_bytes()).hexdigest()
os.environ['SE_CACHE_PATH'] = str(tool / 'data' / 'selenium-cache')
def api(route, method='GET'):
    request = urllib.request.Request('http://localhost:4317' + route, data=b'{}' if method == 'POST' else None, headers={'Content-Type':'application/json'}, method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--window-size=1440,1100')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 45)
run_id = None
finished = False
started = time.perf_counter()
try:
    driver.get('http://localhost:4317')
    wait.until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, '#group option')) == 3)
    before = {run['id'] for run in api('/api/runs')}
    click_started = time.perf_counter()
    driver.find_element(By.CSS_SELECTOR, '[data-engine="selenium"]').click()
    Select(driver.find_element(By.ID, 'group')).select_by_value(args.group)
    driver.find_element(By.ID, 'run-button').click()
    click_seconds = time.perf_counter() - click_started
    def find_new(_):
        matches = [run for run in api('/api/runs') if run['id'] not in before and run['groupId'] == args.group]
        return matches[0] if matches else False
    summary = wait.until(find_new)
    run_id = summary['id']
    print(json.dumps({'event':'started','runId':run_id,'group':args.group,'artifact':str(artifact.relative_to(repo))}), flush=True)
    deadline = time.monotonic() + (1850 if expected == 10 else 7250)
    next_progress = time.monotonic() + 25
    while time.monotonic() < deadline:
        run = api('/api/runs/' + run_id)
        if run['status'] != 'running':
            finished = True
            break
        if time.monotonic() >= next_progress:
            print(json.dumps({'event':'running','runId':run_id,'elapsedSeconds':round(time.perf_counter()-started)}),flush=True)
            next_progress = time.monotonic() + 25
        time.sleep(2)
    if not finished:
        raise TimeoutError('Runner did not finish before experiment deadline')
    (artifact / 'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2),encoding='utf-8')
    (artifact / 'output.log').write_text(api('/api/runs/' + run_id + '/log')['log'],encoding='utf-8')
    reference=[]
    if run.get('reportFile'):
        with urllib.request.urlopen('http://localhost:4317/api/runs/' + run_id + '/xml') as response:
            xml=response.read()
        (artifact / 'report.xml').write_bytes(xml)
        for case in ET.fromstring(xml).iter('testcase'):
            status='error' if case.find('error') is not None else 'failed' if case.find('failure') is not None else 'skipped' if case.find('skipped') is not None else 'passed'
            reference.append({'name':case.get('name','Không có tên'),'classname':case.get('classname',''),'status':status})
    sort=lambda items:sorted(items,key=lambda item:(item['classname'],item['name'],item['status']))
    actual=[{key:case[key] for key in ['name','classname','status']} for case in run.get('report',{}).get('cases',[])]
    matches=bool(run.get('reportFile')) and sort(reference)==sort(actual)
    wait.until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, '#run-header .badge.running')) == 0)
    driver.save_screenshot(str(artifact / 'ui-result.png'))
    driver.find_element(By.CSS_SELECTOR, '[data-tab="log"]').click()
    driver.save_screenshot(str(artifact / 'ui-log.png'))
    summary={'checkedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'group':args.group,'runId':run_id,'expectedCollectedCases':expected,'runStatus':run['status'],'summary':run.get('report',{}).get('summary'),'runnerWallSeconds':run['duration'],'reportedTestSeconds':run.get('report',{}).get('duration'),'automatedSelectClickSeconds':click_seconds,'automatedOverallSeconds':time.perf_counter()-started,'referenceParser':'Python ElementTree','apiMatchesOriginalXml':matches,'caseCountMatchesExpected':len(reference)==expected,'websiteEnvUnchanged':env_hash==hashlib.sha256((repo/'hsk-app'/'frontend'/'.env.local').read_bytes()).hexdigest(),'error':run.get('error'),'artifactDirectory':str(artifact.relative_to(repo)).replace('\\','/')}
    (artifact / 'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False),flush=True)
    if run['status']!='passed' or not matches or len(reference)!=expected:
        raise SystemExit(1)
finally:
    if run_id and not finished:
        try:
            api('/api/runs/' + run_id + '/cancel',method='POST')
        except Exception:
            pass
    driver.quit()
