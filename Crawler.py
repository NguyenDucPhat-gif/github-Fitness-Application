# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 12:08:30 2026

@author: this pc
"""
# -*- coding: utf-8 -*-
"""
Crawler.py - Lấy dữ liệu bài tập từ Free Exercise DB (CC0) qua PlainExercise
rồi nối vào exercises.json.

Nguồn dữ liệu:
  - Bài tập: Free Exercise DB (CC0) - https://github.com/yuhonas/free-exercise-db
    (PlainExercise dùng chính nguồn này; dữ liệu mở, được phép crawl/redistribute)
  - Calo: Compendium of Physical Activities (Ainsworth et al., 2011) - giá trị MET
    (PlainExercise dùng MET để ước tính calo)

Không cần API key.
"""
import json
import os
import shutil
import sys

import requests

from DataManager import DataManager

# Free Exercise DB: file JSON công khai trên GitHub (raw)
EXERCISE_DB_URL = (
    "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
)
TIMEOUT_SECONDS = 15
WEIGHT_KG = 70                      # cân nặng dùng để ước tính calo (kg)
EXERCISE_FILE = "exercises.json"
MAX_PER_SPORT = 5                   # mỗi môn lấy tối đa 5 bài tập mới
SOURCE_LABEL = "Free Exercise DB (CC0) / MET: Compendium of Physical Activities"

# Môn trong ứng dụng -> cách lọc từ Free Exercise DB (theo category + từ khóa tên)
SPORT_QUERIES = {
    "Running":  {"category": "cardio", "keywords": ("run", "jog", "sprint", "treadmill")},
    "Swimming": {"category": "cardio", "keywords": ("swim", "pool", "aquatic")},
    "Cycling":  {"category": "cardio", "keywords": ("cycl", "bike", "bicycle", "spin")},
}

# MET ước tính theo môn (Compendium of Physical Activities, 2011) - dùng khi
# Free Exercise DB không có trường calo. Đây là giá trị đại diện, có thể tinh chỉnh.
MET_BY_SPORT = {
    "Running": 9.8,      # chạy bộ ~ 9.8 MET
    "Swimming": 7.0,     # bơi lội ~ 7.0 MET
    "Cycling": 7.5,      # đạp xe ~ 7.5 MET
}
# 1 MET = 1 kcal / kg / giờ
KCAL_PER_MET_PER_HOUR = 1.0


class CrawlError(Exception):
    """Lỗi khi lấy hoặc lưu dữ liệu từ nguồn bên ngoài (thông báo tiếng Việt)."""


# ---------- (1) Tải dữ liệu bài tập từ Free Exercise DB ----------
def fetch_exercise_db(url=EXERCISE_DB_URL):
    """Tải toàn bộ Free Exercise DB (list các dict thô). Báo CrawlError nếu lỗi."""
    try:
        response = requests.get(url, TIMEOUT_SECONDS)
    except requests.exceptions.Timeout:
        raise CrawlError("Hết thời gian chờ, nguồn dữ liệu không phản hồi")
    except requests.exceptions.ConnectionError:
        raise CrawlError("Không kết nối được, hãy kiểm tra mạng Internet")
    except requests.exceptions.RequestException as e:
        raise CrawlError(f"Lỗi khi gửi yêu cầu: {e}")

    if response.status_code != 200:
        raise CrawlError(f"Nguồn dữ liệu trả về mã lỗi {response.status_code}")
    try:
        data = response.json()
    except ValueError:
        raise CrawlError("Dữ liệu trả về không phải JSON hợp lệ")
    if not isinstance(data, list):
        raise CrawlError("Dữ liệu trả về sai cấu trúc (không phải danh sách)")
    return data


# ---------- (2) Chuyển đổi sang dạng Exercise ----------
def calo_rate_from_met(sport, weight_kg=WEIGHT_KG):
    """Tính calo/phút từ MET. Running: calo/km (ước tính qua tốc độ mặc định)."""
    met = MET_BY_SPORT.get(sport)
    if met is None or met <= 0:
        return None
    # kcal/giờ = MET * kg * 1.0
    kcal_per_hour = met * weight_kg * KCAL_PER_MET_PER_HOUR
    if sport == "Running":
        # Giả định tốc độ chạy trung bình 10 km/h để đổi calo/giờ -> calo/km
        assumed_speed_kmh = 10.0
        return round(kcal_per_hour / assumed_speed_kmh, 1)
    return round(kcal_per_hour / 60.0, 1)   # calo/phút


def matches_sport(item, sport):
    """Kiểm tra bài tập có thuộc môn thể thao mong muốn không."""
    query = SPORT_QUERIES.get(sport)
    if not query:
        return False
    category = (item.get("category") or "").lower()
    name = (item.get("name") or "").lower()
    if category != query["category"]:
        return False
    return any(kw in name for kw in query["keywords"])


def convert_to_exercises(raw_items, sport, existing_names, next_number,
                         limit=MAX_PER_SPORT):
    """Lọc bản ghi thiếu/sai, bỏ trùng tên, đổi sang dict giống exercises.json."""
    result = []
    for item in raw_items:
        if len(result) >= limit:
            break
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        if not matches_sport(item, sport):
            continue
        name = name.strip()
        if name.lower() in existing_names:
            continue
        rate = calo_rate_from_met(sport)
        if rate is None or rate <= 0:
            continue
        existing_names.add(name.lower())
        result.append({
            "exercise_id": f"E{next_number + len(result):02d}",
            "name": name,
            "sport": sport,
            "calo_rate": rate,
            # giữ thêm metadata hữu ích từ nguồn mở (có thể bỏ nếu không cần)
            "primary_muscles": item.get("primaryMuscles", []),
            "equipment": item.get("equipment"),
            "source": SOURCE_LABEL,
        })
    return result


# ---------- (3) Lưu vào exercises.json (có sao lưu) ----------
def next_exercise_number(existing):
    numbers = []
    for e in existing:
        if isinstance(e, dict):
            eid = e.get("exercise_id", "")
            if isinstance(eid, str) and eid[1:].isdigit():
                numbers.append(int(eid[1:]))
    return max(numbers, default=0) + 1


def update_exercises(data_manager, max_per_sport=MAX_PER_SPORT):
    """Lấy bài tập mới cho từng môn và nối vào file.
    Trả về {'added': [...], 'errors': [...]}."""
    existing = data_manager.load_data()
    names = {e.get("name", "").lower() for e in existing if isinstance(e, dict)}
    next_number = next_exercise_number(existing)
    added = []
    errors = []

    # Tải dữ liệu nguồn 1 lần, dùng cho tất cả môn
    try:
        raw_all = fetch_exercise_db()
    except CrawlError as e:
        raise CrawlError(f"Không tải được Free Exercise DB: {e}")

    for sport in SPORT_QUERIES:
        try:
            items = convert_to_exercises(
                raw_all, sport, names, next_number, max_per_sport
            )
        except CrawlError as e:
            errors.append(f"{sport}: {e}")
            continue
        added.extend(items)
        next_number += len(items)

    if added:
        if os.path.exists(data_manager.file_path):
            try:
                shutil.copy2(data_manager.file_path,
                             data_manager.file_path + ".bak")
            except OSError as e:
                raise CrawlError(f"Không sao lưu được file: {e}")
        if not data_manager.save_data(existing + added):
            raise CrawlError("Không ghi được file exercises.json")
    return {"added": added, "errors": errors}


def main():
    try:
        result = update_exercises(DataManager(EXERCISE_FILE))
    except CrawlError as e:
        print("Lỗi:", e)
        sys.exit(1)
    print(f"Đã thêm {len(result['added'])} bài tập mới")
    for ex in result["added"]:
        print(f"  {ex['exercise_id']} | {ex['sport']:<8} | "
              f"{ex['calo_rate']:>6} | {ex['name']}")
    for message in result["errors"]:
        print("  Cảnh báo:", message)


if __name__ == "__main__":
    main()

