# -*- coding: utf-8 -*-
"""
Crawler.py - Crawl TRỰC TIẾP từ PlainExercise.com
Lấy danh sách bài tập từ /exercises/ (có phân trang), parse từng <li>.
"""
import os
import shutil
import sys
import time
import requests
from bs4 import BeautifulSoup
from data_manager import DataManager

# ---------- (0) Cấu hình ----------
BASE_URL = "https://plainexercise.com"
LIST_URL = f"{BASE_URL}/exercises/"
TIMEOUT_SECONDS = 15
DELAY_BETWEEN_REQUESTS = 1.0
WEIGHT_KG = 70
EXERCISE_FILE = "exercises.json"
MAX_PER_SPORT = 5
SOURCE_LABEL = "PlainExercise.com / MET: Compendium of Physical Activities"
USER_AGENT = (
    "Mozilla/5.0 (compatible; SportsAppCrawler/1.0; "
    "+https://plainexercise.com) Python-requests"
)

# Từ khóa lọc theo TÊN bài tập (vì PlainExercise không có category cardio/strength)
SPORT_QUERIES = {
    "Running":  {"keywords": ("run", "jog", "sprint", "treadmill")},
    "Swimming": {"keywords": ("swim", "pool", "aquatic")},
    "Cycling":  {"keywords": ("cycl", "bike", "bicycle", "spin")},
}

MET_BY_SPORT = {"Running": 9.8, "Swimming": 7.0, "Cycling": 7.5}
KCAL_PER_MET_PER_HOUR = 1.0


class CrawlError(Exception):
    """Lỗi khi lấy hoặc lưu dữ liệu từ nguồn bên ngoài."""


# ---------- (1) Tải 1 trang danh sách, parse các <li> bài tập ----------
def fetch_list_page(url=LIST_URL):
    """Tải trang /exercises/ (hoặc ?page=N) và trả về list dict bài tập."""
    try:
        response = requests.get(
            url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT}
        )
    except requests.exceptions.Timeout:
        raise CrawlError("Hết thời gian chờ, PlainExercise không phản hồi")
    except requests.exceptions.ConnectionError:
        raise CrawlError("Không kết nối được, hãy kiểm tra mạng Internet")
    except requests.exceptions.RequestException as e:
        raise CrawlError(f"Lỗi khi gửi yêu cầu: {e}")

    if response.status_code != 200:
        raise CrawlError(f"PlainExercise trả về mã lỗi {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    exercises = []

    # Tìm tất cả link /exercise/<slug>/ nằm trong <li>
    # (dùng selector rộng rồi lọc theo href để bền với thay đổi class)
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("/exercise/") or href.rstrip("/") == "/exercise":
            continue
        name = a.get_text(" ", strip=True)
        if not name:
            continue

        # Lấy metadata từ div kế bên (các <span> ngăn cách bởi dấu ·)
        parent_li = a.find_parent("li")
        primary_muscle, equipment, level = None, None, None
        if parent_li:
            meta_div = parent_li.find(
                "div", class_=lambda c: c and "text-xs" in c
            )
            if meta_div:
                # Lấy các span KHÔNG phải dấu phân cách (aria-hidden="true")
                spans = [
                    s.get_text(" ", strip=True)
                    for s in meta_div.find_all("span")
                    if s.get("aria-hidden") != "true"
                ]
                # spans có thể là [muscle, equipment, level] hoặc [muscle, level]
                if len(spans) >= 2:
                    primary_muscle = spans[0]
                    level = spans[-1]
                    if len(spans) == 3:
                        equipment = spans[1]

        exercises.append({
            "name": name,
            "url": BASE_URL + href,
            "primary_muscles": [primary_muscle] if primary_muscle else [],
            "equipment": equipment,
            "level": level,
        })

    # Loại trùng theo URL
    seen= set()
    unique = []
    for ex in exercises:
        if ex["url"] in seen:
            continue
        seen.add(ex["url"])
        unique.append(ex)

    if not unique:
        raise CrawlError("Không tìm thấy bài tập — cấu trúc HTML có thể đã thay đổi")
    return unique


def has_next_page(html):
    """Kiểm tra còn trang sau không (dựa vào link rel=next)."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("a", rel="next") is not None


# ---------- (2) Lọc theo môn + tính calo ----------
def calo_rate_from_met(sport, weight_kg=WEIGHT_KG):
    met = MET_BY_SPORT.get(sport)
    if met is None or met <= 0:
        return None
    kcal_per_hour = met * weight_kg * KCAL_PER_MET_PER_HOUR
    if sport == "Running":
        return round(kcal_per_hour / 10.0, 1)   # giả định 10 km/h
    return round(kcal_per_hour / 60.0, 1)


def matches_sport(name, sport):
    query = SPORT_QUERIES.get(sport)
    if not query:
        return False
    low = name.lower()
    return any(kw in low for kw in query["keywords"])


# ---------- (3) Lưu file ----------
def next_exercise_number(existing):
    nums = []
    for e in existing:
        if isinstance(e, dict):
            eid = e.get("exercise_id", "")
            if isinstance(eid, str) and eid[1:].isdigit():
                nums.append(int(eid[1:]))
    return max(nums, default=0) + 1


def update_exercises(data_manager, max_per_sport=MAX_PER_SPORT, max_pages=3):
    """Crawl tối đa max_pages trang danh sách, lấy tối đa max_per_sport bài/môn."""
    existing = data_manager.load_data()
    names = {e.get("name", "").lower() for e in existing if isinstance(e, dict)}
    next_number = next_exercise_number(existing)
    added, errors = [], []
    counted = {sport: 0 for sport in SPORT_QUERIES}

    page = 1
    while page <= max_pages:
        url = LIST_URL if page == 1 else f"{LIST_URL}?page={page}"
        try:
            items = fetch_list_page(url)
        except CrawlError as e:
            errors.append(f"Trang {page}: {e}")
            break

        for item in items:
            if all(counted[s] >= max_per_sport for s in SPORT_QUERIES):
                break
            for sport in SPORT_QUERIES:
                if counted[sport] >= max_per_sport:
                    continue
                if not matches_sport(item["name"], sport):
                    continue
                if item["name"].lower() in names:
                    continue
                rate = calo_rate_from_met(sport)
                if rate is None:
                    continue
                names.add(item["name"].lower())
                added.append({
                    "exercise_id": f"E{next_number:02d}",
                    "name": item["name"],
                    "sport": sport,
                    "calo_rate": rate,
                    "primary_muscles": item["primary_muscles"],
                    "equipment": item["equipment"],
                    "source": SOURCE_LABEL,
                })
                next_number += 1
                counted[sport] += 1
                break  # 1 bài chỉ gán cho 1 môn

        # kiểm tra còn trang sau không
        try:
            r = requests.get(url, timeout=TIMEOUT_SECONDS,
                             headers={"User-Agent": USER_AGENT})
            if not has_next_page(r.text):
                break
        except requests.exceptions.RequestException:
            break
        page += 1
        time.sleep(DELAY_BETWEEN_REQUESTS)

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
    for msg in result["errors"]:
        print("  Cảnh báo:", msg)


if __name__ == "__main__":
    main()
