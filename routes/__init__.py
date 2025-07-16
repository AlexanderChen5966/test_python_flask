# routes/__init__.py
# 此檔案讓 routes 資料夾成為 Python 模組，可用於 Blueprint 統一匯入（選擇性）

# 若有需要統一導入所有 Blueprint，也可以這樣寫：
# from .user_routes import user_bp
# from .checkin_routes import checkin_bp
# from .line_reply_routes import line_reply_bp
# from .webhook import webhook_bp

# 然後在 app.py 使用 from routes import user_bp, ...
