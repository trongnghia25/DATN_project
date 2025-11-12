from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:  # Kiểm tra trạng thái đăng nhập
            return redirect(url_for('login'))  # Chuyển hướng đến trang đăng nhập
        return f(*args, **kwargs)  # Cho phép truy cập endpoint nếu đã đăng nhập
    return decorated_function
