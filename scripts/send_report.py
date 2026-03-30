"""
send_report.py
Парсить JUnit XML-звіт після pytest та відправляє JSON-payload
на n8n webhook, звідки n8n надсилає повідомлення в Telegram.

Змінні середовища (GitHub Actions → Secrets / env):
  N8N_WEBHOOK_URL  — URL вашого n8n Webhook-ноди
  GITHUB_RUN_URL   — посилання на конкретний запуск (підставляє workflow)
  TRIGGER_TYPE     — schedule | workflow_dispatch
  MARKER_USED      — маркер pytest, якщо запущено вручну
"""

import json
import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Парсинг JUnit XML
# ---------------------------------------------------------------------------

def parse_junit(path: str) -> dict:
    """Повертає словник зі статистикою тестів."""
    if not os.path.exists(path):
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "duration": 0.0,
            "failed_tests": [],
        }

    tree = ET.parse(path)
    root = tree.getroot()

    # <testsuite> може бути коренем або всередині <testsuites>
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        suite = root

    total    = int(suite.get("tests", 0))
    failed   = int(suite.get("failures", 0))
    errors   = int(suite.get("errors", 0))
    skipped  = int(suite.get("skipped", 0))
    duration = round(float(suite.get("time", 0)), 1)
    passed   = total - failed - errors - skipped

    # Збираємо назви тестів, що впали
    failed_tests = []
    for tc in root.iter("testcase"):
        if tc.find("failure") is not None or tc.find("error") is not None:
            name = f"{tc.get('classname', '')}.{tc.get('name', '')}".strip(".")
            failed_tests.append(name)

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "duration": duration,
        "failed_tests": failed_tests[:10],  # не більше 10 у повідомленні
    }


# ---------------------------------------------------------------------------
# Формування Telegram-повідомлення (Markdown)
# ---------------------------------------------------------------------------

def build_message(stats: dict, run_url: str, trigger: str, marker: str) -> str:
    total   = stats["total"]
    passed  = stats["passed"]
    failed  = stats["failed"]
    errors  = stats["errors"]
    skipped = stats["skipped"]
    duration = stats["duration"]

    overall_ok = (failed == 0 and errors == 0 and total > 0)
    status_icon = "✅" if overall_ok else "❌"
    status_text = "PASSED" if overall_ok else "FAILED"

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    trigger_label = "⏰ За розкладом" if trigger == "schedule" else "🖐 Ручний запуск"
    marker_label  = f" `{marker}`" if marker else " (всі тести)"

    lines = [
        f"{status_icon} *Mercury API Tests — {status_text}*",
        "",
        f"📅 {now_utc}",
        f"🚀 {trigger_label}{marker_label}",
        "",
        f"📊 *Результати:*",
        f"  • Всього: *{total}*",
        f"  • ✅ Пройшли: *{passed}*",
        f"  • ❌ Впали: *{failed}*",
        f"  • 💥 Помилки: *{errors}*",
        f"  • ⏭ Пропущені: *{skipped}*",
        f"  • ⏱ Час: *{duration}s*",
    ]

    if stats["failed_tests"]:
        lines.append("")
        lines.append("🔴 *Тести що впали:*")
        for t in stats["failed_tests"]:
            lines.append(f"  • `{t}`")

    lines.append("")
    lines.append(f"[🔗 Відкрити звіт в GitHub Actions]({run_url})")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Відправка на n8n webhook
# ---------------------------------------------------------------------------

def send_to_n8n(webhook_url: str, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[send_report] n8n відповів: {resp.status} {resp.reason}")
    except urllib.error.HTTPError as e:
        print(f"[send_report] HTTP помилка: {e.code} — {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[send_report] Не вдалось з'єднатись з n8n: {e.reason}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    webhook_url = os.environ.get("N8N_WEBHOOK_URL", "").strip()
    if not webhook_url:
        print("[send_report] N8N_WEBHOOK_URL не задано — пропускаємо відправку.")
        sys.exit(0)

    run_url  = os.environ.get("GITHUB_RUN_URL", "https://github.com")
    trigger  = os.environ.get("TRIGGER_TYPE", "workflow_dispatch")
    marker   = os.environ.get("MARKER_USED", "").strip()

    stats   = parse_junit("report.xml")
    message = build_message(stats, run_url, trigger, marker)

    payload = {
        # Головне поле — готовий текст для Telegram (Markdown)
        "message": message,

        # Сирі дані — якщо в n8n потрібна додаткова логіка
        "total":    stats["total"],
        "passed":   stats["passed"],
        "failed":   stats["failed"],
        "errors":   stats["errors"],
        "skipped":  stats["skipped"],
        "duration": stats["duration"],
        "status":   "passed" if (stats["failed"] == 0 and stats["errors"] == 0 and stats["total"] > 0) else "failed",
        "run_url":  run_url,
        "trigger":  trigger,
        "marker":   marker,
    }

    print("[send_report] Відправляємо звіт на n8n...")
    send_to_n8n(webhook_url, payload)
    print("[send_report] Готово.")


if __name__ == "__main__":
    main()
