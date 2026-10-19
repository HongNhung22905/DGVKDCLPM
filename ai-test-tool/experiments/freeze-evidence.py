"""Index saved evidence and hashes for reporting; no tests, API calls or DB access."""
import argparse
import csv
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import subprocess

TOOL = Path(__file__).resolve().parents[1]
REPO = TOOL.parent
OLD = TOOL / "experiments" / "2026-10-19"
MANIFEST = TOOL / "experiments" / "2026-10-20" / "evidence-baseline.json"
DOCUMENT = TOOL / "docs" / "EVIDENCE-BASELINE.md"
ARCHIVE = "ce3290af09456590f2b98a9dcfcb51a7320f25b6"
LOCAL = timezone(timedelta(hours=7))


def load(name):
    return json.loads((OLD / name).read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(LOCAL).strftime("%d/%m/%Y %H:%M:%S UTC+7")


def build():
    environment = load("environment.json")
    full = load("selenium-all-122951/run.json")
    small = load("selenium-notebook-122623/run.json")
    stopped = load("selenium-notebook-122432/run.json")
    comparison = load("selenium-cli-ui-comparison.json")
    vitest = load("cli-ui-comparison.json")
    gemini = load("gemini-connection.json")
    faults = load("fault-scenarios.json")
    actual_ai = load("selenium-gemini-analysis.json")
    rows = [
        ("E-S02", "Kết quả chính — Selenium toàn bộ", local_time(full["startedAt"]) + " (bắt đầu)",
         "HSK snapshot local; Chrome 154; endpoint Neon kiểm thử riêng", "85: 75 PASS / 10 FAIL / 0 ERROR / 0 SKIP; runner 1727,746 s",
         "selenium-all-122951/report.xml", full["id"]),
        ("E-V01", "Kết quả chính — logic HSK (Vitest)", local_time(vitest["checkedAt"]) + " (đối chiếu)",
         "Windows, Node 24.19.0, Vitest 2.1.9; không cần DB", "22/22 PASS mỗi cách; không cộng CLI và UI thành 44 ca",
         "cli-ui-comparison.json", vitest["ui"]["runId"]),
        ("E-S01", "Đối chiếu luồng — Selenium nhóm nhỏ UI", local_time(small["startedAt"]) + " (bắt đầu)",
         "Cùng môi trường snapshot/endpoint kiểm thử của E-S02", "10/10 PASS, runner 180,279 s; không thay kết quả E-S02",
         "selenium-notebook-122623/report.xml", small["id"]),
        ("E-S03", "Đối chiếu — Selenium nhóm nhỏ CLI", local_time(comparison["checkedAt"]) + " (đối chiếu)",
         "Cùng snapshot/endpoint; CLI chạy sau E-S02; không reset DB", "10/10 PASS; tiến trình 155,019 s; tên/trạng thái khớp E-S01",
         "selenium-cli-ui-comparison.json", None),
        ("E-T01", "Sản phẩm hỗ trợ — test HSK Test Lab", "19/10/2026 (thư mục đợt; log không ghi giờ)",
         "Node test runner; fixture/mock và tiến trình Node; không phải E2E HSK", "21/21 test công cụ đạt; không cộng vào 22 Vitest hoặc 85 Selenium",
         "tool-tests-after-selenium.log", None),
        ("E-X01", "Khả năng nhập — XML lịch sử", "19/10/2026 (thư mục đợt; JSON không ghi giờ)",
         "Parser công cụ đối chiếu Python ElementTree trên cùng tệp", "70/70 XML khớp, 115 bản ghi có trùng; không phải 70 lượt chạy mới",
         "xml-compatibility.json", None),
        ("E-F01", "Tình huống lỗi công cụ", local_time(faults["checkedAt"]) + " (ghi nhận)",
         "XML và tiến trình/HTTP fixture local có kiểm soát", "Hủy/timeout/XML sai/kết nối bị từ chối; không phải lỗi website mới",
         "fault-scenarios.json", None),
        ("E-A01", "Tích hợp — Gemini với lỗi HSK lịch sử", local_time(gemini["checkedAt"]) + " (ghi nhận)",
         "Gemini API thật; alias gemini-flash-latest", "HTTP 200; FC-05 lịch sử; không phải ca Selenium mới",
         "gemini-connection.json", gemini["runId"]),
        ("E-A02", "AI — bộ 10 mẫu, đánh giá sơ bộ", local_time(load("ai-responses.json")["checkedAt"]) + " (metadata; retry có timestamp riêng)",
         "1 lỗi HSK lịch sử + 9 lỗi kiểm soát; nguyên nhân lưu trước lời gọi", "7 đúng / 3 đúng một phần / 0 sai; chưa chấm độc lập; 503 lưu riêng",
         "ai-judgements.json", None),
        ("E-A03", "Tích hợp — Gemini với lỗi lượt đầy đủ", local_time(actual_ai["checkedAt"]) + " (ghi nhận)",
         "Gemini nhận XML/log rút gọn của E-S02", "HTTP 200; không phải phần chấm 10 mẫu E-A02",
         "selenium-gemini-analysis.json", full["id"]),
        ("E-S00", "Loại khỏi kết quả chính — lượt bị dừng trước sửa launcher", local_time(stopped["startedAt"]) + " (bắt đầu)",
         "Snapshot trước sửa cwd; không đồng nhất phiên bản launcher E-S02", "cancelled; 56,076 s; chưa có XML đầy đủ; không cộng ca",
         "selenium-notebook-122432/summary.json", stopped["id"]),
    ]
    # Only enumerate archived experiment files; never index .env or local data snapshots.
    artifacts = {p for p in OLD.rglob("*") if p.is_file()}
    historical_xml = load("xml-compatibility.json")
    for item in historical_xml["results"]:
        path = REPO / item["file"]
        if digest(path) != item["sha256"]:
            raise ValueError(f"Historical XML changed: {item['file']}")
        artifacts.add(path)
    historical = []
    for index, path in enumerate(sorted(REPO.glob("PERF*.jtl")), 1):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            samples = list(csv.DictReader(stream))
        timestamps = [int(item["timeStamp"]) for item in samples]
        start = datetime.fromtimestamp(min(timestamps) / 1000, timezone.utc)
        end = datetime.fromtimestamp(max(timestamps) / 1000, timezone.utc)
        report = REPO / (path.stem + "-report")
        related = [path, path.with_suffix(".log"), report / "index.html", report / "statistics.json"]
        artifacts.update(p for p in related if p.is_file())
        historical.append({"id": f"H-J{index:02}", "jtl": path.name, "sampleRecords": len(samples),
                           "firstSampleUtc": start.isoformat(), "lastSampleUtc": end.isoformat(),
                           "reportIndex": str((report / "index.html").relative_to(REPO)).replace("\\", "/")
                           if (report / "index.html").is_file() else None,
                           "testedCommit": None, "includedInCurrentPassFail": False})
    artifacts.update(REPO / name for name in ["HSK-performance.jmx", "HSK-progress-performance.jmx"])
    source_checks = []
    for filename in ["environment.json", "selenium-environment.json", "selenium-full-results.json"]:
        metadata = load(filename)
        comparisons = {}
        for name, recorded in metadata["sourceSha256"].items():
            path = REPO / name
            current = digest(path)
            archived = subprocess.check_output(["git", "show", f"{ARCHIVE}:{name}"], cwd=REPO)
            comparisons[name] = {"recordedSha256": recorded, "currentSha256": current,
                                 "currentMatchesRecorded": current == recorded,
                                 "archiveContentMatchesCurrentIgnoringCrLf":
                                 archived.replace(b"\r\n", b"\n") == path.read_bytes().replace(b"\r\n", b"\n")}
        source_checks.append({"metadata": filename, "files": comparisons})
    manifest = {
        "topic": "Kiểm thử tự động website hỗ trợ học tiếng Trung và xây dựng công cụ tích hợp AI hỗ trợ phân tích kết quả.",
        "documentationDate": "2026-10-20", "experimentDate": "2026-10-19", "displayTimezone": "UTC+7",
        "recordedGitHeadAtEnvironmentCapture": environment["gitHead"],
        "testedCleanCommit": None, "archiveCommitAfterExperiments": ARCHIVE,
        "versionLimit": "Working tree was uncommitted; launcher changed between stages. Recorded source hashes identify selected files, not a complete deployed website snapshot.",
        "sourceComparisons": source_checks,
        "evidenceRows": [{"id": i, "role": role, "time": time, "environment": env,
                          "result": result, "evidence": filename, "runId": run}
                         for i, role, time, env, result, filename, run in rows],
        "historicalJmeter": historical,
        "artifactSha256": {str(p.relative_to(REPO)).replace("\\", "/"): digest(p)
                           for p in sorted(artifacts)},
    }
    lines = ["# Chốt kết quả và danh mục minh chứng", "",
             "Đề tài: **Kiểm thử tự động website hỗ trợ học tiếng Trung và xây dựng công cụ tích hợp AI hỗ trợ phân tích kết quả.** Đánh giá website HSK là trọng tâm môn học; HSK Test Lab là sản phẩm hỗ trợ được phát triển trong dự án.", "",
             "Chốt hồ sơ ngày **20/10/2026** từ các tệp đã có; không chạy thêm test hoặc truy cập DB. Số liệu đợt chính thuộc **19/10/2026**. Các giờ dưới đây đã đổi sang UTC+7; JSON/XML giữ timestamp gốc. “Đối chiếu/ghi nhận” không có nghĩa là thời điểm bắt đầu chạy.", "",
             "## 1. Phiên bản và môi trường", "",
             f"- HEAD được ghi trong `environment.json`: `{environment['gitHead']}`. Khi ghi metadata, công cụ và báo cáo còn ở working tree, chưa commit; không có một clean commit được xác nhận đại diện toàn bộ lần chạy.",
             f"- Commit lưu trữ mã/minh chứng sau thực nghiệm: `{ARCHIVE}`. Không gọi commit này là commit đã được chạy test vào thời điểm trước đó. Hash các tệp nguồn được ghi theo từng giai đoạn trong manifest bên dưới.",
             "- Metadata trước Selenium và metadata sau sửa launcher khác hash `hsk-test-server.ts` đúng với thay đổi cwd đã ghi nhận. Hash của 33 tệp Selenium khớp hồ sơ lượt đầy đủ; các hash này không bao phủ toàn bộ mã website hoặc toàn bộ snapshot.",
             "- Selenium: Windows, Python 3.14, pytest/Selenium theo bộ dependency đã khóa, Chrome 154.0.8037.100; HSK snapshot local, endpoint Neon khác website hiện tại. Nhãn cấu hình `hsk-test-2026-10-19` chưa được xác minh qua Neon management API. Không đưa URL DB/khóa API vào bảng.",
             "- Vitest: Node 24.19.0, Vitest 2.1.9, không cần DB cho 22 ca hộp trắng. Test công cụ dùng fixture/mock và tiến trình riêng. UI/CLI Selenium cùng snapshot nhưng không reset DB giữa lượt, nên không coi dữ liệu hoàn toàn đồng nhất.", "",
             "Nguồn: [metadata ban đầu](../experiments/2026-10-19/environment.json), [metadata Selenium](../experiments/2026-10-19/selenium-environment.json), [hash test của lượt đầy đủ](../experiments/2026-10-19/selenium-full-results.json), [dependency Python](../requirements-lock.txt), [manifest SHA-256](../experiments/2026-10-20/evidence-baseline.json).", "",
             "## 2. Bảng tổng hợp được dùng trong báo cáo", "",
             "| ID | Vai trò | Thời gian và loại mốc | Môi trường | Kết quả được dùng | Minh chứng / run ID |",
             "| --- | --- | --- | --- | --- | --- |"]
    for i, role, time, env, result, filename, run in rows:
        evidence = f"[Tệp nguồn](../experiments/2026-10-19/{filename})"
        if run: evidence += f"; `{run}`"
        lines.append(f"| {i} | {role} | {time} | {env} | {result} | {evidence} |")
    lines += ["", "E-S02 là mẫu số chính của kết luận E2E: **85 ca, 75 PASS, 10 FAIL**. E-V01 là bộ logic 22 ca riêng. E-S01/E-S03 là chạy lại một tập con để đối chiếu luồng, không thêm ca độc lập vào tổng. E-T01 đánh giá công cụ, không thay kết quả website. E-X01 xác minh khả năng nhập báo cáo lịch sử, không xác nhận website hiện tại đạt các báo cáo đó.", "",
              "## 3. Minh chứng JMeter lịch sử, chưa đưa vào kết luận đạt hiệu năng", "",
              "Các JTL đã tồn tại trước đợt điều phối bằng HSK Test Lab, dù timestamp đều cùng ngày 19/10/2026. Phân loại lịch sử theo lượt/nguồn, không chỉ theo ngày. Chỉ kiểm kê số dòng sample và khoảng timestamp từ tệp; chưa chốt commit website, DB/môi trường, cấu hình tải, assertion, ngưỡng chấp nhận hoặc tính tương đương giữa các lượt. Tên `PROD`, `05`, `10`, `20` không đủ xác minh môi trường hay số người dùng thực tế.", "",
              "| ID | JTL gốc | Khoảng sample UTC+7 | Số bản ghi sample (không phải testcase) | Báo cáo có sẵn |",
              "| --- | --- | --- | ---: | --- |"]
    for item in historical:
        start, end = local_time(item["firstSampleUtc"]), local_time(item["lastSampleUtc"])
        report = f"[HTML](../../{item['reportIndex']})" if item["reportIndex"] else "Chưa có"
        lines.append(f"| {item['id']} | [{item['jtl']}](../../{item['jtl']}) | {start} → {end} | {item['sampleRecords']} | {report} |")
    lines += ["", "Kế hoạch hiện có: [HSK-performance.jmx](../../HSK-performance.jmx), [HSK-progress-performance.jmx](../../HSK-progress-performance.jmx). Chưa khẳng định từng lượt lịch sử chạy đúng phiên bản hiện tại của các JMX này. Không cộng sample JMeter với ca Selenium/Vitest, không suy mẫu thành PASS nghiệp vụ hoặc kết luận website đạt tải. Chương 5 có thể trình bày kiểm kê lịch sử với giới hạn trên; kết luận định lượng hiệu năng cần hồ sơ môi trường và ngưỡng được xác định trước lượt bổ sung.", "",
              "## 4. Quy tắc viết và sử dụng minh chứng", "",
              "1. Dùng ID E-* cho kết quả đợt chính/đối chiếu và H-J* cho JMeter lịch sử. Mỗi bảng số liệu của chương 3–6 phải chỉ rõ bộ nào; không gộp lại thành tổng ca mới.",
              "2. Kiểm tra API trong Selenium (status/body/CRUD/persistence) thuộc chính ca Selenium đó. Chưa có bộ kiểm thử API độc lập được chốt trong hồ sơ này; HTTP 200 của Gemini là kết nối tích hợp, không phải PASS toàn bộ API HSK.",
              "3. Giữ E-S00 cancelled và các FAIL gốc. Bốn nhóm HSK-001…004 quy về 10 FAIL; nhóm nhỏ PASS không đóng NOTE-04. Không cần sửa website để làm đẹp số liệu.",
              "4. Đánh giá AI E-A02 là sơ bộ, chưa có người chấm độc lập; không công bố độ chính xác chung 70%. HTTP 503 lưu riêng với câu trả lời retry.",
              "5. Hash manifest khóa nội dung tệp được dùng trong báo cáo, không thay thế việc biết commit/môi trường tại thời điểm chạy. Không bổ sung metadata hồi tố như thể đã thu thập trong quá trình thực thi.", "",
              "Ma trận: [yêu cầu–tiêu chí–test–kết quả](TEST-TRACEABILITY.md). Lỗi: [mức ảnh hưởng, cách tái hiện và độ chắc chắn](DEFECT-REGISTER.md). Bố cục báo cáo: [sáu chương](REPORT-OUTLINE.md).", "",
              "Kiểm tra hồ sơ bằng `python ai-test-tool/experiments/freeze-evidence.py --check`; bỏ `--check` chỉ khi chủ động chốt lại tệp đã thay đổi. Script không tạo lượt test mới, không dùng khóa API và không gọi database.", ""]
    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest, document = build()
    if args.check:
        if MANIFEST.read_text(encoding="utf-8") != manifest or DOCUMENT.read_text(encoding="utf-8") != document:
            raise SystemExit("Evidence baseline changed; review before freezing again.")
        print("OK: evidence baseline, historical JMeter inventory and SHA-256 hashes match.")
    else:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(manifest, encoding="utf-8")
        DOCUMENT.write_text(document, encoding="utf-8")
        print("Frozen evidence index and hashes; no tests or external services executed.")
