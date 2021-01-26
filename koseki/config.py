import secrets


class KosekiConfig(object):
    DEBUG = False

    @property
    def SECRET_KEY(self):
        return secrets.token_urlsafe(16)

    # Password used for Kiosk unlock
    KIOSK_KEY = "123456"

    DB_HOST = "127.0.0.1"
    DB_USER = "root"
    DB_DATABASE = "koseki"
    DB_PASSWORD = "password"

    SMTP_SERVER = "127.0.0.1"
    EMAIL_FROM = "Koseki Member management <member@acme.nu>"
    EMAIL_SUBJECT = "Koseki Member management"

    ORG_NAME = "Koseki"
    ORG_EMAIL = "contact@acme.nu"

    URL_BASE = "http://localhost:5000"

    UPLOAD_FOLDER = "./data"

    FOOTER = "koseki &copy; MMXXI"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
