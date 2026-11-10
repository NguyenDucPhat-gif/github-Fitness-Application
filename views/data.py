"""Du lieu dung chung. Hien luu trong bo nho; khi co phan luu tru (file/SQLite) thi chi can sua cac ham trong file nay."""
import hashlib
import json
import os
import random
import re
import secrets
import shutil
from datetime import datetime, timedelta

import config

DATE_FORMAT = "%d/%m/%Y"

EXERCISES = {
    "Chạy bộ": ["Chạy chậm", "Chạy nước rút", "Chạy địa hình"],
    "Gym": ["Đẩy ngực", "Squat", "Deadlift", "Kéo xà"],
    "Bơi lội": ["Bơi ếch", "Bơi sải", "Bơi bướm"],
    "Yoga": ["Hatha", "Vinyasa"],
}
BASE_CAL = {"Chạy bộ": 10, "Gym": 7, "Bơi lội": 9, "Yoga": 4}   # calo/phut
INTENSITY = {"Nhẹ": 0.8, "Vừa": 1.0, "Nặng": 1.3}
ALL_SPORTS = "Tất cả"

users = {} # ten -> {"salt", "hash", "role"}
sessions = [] # buoi tap: id, owner, date, sport, exercise, minutes, intensity, cal
plans = [] # ke hoach: id, owner, name, sport, target_minutes, start, end
last_error = ""  # loi gan nhat khi doc/ghi file (giao dien hien thong bao)

def parse_date(text):
    return datetime.strptime(text, DATE_FORMAT)

def calc_calories(sport, minutes, intensity):
    return round(BASE_CAL[sport] * INTENSITY[intensity] * minutes)


def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
 
 
def _make_user(password, role):
    salt = secrets.token_hex(8)
    return {"salt": salt, "hash": hash_password(password, salt), "role": role}
 
 
def _next_id(items):
    return max((i["id"] for i in items), default=0) + 1
 
 

def _apply(data):
    """Nap du lieu doc tu file vao bien toan cuc; nem loi neu sai cau truc."""
    new_users = data["users"]
    new_sessions = data["sessions"]
    new_plans = data["plans"]
    if not (isinstance(new_users, dict) and isinstance(new_sessions, list)
            and isinstance(new_plans, list)):
        raise ValueError("Sai cấu trúc dữ liệu")
    for name, u in new_users.items():
        u["salt"], u["hash"], u["role"]          # kiem tra du khoa
    for s in new_sessions:
        s["id"], s["owner"], s["date"], s["minutes"], s["cal"]
    for p in new_plans:
        p["id"], p["owner"], p["target_minutes"], p["start"], p["end"]
    users.clear(); users.update(new_users)
    sessions[:] = new_sessions
    plans[:] = new_plans
 
 
def _reset_to_default():
    """Du lieu khoi tao: 1 admin, 1 nguoi dung demo kem du lieu mau."""
    users.clear(); sessions.clear(); plans.clear()
    users[config.DEFAULT_ADMIN[0]] = _make_user(config.DEFAULT_ADMIN[1], config.ROLE_ADMIN)
    demo = config.DEFAULT_USER[0]
    users[demo] = _make_user(config.DEFAULT_USER[1], config.ROLE_USER)
    generate_sample(demo, 12, rng=random.Random(config.SAMPLE_SEED), persist=False)
    today = datetime.now()
    plans.append({"id": 1, "owner": demo, "name": "Chạy 150 phút / 2 tuần",
                  "sport": "Chạy bộ", "target_minutes": 150,
                  "start": (today - timedelta(days=10)).strftime(DATE_FORMAT),
                  "end": (today + timedelta(days=3)).strftime(DATE_FORMAT)})
    plans.append({"id": 2, "owner": demo, "name": "Tổng thời gian tập tháng này",
                  "sport": ALL_SPORTS, "target_minutes": 600,
                  "start": (today - timedelta(days=14)).strftime(DATE_FORMAT),
                  "end": (today + timedelta(days=16)).strftime(DATE_FORMAT)})
 
 
def load():
    """Doc file JSON. File thieu -> tao moi; rong/hong -> sao luu file hong
    roi tao lai du lieu khoi tao. Tra ve True neu doc/khoi tao duoc."""
    global last_error
    last_error = ""
    path = config.DATA_FILE
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        if not raw.strip():
            raise ValueError("File dữ liệu rỗng")
        _apply(json.loads(raw))
        return True
    except FileNotFoundError:
        _reset_to_default()
        return save()
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        # JSONDecodeError la con cua ValueError
        message = f"File dữ liệu lỗi ({exc}). Đã tạo lại dữ liệu mẫu."
        try:
            shutil.copy2(path, path.parent / (path.stem + ".corrupt.json"))
        except OSError:
            pass
        _reset_to_default()
        save()
        last_error = message      # save() xoa last_error nen gan lai de giao dien bao
        return True
    except OSError as exc:
        last_error = f"Không đọc được file dữ liệu: {exc}"
        _reset_to_default()
        return False
 
 
def save():
    """Ghi an toan: sao luu ban cu, ghi file tam roi thay the."""
    global last_error
    last_error = ""
    try:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        path = config.DATA_FILE
        if path.exists():
            shutil.copy2(path, config.BACKUP_FILE)
        tmp = path.parent / (path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"users": users, "sessions": sessions, "plans": plans},
                      f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return True
    except OSError as exc:
        last_error = f"Không ghi được file dữ liệu: {exc}"
        return False
 
 
# ---------------------------------------------------------------- tai khoan
def register(username, password):
    # Thay the validators.valid_username bang Regex
    if not re.match(r"^[A-Za-z0-9_]{3,20}$", username):
        return False, "Tên đăng nhập 3-20 ký tự: chữ không dấu, số hoặc dấu _."
    
    # Thay the validators.valid_password bang len()
    if not isinstance(password, str) or len(password) < 4:
        return False, "Mật khẩu phải có ít nhất 4 ký tự."
        
    if username.lower() in (u.lower() for u in users):
        return False, "Tên đăng nhập đã tồn tại."
        
    users[username] = _make_user(password, config.ROLE_USER)
    save()
    return True, "Đăng ký thành công, hãy đăng nhập."
 
 
def authenticate(username, password):
    """Tra ve vai tro neu dung, nguoc lai None."""
    u = users.get(username)
    if u and secrets.compare_digest(hash_password(password, u["salt"]), u["hash"]):
        return u["role"]
    return None
 
 
def change_password(username, old, new):
    if authenticate(username, old) is None:
        return False, "Mật khẩu hiện tại không đúng."
        
    # Thay the validators.valid_password bang len()
    if not isinstance(new, str) or len(new) < 4:
        return False, "Mật khẩu mới phải có ít nhất 4 ký tự."
        
    if new == old:
        return False, "Mật khẩu mới phải khác mật khẩu cũ."
        
    users[username] = _make_user(new, users[username]["role"])
    save()
    return True, "Đã đổi mật khẩu."
 
 
def list_users():
    """[(ten, vai tro, so buoi tap)]"""
    return [(n, u["role"], sum(1 for s in sessions if s["owner"] == n))
            for n, u in sorted(users.items())]
 
 
# ---------------------------------------------------------------- buoi tap
def sessions_for(username, role):
    if role == config.ROLE_ADMIN:
        return list(sessions)
    return [s for s in sessions if s["owner"] == username]
 
 
def get_session(sid):
    return next((s for s in sessions if s["id"] == sid), None)
 
 
def add_session(data, owner, persist=True):
    item = dict(data, id=_next_id(sessions), owner=owner)
    sessions.append(item)
    if persist:
        save()
    return item
 
 
def update_session(sid, data):
    s = get_session(sid)
    if s:
        s.update(data)
        save()
 
 
def delete_session(sid):
    s = get_session(sid)
    if s:
        sessions.remove(s)
        save()
 
 
def generate_sample(owner, n=10, rng=None, days_back=14, persist=True):
    """Sinh n buoi tap ngau nhien (module random) cho 'owner'."""
    rng = rng or random.Random()
    today = datetime.now()
    for _ in range(n):
        sport = rng.choice(list(EXERCISES))
        minutes = rng.choice([20, 30, 45, 60, 75, 90])
        inten = rng.choice(list(INTENSITY))
        day = today - timedelta(days=rng.randint(0, days_back - 1))
        add_session({"date": day.strftime(DATE_FORMAT), "sport": sport,
                     "exercise": rng.choice(EXERCISES[sport]), "minutes": minutes,
                     "intensity": inten,
                     "cal": calc_calories(sport, minutes, inten)},
                    owner, persist=False)
    if persist:
        save()
 
 
# ---------------------------------------------------------------- ke hoach
def plans_for(username, role):
    if role == config.ROLE_ADMIN:
        return list(plans)
    return [p for p in plans if p["owner"] == username]
 
 
def get_plan(pid):
    return next((p for p in plans if p["id"] == pid), None)
 
 
def add_plan(data, owner):
    item = dict(data, id=_next_id(plans), owner=owner)
    plans.append(item)
    save()
    return item
 
 
def delete_plan(pid):
    p = get_plan(pid)
    if p:
        plans.remove(p)
        save()
 
 
def plan_progress(plan):
    """(so phut da tap trong ky ke hoach, % hoan thanh toi da 100)."""
    try:
        start, end = parse_date(plan["start"]), parse_date(plan["end"])
    except (ValueError, KeyError):
        return 0, 0.0
    done = 0
    for s in sessions:
        if s["owner"] != plan["owner"]:
            continue
        if plan["sport"] != ALL_SPORTS and s["sport"] != plan["sport"]:
            continue
        try:
            d = parse_date(s["date"])
        except ValueError:
            continue
        if start <= d <= end:
            done += s["minutes"]
    target = plan["target_minutes"]
    pct = min(100.0, done * 100.0 / target) if target > 0 else 0.0   # tranh chia 0
    return done, pct
 
 
def overall_progress(plan_list):
    """% hoan thanh gop cua nhieu ke hoach (0 neu khong co)."""
    total = sum(p["target_minutes"] for p in plan_list)
    if total <= 0:
        return 0.0
    got = sum(min(plan_progress(p)[0], p["target_minutes"]) for p in plan_list)
    return got * 100.0 / total
 
 
def plans_due_soon(username, days):
    """Ke hoach cua nguoi dung chua xong va het han trong 'days' ngay toi."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    out = []
    for p in plans:
        if p["owner"] != username:
            continue
        try:
            end = parse_date(p["end"])
        except ValueError:
            continue
        if today <= end <= today + timedelta(days=days) and plan_progress(p)[1] < 100:
            out.append(p)
    return out
 
 
def minutes_per_day(rows, days):
    """[(dd/mm, tong phut)] cho 'days' ngay gan nhat (cu -> moi)."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    buckets = {(today - timedelta(days=i)).date(): 0 for i in range(days - 1, -1, -1)}
    for s in rows:
        try:
            d = parse_date(s["date"]).date()
        except ValueError:
            continue
        if d in buckets:
            buckets[d] += s["minutes"]
    return [(d.strftime("%d/%m"), m) for d, m in buckets.items()]