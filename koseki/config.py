import secrets


class KosekiConfig(object):
    DEBUG = False

    #
    # Koseki config
    #
    KOSEKI_VERSION = "MMXXI"

    @property
    def FOOTER(self) -> str:
        return "koseki &copy; " + self.KOSEKI_VERSION

    #
    # Hosting config
    #
    URL_BASE = "http://localhost:5000"
    UPLOAD_FOLDER = "./data"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True

    @property
    def SECRET_KEY(self) -> str:
        return secrets.token_urlsafe(16)

    #
    # Database config
    #
    DB_HOST = "127.0.0.1"
    DB_USER = "root"
    DB_DATABASE = "koseki"
    DB_PASSWORD = "password"

    #
    # Email config
    #
    SMTP_SERVER = "127.0.0.1"
    EMAIL_FROM = "Koseki Member management <member@acme.nu>"
    EMAIL_SUBJECT = "Koseki Member management"

    #
    # Organisation config
    #
    ORG_NAME = "Koseki"
    ORG_EMAIL = "contact@acme.nu"

    #
    # Plugins - Must be correctly capitalized!
    #
    # Default:
    #   CAS - Integration with Lund University login system (Central Authentication System)
    #   Salto - Integration with Lund University card system
    #   Kiosk - Touch interface store solution
    #   Store - Handles product registration
    #   Print - Allows sending documents to CUPS for printing (Linux-only!)
    #
    PLUGINS: list[str] = ["CAS", "Salto", "Kiosk", "Store"]
    #PLUGINS: list[str] = list()
