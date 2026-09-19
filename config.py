import os

class Config:
    # --- Base ---
    SECRET_KEY = os.environ.get('SECRET_KEY', 'loge-facile-niger-secret-2025')
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # --- Base de donnees SQLite ---
    DATABASE = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'logefacile.db'))

    # --- Upload fichiers ---
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'static', 'uploads'))
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi'}

    # --- Email Gmail ---
    MAIL_SERVER   = 'smtp.gmail.com'
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'logefacile.niger@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'TON_MOT_DE_PASSE_APP_GMAIL')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', 'logefacile.niger@gmail.com')
    MAIL_RECEIVER = os.environ.get('MAIL_RECEIVER', 'logefacile.niger@gmail.com')

    # --- WhatsApp Twilio (optionnel) ---
    TWILIO_SID           = os.environ.get('TWILIO_SID', '')
    TWILIO_AUTH_TOKEN    = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_WHATSAPP_FROM = 'whatsapp:+22797431619'
    TWILIO_WHATSAPP_TO   = os.environ.get('TWILIO_WHATSAPP_TO', 'whatsapp:+22797431619')

    # --- Admin ---
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'LogeFacile2025!')
