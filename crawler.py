# -*- coding: utf-8 -*-
"""
Crawler.py - Sử dụng API JSON từ Free Exercise DB (CC0)
Nguồn: https://github.com/yuhonas/free-exercise-db
"""
import os
import shutil
import sys
import time
import requests
from data_manager import DataManager

# ---------- (0) Cấu hình ----------
API_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
TIMEOUT_SECONDS = 15
WEIGHT_KG = 70
EXERCISE_FILE = "exercises.json"
MAX_PER_SPORT = 3  
SOURCE_LABEL = "Free Exercise DB (CC0) / MET: Compendium"

SPORT_QUERIES = {
    "Running":  {"category": "cardio", "keywords": ("run", "jog", "sprint", "treadmill")},
    "Swimming": {"category": "cardio", "keywords": ("swim", "pool", "aquatic")},
    "Cycling":  {"category": "cardio", "keywords": ("cycl", "bike", "bicycle", "spin")},
}


MET_BY_SPORT = {"Running": 9.8, "Swimming": 7.0, "Cycling": 7.5}
KCAL_PER_MET_PER_HOUR = 1.0


class CrawlError(Exception):
    """Lỗi khi lấy hoặc lưu dữ liệu từ nguồn bên ngoài."""


# ---------- (1) Tải dữ liệu từ API ----------
def fetch_api_data(url=API_URL):
    """Tải file JSON từ API, xử lý các lỗi mạng."""
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.Timeout:
        raise CrawlError("Hết thời gian chờ, API không phản hồi")
    except requests.exceptions.ConnectionError:
        raise CrawlError("Không kết nối được, hãy kiểm tra mạng Internet")
    except requests.exceptions.RequestException as e:
        raise CrawlError(f"Lỗi khi gửi yêu cầu: {e}")

    if response.status_code != 200:
        raise CrawlError(f"API trả về mã lỗi {response.status_code}")

    try:
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Dữ liệu không phải là một danh sách")
        return data
    except ValueError as e:
        raise CrawlError(f"Dữ liệu trả về không hợp lệ: {e}")


# ---------- (2) Lọc và xử lý dữ liệu ----------
def calo_rate_from_met(sport, weight_kg=WEIGHT_KG):
    met = MET_BY_SPORT.get(sport)
    if met is None or met <= 0:
        return None
    kcal_per_hour = met * weight_kg * KCAL_PER_MET_PER_HOUR
    if sport == "Running":
        return round(kcal_per_hour / 10.0, 1)   # giả định 10 km/h
    return round(kcal_per_hour / 60.0, 1)


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


def next_exercise_number(existing):
    nums = []
    for e in existing:
        if isinstance(e, dict):
            eid = e.get("exercise_id", "")
            if isinstance(eid, str) and eid[1:].isdigit():
                nums.append(int(eid[1:]))
    return max(nums, default=0) + 1


# ---------- (3) Chạy Crawl và Lưu file ----------
def update_exercises(data_manager, max_per_sport=MAX_PER_SPORT):
    existing = data_manager.load_data()
    names = {e.get("name", "").lower() for e in existing if isinstance(e, dict)}
    next_number = next_exercise_number(existing)
    added, errors = [], []
    counted = {sport: 0 for sport in SPORT_QUERIES}

  
    try:
        raw_items = fetch_api_data()
    except CrawlError as e:
        raise CrawlError(f"Không tải được dữ liệu từ Free Exercise DB: {e}")

    for item in raw_items:
        if all(counted[s] >= max_per_sport for s in SPORT_QUERIES):
            break
            
        for sport in SPORT_QUERIES:
            if counted[sport] >= max_per_sport:
                continue
            if not matches_sport(item, sport):
                continue
                
            name = item.get("name", "").strip()
            if not name or name.lower() in names:
                continue
                
            rate = calo_rate_from_met(sport)
            if rate is None:
                continue
                
            names.add(name.lower())
         
            added.append({
                "exercise_id": f"E{next_number:02d}",
                "name": name,
                "sport": sport,
                "calo_rate": rate,
                "primary_muscles": item.get("primaryMuscles", []),
                "equipment": item.get("equipment", "body only"),
                "source": SOURCE_LABEL,
            })
            next_number += 1
            counted[sport] += 1
            break  # 1 bài chỉ gán cho 1 môn


    if added:
        if os.path.exists(data_manager.file_path):
            try:
                shutil.copy2(data_manager.file_path, data_manager.file_path + ".bak")
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
        print(f"  {ex['exercise_id']} | {ex['sport']:<8} | {ex['calo_rate']:>6} | {ex['name']}")


if __name__ == "__main__":
    main()