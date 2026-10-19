"""Build/check documentation from saved evidence; never execute HSK or contact a DB."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

TOOL = Path(__file__).resolve().parents[1]
REPO = TOOL.parent
EVIDENCE = TOOL / "experiments" / "2026-10-19"
TARGET = TOOL / "docs" / "TEST-TRACEABILITY.md"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(name):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8-sig"))


def cases(name):
    root = ET.parse(EVIDENCE / name).getroot()
    result = []
    for case in root.iter("testcase"):
        status = "failed" if case.find("failure") is not None else (
            "error" if case.find("error") is not None else (
                "skipped" if case.find("skipped") is not None else "passed"))
        result.append((case.get("classname", ""), case.get("name", ""), status))
    require(len(result) == len(set(result)), f"Duplicate cases: {name}")
    return result


def summary(rows):
    counts = Counter(row[2] for row in rows)
    return {"total": len(rows), "passed": counts["passed"], "failed": counts["failed"],
            "error": counts["error"], "skipped": counts["skipped"]}


def cell(value):
    return str(value).replace("|", "&#124;").replace("\n", " ")


def link(label, target):
    return f"[{label}]({target})"


def build():
    full = cases("selenium-all-122951/report.xml")
    vitest = cases("vitest-ui.xml")
    full_summary = summary(full)
    require(full_summary == {"total": 85, "passed": 75, "failed": 10, "error": 0, "skipped": 0},
            "Full run changed; review the report before regenerating")
    stored = read_json("selenium-all-122951/run.json")
    require([(c["classname"], c["name"], c["status"]) for c in stored["report"]["cases"]] == full,
            "XML and stored cases differ")
    for name in ["selenium-all-122951/summary.json", "selenium-full-results.json"]:
        require(read_json(name)["summary"] == full_summary, f"Summary mismatch: {name}")
    require(summary(vitest) == {"total": 22, "passed": 22, "failed": 0, "error": 0, "skipped": 0},
            "Vitest summary mismatch")
    require(vitest == cases("vitest-cli.xml"), "CLI/UI Vitest cases differ")
    require(cases("selenium-notebook-122623/report.xml") == cases(
        "selenium-notebook-cli-2026-10-19T12-58-44-003Z/report.xml"), "CLI/UI Selenium cases differ")
    xml_import = read_json("xml-compatibility.json")
    require(xml_import["files"] == 70 and xml_import["totalTestcaseRecords"] == 115
            and xml_import["allMatch"], "Historical XML evidence changed")
    ai = read_json("ai-judgements.json")
    ai_counts = Counter(item["classification"] for item in ai["results"])
    require(ai_counts == Counter({"đúng": 7, "đúng một phần": 3}) and len(ai["results"]) == 10,
            "Preliminary AI results changed")
    for item in ai["results"]:
        cause, action = item["causeScore"], item["actionScore"]
        require(cause in (0, 1, 2) and action in (0, 1, 2), "Invalid AI rubric scores")
        classification = "đúng" if cause == action == 2 else (
            "đúng một phần" if cause + action >= 2 else "sai")
        require(item["classification"] == classification, f"AI classification mismatch: {item['id']}")
    require(ai["summary"]["total"] == 10 and ai["summary"]["correct"] == 7
            and ai["summary"]["partlyCorrect"] == 3 and ai["summary"]["incorrect"] == 0,
            "AI summary mismatch")

    lines = ["# Truy vết yêu cầu → ca kiểm thử → kết quả → minh chứng", "",
             "Đề tài: **Kiểm thử tự động website hỗ trợ học tiếng Trung và xây dựng công cụ tích hợp AI hỗ trợ phân tích kết quả.** Website HSK là đối tượng đánh giá chính; phần công cụ là minh chứng cho sản phẩm hỗ trợ. [Bảng chốt minh chứng, phiên bản và môi trường](EVIDENCE-BASELINE.md).", "",
             "Cập nhật tài liệu **20/10/2026**, nguồn thực nghiệm **19/10/2026**. Bảng được sinh từ XML, mã test và nhật ký đã lưu, không chạy test mới. Mã yêu cầu là nhãn truy vết của báo cáo, không thay thế đặc tả nghiệp vụ hoặc chứng minh độ bao phủ toàn website.", "",
             "Chạy `python ai-test-tool/experiments/build-traceability.py --check` để đối chiếu bảng với nguồn; bỏ `--check` để sinh lại sau khi rà soát. Script dừng nếu số liệu mốc hoặc kết quả từng ca không khớp.", "",
             "## 1. Phân biệt các bộ kết quả", "",
             "| Bộ | Kết quả | Nguồn chuẩn |", "| --- | --- | --- |",
             "| Selenium lượt đầy đủ | 85 ca: 75 PASS, 10 FAIL, 0 ERROR/SKIP | [XML gốc](../experiments/2026-10-19/selenium-all-122951/report.xml), run ID `04d381c9-e06b-453e-9601-2a698141b34a` |",
             "| Logic HSK (Vitest) | 22/22 PASS mỗi cách CLI/UI | [XML UI](../experiments/2026-10-19/vitest-ui.xml), [đối chiếu](../experiments/2026-10-19/cli-ui-comparison.json) |",
             "| Selenium nhóm nhỏ, lượt khác | UI 10/10 PASS; CLI 10/10 PASS | [Đối chiếu nhóm nhỏ](../experiments/2026-10-19/selenium-cli-ui-comparison.json) |",
             "| Công cụ | 21/21 đạt | [Nhật ký 21 ca](../experiments/2026-10-19/tool-tests-after-selenium.log) |",
             "| Nhập XML lịch sử | 70/70 tệp khớp, 115 bản ghi testcase có trùng giữa các lượt | [Đối chiếu XML](../experiments/2026-10-19/xml-compatibility.json) |",
             "| AI, đánh giá sơ bộ | 10 mẫu: 7 đúng, 3 đúng một phần; chưa chấm độc lập | [Điểm sơ bộ](../experiments/2026-10-19/ai-judgements.json), [phiếu độc lập trống](AI-INDEPENDENT-REVIEW.md) |", "",
             "Không cộng các dòng thành một tổng ca đạt. Mốc 18/18 công cụ là mốc cũ, đã được thay bằng bộ 21 ca. Nhóm nhỏ là tập con chạy ở lượt khác; NOTE-04 PASS ở nhóm nhỏ không thay FAIL của lượt đầy đủ. 70 XML không phải 70 lượt chạy mới. 7/10 mẫu AI không phải độ chính xác chung.", "",
             "## 2. Yêu cầu công cụ và các ca kiểm tra", "",
             "| Yêu cầu hỗ trợ | Tiêu chí mong đợi trong phạm vi test | Test/minh chứng tương ứng | Kết quả đã lưu |",
             "| --- | --- | --- | --- |",
             "| TOOL-01 | Chỉ chạy nhóm cấu hình sẵn, từ chối ID/lệnh tùy ý | T-RUN-06; lượt UI E-S01/E-S02 trong bảng minh chứng | Test kiểm soát đạt; UI chọn/chạy được |",
             "| TOOL-02 | Chạy tối đa một nhóm, hủy/timeout dừng tiến trình và không báo PASS giả | T-RUN-01,03,04,06; E-F01 | Các ca tương ứng PASS; trạng thái hủy/timeout đúng |",
             "| TOOL-03 | Đọc đúng tên/trạng thái; từ chối XML sai; thiếu XML/exit lỗi không thành PASS | T-XML-01…07, T-RUN-01,02; E-X01; E-S02 | Test đạt; 70/70 XML khớp; 85/85 ca khớp XML |",
             "| TOOL-04 | Chọn/chạy/xem kết quả, nhật ký và mở lại lịch sử; nhập/tải XML qua API local | T-API-01; E-S01/E-S02/E-S03 | API test đạt; luồng UI và mở lại lịch sử hoạt động |",
             "| TOOL-05 | Giữ kết quả sau khi mở store mới, khôi phục lượt bị gián đoạn | T-RUN-01,05; T-API-01; E-S02 | Test đạt; lịch sử 85 ca khớp nguồn |",
             "| TOOL-06 | Không key vẫn chạy test; gọi AI theo yêu cầu, giữ kết quả test và che bí mật thông dụng | T-GEM-01…04; E-A01/E-A03 | Test đạt; HTTP 200 thật; chất lượng lời giải thích chỉ đánh giá sơ bộ |",
             "| TOOL-07 | Từ chối cấu hình thiếu/endpoint website; chỉ dùng môi trường kiểm thử riêng | T-ENV-01…03; E-F01/E-S02 | Test cấu hình đạt; endpoint khác và hash cấu hình gốc giữ nguyên |", "",
             "Mã TOOL-01…07 xem [yêu cầu trong báo cáo](EXPERIMENT-REPORT.md#2-yêu-cầu-và-thiết-kế). Các dòng dưới là 21 test top-level trong bộ công cụ. PASS được đối chiếu với tên ca và tổng trong nhật ký, không suy từ việc file mã nguồn tồn tại.", "",
             "| ID truy vết | Yêu cầu | Ca gốc | Kết quả | Nguồn test |", "| --- | --- | --- | --- | --- |"]
    tool_specs = [
        ("gemini", "GEM", ["TOOL-06"] * 4),
        ("hsk-test-environment", "ENV", ["TOOL-07"] * 3),
        ("junit", "XML", ["TOOL-03"] * 7),
        ("runner", "RUN", ["TOOL-02, TOOL-03, TOOL-05", "TOOL-03", "TOOL-02",
                              "TOOL-02", "TOOL-05", "TOOL-01, TOOL-02"]),
        ("server", "API", ["TOOL-04, TOOL-05"]),
    ]
    test_log = (EVIDENCE / "tool-tests-after-selenium.log").read_text(encoding="utf-8-sig")
    tool_count = 0
    for name, prefix, requirements in tool_specs:
        source = TOOL / "tests" / f"{name}.test.ts"
        names = re.findall(r"^test\('([^']+)'", source.read_text(encoding="utf-8-sig"), re.M)
        require(len(names) == len(requirements), f"Tool tests changed: {source.name}")
        for index, (test_name, req) in enumerate(zip(names, requirements), 1):
            require(any(line.startswith("✔ " + test_name + " (") for line in test_log.splitlines()),
                    f"No passing log entry: {test_name}")
            tool_count += 1
            lines.append(f"| T-{prefix}-{index:02} | {req} | {cell(test_name)} | PASS | "
                         f"{link(source.name, '../tests/' + source.name)} |")
    require(tool_count == 21 and re.search(r"tests 21\b", test_log)
            and re.search(r"pass 21\b", test_log) and re.search(r"fail 0\b", test_log),
            "Tool test total differs")
    lines += ["", "Minh chứng bổ sung cho TOOL-01/02/04/05: [chạy nhóm nhỏ qua UI](../experiments/2026-10-19/selenium-notebook-122623/summary.json), [lịch sử 85 ca khớp XML](../experiments/2026-10-19/selenium-dom-verification.json), [ảnh lịch sử](../experiments/2026-10-19/selenium-history-result.png), [hủy/timeout/XML hỏng/kết nối lỗi](../experiments/2026-10-19/fault-scenarios.json). TOOL-06 còn có [Gemini thật HTTP 200](../experiments/2026-10-19/selenium-gemini-analysis.json); TOOL-07 có [chặn môi trường chưa cấu hình](../experiments/2026-10-19/ui-guard.json) và [hash cấu hình giữ nguyên](../experiments/2026-10-19/verification-final.json). Các minh chứng này không được tính thêm thành test top-level.", "",
              "## 3. Yêu cầu HSK và kết quả Selenium", "",
              "Đây là hành vi được các test có sẵn kiểm tra. Mỗi file thuộc đúng một nhóm dưới đây; 9 lựa chọn Selenium trên UI gồm 8 nhóm chức năng và 1 lựa chọn toàn bộ, không phải 9 bộ độc lập.", "",
              "| Yêu cầu HSK | Tiêu chí mong đợi | Test tương ứng (tên file, bỏ tiền tố test_) | Tổng | PASS | FAIL | Lỗi |",
              "| --- | --- | --- | ---: | ---: | ---: | --- |"]
    groups = [
        ("HSK-AUTH", "Đăng ký hợp lệ/không hợp lệ, đăng nhập/đăng xuất", ["register", "login", "logout"]),
        ("HSK-VOC", "Chọn cấp, điều hướng bài/từ và thao tác flashcard", ["vocabulary", "flashcard"]),
        ("HSK-UNLOCK", "Ngưỡng điểm, thử lại, pinyin và khôi phục quyền mở khóa", ["unlock", "unlock_score", "unlock_retry", "unlock_pinyin", "unlock_session"]),
        ("HSK-REVIEW", "Thẻ đến hạn/chưa đến hạn, đánh giá và lịch sử ôn", ["review", "review_due", "review_future", "review_rate", "review_repeat", "review_history"]),
        ("HSK-PROGRESS", "Tiến độ, lịch, lưu phiên và cách ly tài khoản", ["progress", "progress_cards", "progress_completed", "stats", "stats_calendar", "stats_persistence", "stats_session", "data_isolation"]),
        ("HSK-WRITE", "Mở luyện viết, xử lý nét sai và hoàn thành chữ", ["writing", "writing_quiz", "writing_complete"]),
        ("HSK-GAME", "Chế độ chữ Hán, đáp án hỗn hợp và hoàn thành trò chơi", ["game", "game_hanzi", "game_mixed", "game_complete"]),
        ("HSK-NOTE", "Tìm kiếm và thêm/sửa/xóa sổ tay", ["search", "notebook"]),
    ]
    expected_by_req = {
        "HSK-AUTH": "Đầu vào hợp lệ tạo/đăng nhập được; email trùng và đầu vào sai bị từ chối, gồm tên rỗng sau trim; đăng xuất kết thúc phiên",
        "HSK-VOC": "Chọn HSK 1…7, hiển thị bài/hành động học đúng và quay lại được; khóa bài ban đầu, điều hướng từ và flashcard đúng kỳ vọng từng ca",
        "HSK-UNLOCK": "Đạt ngưỡng thì mở, chưa đạt thì khóa; thử lại thấp hơn không mất quyền đã đạt; xử lý pinyin và khôi phục quyền ở trình duyệt mới đúng",
        "HSK-REVIEW": "Tài khoản mới rỗng; thẻ đến hạn xuất hiện, thẻ tương lai bị loại; đánh giá/lặp thẻ và lưu lịch sử một lần đúng assertion",
        "HSK-PROGRESS": "Tiến độ/thống kê phản ánh dữ liệu học, giữ sau tải lại/đăng nhập; lịch chứa hoạt động hôm nay; dữ liệu hai tài khoản không lẫn",
        "HSK-WRITE": "Mở đúng chế độ luyện viết; nét sai không tính hoàn thành; hoàn thành chữ được ghi nhận theo ca hiện có",
        "HSK-GAME": "Mở/chơi được các chế độ; đáp án đúng/sai, điểm và kết thúc trò chơi thống nhất với ca hiện có",
        "HSK-NOTE": "Tìm/lọc từ đúng; thêm/lưu không trùng, sửa ghi chú và xóa được; API và UI thống nhất, xóa hết hiển thị sổ tay trống",
    }
    requirement_by_module = {"selenium-tests.test_" + module: req
                             for req, _, modules in groups for module in modules}
    defects = {}
    for classname, name, status in full:
        require(classname in requirement_by_module, f"Unmapped module: {classname}")
        source = REPO / "selenium-tests" / (classname.split(".")[-1] + ".py")
        require(source.is_file(), f"Missing test source: {source}")
        if status != "failed":
            continue
        if name == "test_register_whitespace_name": defect = "HSK-001"
        elif name.startswith("test_select_level_and_return["): defect = "HSK-002"
        elif name == "test_stats_calendar_and_ranges": defect = "HSK-003"
        elif name == "test_notebook[NOTE-04]": defect = "HSK-004"
        else: raise ValueError(f"Unmapped failure: {name}")
        defects[(classname, name)] = defect
    require(Counter(defects.values()) == Counter({"HSK-001": 1, "HSK-002": 7, "HSK-003": 1, "HSK-004": 1}),
            "Defect count differs")
    for req, description, modules in groups:
        rows = [c for c in full if requirement_by_module[c[0]] == req]
        s = summary(rows)
        ids = sorted({defects[(c[0], c[1])] for c in rows if (c[0], c[1]) in defects})
        sources = ", ".join(link(module, '../../selenium-tests/test_' + module + '.py') for module in modules)
        lines.append(f"| {req} | {expected_by_req[req]} | {sources} | {s['total']} | {s['passed']} | {s['failed']} | {', '.join(ids) or '—'} |")
    lines += ["| **Tổng lượt chính** | | | **85** | **75** | **10** | **4 nhóm phát hiện** |", "",
              "Các tiêu chí trên được rút từ hành vi mong đợi của test có sẵn, không phải đặc tả đã được chủ sản phẩm duyệt lại. Ví dụ ngưỡng số cụ thể xem assertion và WB-GATE bên dưới. Các kiểm tra API trong Selenium cùng thuộc ca gốc, không cộng thành số ca API độc lập. Việc 8 nhóm có test không phải code coverage hoặc tỷ lệ bao phủ toàn bộ yêu cầu HSK.", "",
              "### Từng ca của lượt chính", "",
              "Nguồn trạng thái cho toàn bộ bảng: [report.xml](../experiments/2026-10-19/selenium-all-122951/report.xml), đối chiếu với [run.json](../experiments/2026-10-19/selenium-all-122951/run.json) và [DOM lịch sử](../experiments/2026-10-19/selenium-dom-verification.json). Tên ca giữ nguyên từ XML; các ID S-xxx chỉ để tra cứu trong báo cáo. Ảnh và cách tái hiện theo mã lỗi ở [bảng lỗi](DEFECT-REGISTER.md).", "",
              "| ID | Yêu cầu | Ca gốc | Trạng thái | Mã lỗi | Nguồn test |",
              "| --- | --- | --- | --- | --- | --- |"]
    for index, (classname, name, status) in enumerate(full, 1):
        source = classname.split(".")[-1] + ".py"
        defect = defects.get((classname, name), "—")
        lines.append(f"| S-{index:03} | {requirement_by_module[classname]} | `{cell(name)}` | "
                     f"{status.upper().replace('PASSED', 'PASS').replace('FAILED', 'FAIL')} | {defect} | "
                     f"{link(source, '../../selenium-tests/' + source)} |")
    lines += ["", "## 4. Logic HSK — 22 ca Vitest", "",
              "Nguồn: [XML UI](../experiments/2026-10-19/vitest-ui.xml), [XML CLI](../experiments/2026-10-19/vitest-cli.xml). Mỗi cách đều 22/22 PASS; 17 ca core và 5 ca gate là các tập con của 22 ca, không cộng lại. HSK-REVIEW gồm 10 ca SM-2; HSK-UNLOCK gồm 7 ca mở khóa và 5 ca ngưỡng/bảo toàn kết quả. Đây không phải kiểm định lại đặc tả SM-2.", "",
              "| ID gốc | Yêu cầu | Tên ca trong XML | Trạng thái | Nguồn test |",
              "| --- | --- | --- | --- | --- |"]
    for classname, name, status in vitest:
        match = re.search(r"WB-(SM2|UNLOCK|GATE)-\d+", name)
        require(match is not None, f"Unknown Vitest case: {name}")
        require((REPO / "hsk-app" / "frontend" / classname).is_file(), "Missing Vitest source")
        req = "HSK-REVIEW" if match[1] == "SM2" else "HSK-UNLOCK"
        lines.append(f"| {match[0]} | {req} | {cell(name)} | PASS | "
                     f"{link(Path(classname).name, '../../hsk-app/frontend/' + classname)} |")
    lines += ["", "## 5. Giới hạn sử dụng bảng", "",
              "Các yêu cầu ngoài bộ ca hiện có chưa được truy vết thành PASS. Những phần chưa kiểm thử và kết luận theo tiêu chí xem [mục 8 báo cáo](EXPERIMENT-REPORT.md#8-kết-luận-chất-lượng-theo-tiêu-chí-và-phạm-vi-chưa-kiểm-thử). Bảng không chứng minh code coverage, bảo mật toàn hệ thống, chất lượng nội dung học tập, hiệu năng hoặc hiệu quả thao tác người dùng.", ""]
    # Present website evaluation first; retain tool validation as supporting evidence.
    tool_start = lines.index("## 2. Yêu cầu công cụ và các ca kiểm tra")
    hsk_start = lines.index("## 3. Yêu cầu HSK và kết quả Selenium")
    vitest_start = lines.index("## 4. Logic HSK — 22 ca Vitest")
    limits_start = lines.index("## 5. Giới hạn sử dụng bảng")
    ordered = (lines[:tool_start]
               + ["## 2. Yêu cầu HSK và kết quả Selenium"] + lines[hsk_start + 1:vitest_start]
               + ["## 3. Logic HSK — 22 ca Vitest"] + lines[vitest_start + 1:limits_start]
               + ["## 4. Yêu cầu công cụ và các ca kiểm tra"] + lines[tool_start + 1:hsk_start]
               + lines[limits_start:])
    return "\n".join(ordered)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare without writing files")
    args = parser.parse_args()
    content = build()
    if args.check:
        require(TARGET.read_text(encoding="utf-8") == content, "Traceability document needs regeneration")
        print("OK: 21 tool tests, 22 Vitest cases, 85 Selenium cases (75 PASS/10 FAIL), 4 defect groups; evidence matches.")
    else:
        TARGET.write_text(content, encoding="utf-8")
        print(f"Generated {TARGET.relative_to(REPO)} from saved evidence; no website tests executed.")
