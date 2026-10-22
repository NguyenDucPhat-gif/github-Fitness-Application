"""File cau hinh: duong dan du lieu, tham so mac dinh, thiet lap chung.
Dung duong dan TUONG DOI so voi thu muc chua ma nguon (khong phu thuoc may)."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "workout_data.json"
BACKUP_FILE = DATA_DIR / "workout_data.bak.json"

APP_TITLE = "Theo dõi luyện tập thể thao"
WINDOW_SIZE = "980x700"
WINDOW_MIN_SIZE = (860, 620)

ROLE_ADMIN = "admin"
ROLE_USER = "user"
ROLE_LABEL = {ROLE_ADMIN: "Quản trị viên", ROLE_USER: "Người dùng"}

# Tai khoan demo tao lan chay dau tien (nen doi mat khau sau khi dang nhap)
DEFAULT_ADMIN = ("admin", "123456")
DEFAULT_USER = ("user1", "123456")

REMINDER_DAYS = 3     # nhac ke hoach sap het han trong N ngay
CHART_DAYS = 7        # so ngay hien thi tren bieu do
SAMPLE_SEED = 2026    # seed cho du lieu mau (tai lap duoc)