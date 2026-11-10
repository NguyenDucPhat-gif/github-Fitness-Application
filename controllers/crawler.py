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
from controllers.data_manager import DataManager


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


MET_BY_SPORT = {"Running": 9.8, "Swimming": 7.0, "Cycling": 7.5}#MET  theo chuẩn của Hiệp hội Y học Thể thao Hoa Kỳ 


def fetch_api_data(url=API_URL):

    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.Timeout:
        raise Exception("Hết thời gian chờ, API không phản hồi")
    except requests.exceptions.ConnectionError:
        raise Exception("Không kết nối được, hãy kiểm tra mạng Internet")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Lỗi khi gửi yêu cầu: {e}")

    if response.status_code != 200:
        raise Exception(f"API trả về mã lỗi {response.status_code}")

    try:
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Dữ liệu không phải là một danh sách")
        return data
    except ValueError as e:
        raise Exception(f"Dữ liệu trả về không hợp lệ: {e}")



def calo_rate_from_met(sport, weight_kg=WEIGHT_KG):
    met = MET_BY_SPORT.get(sport)
    if met is None or met <= 0:
        return None
    kcal_per_hour = met * weight_kg 
    return round(kcal_per_hour / 60.0, 1)


def matches_sport(item, sport):
  
    query = SPORT_QUERIES.get(sport)
    if not query:
        return False
    category = (item.get("category") or "").lower()
    name = (item.get("name") or "").lower()
    

    if category != query["category"]:
        return False

    for kw in query["keywords"]:
        if kw in name:
            return True
    return False


def next_exercise_id(existing):
    max_num = 0  
    for e in existing:
        if isinstance(e, dict):
            eid = e.get("exercise_id", "")
            if isinstance(eid, str) and eid[1:].isdigit():
                num = int(eid[1:])
                if num > max_num:
                    max_num = num
                    
    return max_num + 1 


def update_exercises(data_manager, max_per_sport=MAX_PER_SPORT):
    existing = data_manager.load_data()
    added = []
    
    old_names = []
    
    for e in existing:
        if isinstance(e, dict):
            old_names.append(e.get("name", "").lower())              
    next_number =next_exercise_id(existing)

    try:
        raw_items = fetch_api_data()
    except Exception as e:
        raise Exception(f"Không tải được dữ liệu từ API: {e}")

    for sport in SPORT_QUERIES:
        count = 0 
        for item in raw_items:
            if count >= max_per_sport:
                break 
                
            if matches_sport(item, sport):
                name = item.get("name", "").strip()
                if name and name.lower() not in old_names:
                    
                    rate = calo_rate_from_met(sport)
                    if rate is not None:
                    
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
                        count += 1
                        old_names.append(name.lower())

   
    if len(added) > 0:
        try:
            shutil.copy2(data_manager.file_path, data_manager.file_path + ".bak")
        except OSError as e:
                raise Exception(f"Không sao lưu được file: {e}")
                
        if not data_manager.save_data(existing + added):
            raise Exception("Không ghi được file exercises.json")
            
    return added
def main():
    try:
        added_list = update_exercises(DataManager(EXERCISE_FILE))
    except Exception as e:
        print("Lỗi:", e)
        sys.exit(1)
        
   
    print(f"Đã thêm {len(added_list)} bài tập mới")
    
  
    for ex in added_list:
        print(f"  {ex['exercise_id']} | {ex['sport']:<8} | {ex['calo_rate']:>6} | {ex['name']}")


if __name__ == "__main__":
    main()