"""Du lieu dung chung. Hien luu trong bo nho; khico phan luu tru (file/SQLite) thi chi can sua cac ham trong file nay."""

EXERCISES = {
    "Chạy bộ": ["Chạy chậm", "Chạy nước rút", "Chạy địa hình"],
    "Gym": ["Đẩy ngực", "Squat", "Deadlift", "Kéo xà"],
    "Bơi lội": ["Bơi ếch", "Bơi sải", "Bơi bướm"],
    "Yoga": ["Hatha", "Vinyasa"],
}
BASE_CAL = {"Chạy bộ": 10, "Gym": 7, "Bơi lội": 9, "Yoga": 4}   # calo/phut
INTENSITY = {"Nhẹ": 0.8, "Vừa": 1.0, "Nặng": 1.3}

users = {"admin": "123456"}
sessions = []
_next_id = 1


def calc_calories(sport, minutes, intensity):
    return round(BASE_CAL[sport] * INTENSITY[intensity] * minutes)


def add_session(data):
    global _next_id
    data = dict(data, id=_next_id)
    _next_id += 1
    sessions.append(data)
    return data


def get_session(sid):
    return next((s for s in sessions if s["id"] == sid), None)


def update_session(sid, data):
    s = get_session(sid)
    if s:
        s.update(data)


def delete_session(sid):
    s = get_session(sid)
    if s:
        sessions.remove(s)