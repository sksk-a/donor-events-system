"""Подготовить отдельную учебную копию JSON, не изменяя исходный файл."""
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    source = root / "data" / "sample_data.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    # Явно учебные записи для показа обеих ветвей шаблона статуса.
    data["registrations"] = [
        {"id": 1, "participant_id": 1, "event_id": 1,
         "registration_date": "2026-10-01", "status": "CONFIRMED",
         "notes": "Учебная запись для защиты; не реальная регистрация."},
        {"id": 2, "participant_id": 2, "event_id": 1,
         "registration_date": "2026-10-02", "status": "CANCELLED",
         "notes": "Учебная отменённая запись; не реальная регистрация."},
    ]
    target = root / "test-results" / "defense_data.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
