"""File cấu hình: đường dẫn dữ liệu, tham số mặc định, thiết lập chung."""
from pathlib import Path

# --- Đường dẫn file dữ liệu (Dùng cho main.py, crawler.py) ---
EXERCISES_FILE = "exercises.json"
ACCOUNTS_FILE = "accounts.json"
ACTIVITIES_FILE = "activities.json"

# --- Đường dẫn dữ liệu (Dùng cho data.py) ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "workout_data.json"
BACKUP_FILE = DATA_DIR / "workout_data.bak.json"

# --- Thiết lập giao diện ---
APP_TITLE = "Hệ Thống Quản Lý Luyện Tập Thể Thao"
WINDOW_SIZE = "1100x750"
WINDOW_LOGIN_SIZE = "500x450"

# --- Phân quyền ---
ROLE_ADMIN = "admin"
ROLE_USER = "user"

# --- Tài khoản mặc định (Dùng cho data.py) ---
DEFAULT_ADMIN = ("admin", "123")
DEFAULT_USER = ("user1", "123456")

# --- Tài khoản mặc định (Dùng cho main.py nếu file JSON trống) ---
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASS = "123"

# --- Cấu hình Crawler ---
CRAWLER_MAX_PER_SPORT = 3
CRAWLER_MAX_PAGES = 5

# --- Từ điển chuyển đổi tên Môn tập từ tiếng Anh sang tiếng Việt ---
SPORT_VI = {
    "Running": "Chạy bộ",
    "Swimming": "Bơi lội",
    "Cycling": "Đạp xe"
}
# Từ điển đảo ngược (Tiếng Việt -> Tiếng Anh) để xử lý logic
SPORT_EN = {v: k for k, v in SPORT_VI.items()}

CHART_DAYS = 7  # Số ngày hiển thị trên biểu đồ cột (7 ngày gần nhất)