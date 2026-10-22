"""Kiem tra du lieu nhap bang dieu kien + Regular Expression
(ten dang nhap, ngay thang)."""
import re
from datetime import datetime

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
DATE_RE = re.compile(r"^(0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/\d{4}$")


def valid_username(text):
    """3-20 ky tu: chu cai khong dau, so, dau gach duoi."""
    return bool(USERNAME_RE.match(text or ""))


def valid_date(text):
    """Dung dinh dang dd/mm/yyyy va la ngay co that (vd 31/02 la sai)."""
    if not DATE_RE.match(text or ""):
        return False
    try:
        datetime.strptime(text, "%d/%m/%Y")
    except ValueError:
        return False
    return True

def valid_password(text):
    return isinstance(text, str) and len(text) >= 4