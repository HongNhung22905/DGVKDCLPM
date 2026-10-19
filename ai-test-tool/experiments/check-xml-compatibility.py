"""Đối chiếu parser công cụ với Python ElementTree trên cùng 70 XML gốc."""
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

tool = Path(__file__).resolve().parents[1]
repo = tool.parent
files = sorted((repo / 'selenium-tests').glob('*.xml')) + [repo / 'hsk-app' / 'frontend' / 'whitebox-results.xml']
script = """
import {readFile} from 'node:fs/promises';
import {parseJUnit} from './ai-test-tool/src/junit.ts';
let input='';for await(const part of process.stdin) input+=part;
const result=[];
for(const file of JSON.parse(input)) {const report=parseJUnit(await readFile(file,'utf8'));result.push({file,summary:report.summary,cases:report.cases.map(({name,classname,status})=>({name,classname,status}))});}
console.log(JSON.stringify(result));
"""
# -e truyền mã tĩnh; danh sách đường dẫn truyền qua stdin, không qua shell.
process = subprocess.run(['node','--input-type=module','-e',script],cwd=repo,input=json.dumps([str(file) for file in files]),capture_output=True,text=True,encoding='utf-8',check=True)
actual = json.loads(process.stdout)
results=[]
for file, parsed in zip(files,actual):
    content=file.read_bytes()
    expected=[]
    for case in ET.fromstring(content).iter('testcase'):
        status='error' if case.find('error') is not None else 'failed' if case.find('failure') is not None else 'skipped' if case.find('skipped') is not None else 'passed'
        expected.append({'name':case.get('name','Không có tên'),'classname':case.get('classname',''),'status':status})
    sort=lambda items:sorted(items,key=lambda item:(item['classname'],item['name'],item['status']))
    expected_summary={'total':len(expected), **{status:sum(case['status']==status for case in expected) for status in ['passed','failed','error','skipped']}}
    match=sort(expected)==sort(parsed['cases']) and expected_summary==parsed['summary']
    row={'file':str(file.relative_to(repo)).replace('\\','/'),'sha256':hashlib.sha256(content).hexdigest(),'summary':expected_summary,'missingNameCases':sum(case.get('name') is None for case in ET.fromstring(content).iter('testcase')),'allCasesAndCountsMatch':match}
    if not match:
        row['expectedCases']=sort(expected)
        row['actualCases']=sort(parsed['cases'])
        row['actualSummary']=parsed['summary']
    results.append(row)
output={'files':len(results),'totalTestcaseRecords':sum(item['summary']['total'] for item in results),'allMatch':all(item['allCasesAndCountsMatch'] for item in results),'referenceParser':'Python ElementTree','namePresentationMapping':'XML không có thuộc tính name được hiển thị bằng nhãn Không có tên; không thêm testcase.','results':results,'interpretation':'Đây là báo cáo lịch sử có thể trùng ca giữa các lần chạy, không phải 70 lần chạy mới hoặc 115 test độc lập.'}
(tool/'experiments'/'2026-10-19'/'xml-compatibility.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({key:value for key,value in output.items() if key!='results'},ensure_ascii=False))
assert output['allMatch']
