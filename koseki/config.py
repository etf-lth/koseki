import secrets


class KosekiConfig():
    DEBUG = False

    #
    # Koseki
    #
    KOSEKI_VERSION = "MMXXI"

    @property
    def FOOTER(self) -> str:  # pylint: disable=invalid-name
        return "koseki &copy; %s" % self.KOSEKI_VERSION

    #
    # Hosting config
    #
    URL_BASE = "http://localhost:5000"
    WEB_HOST = "localhost"
    WEB_PORT = 5000
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True

    @property
    def SECRET_KEY(self) -> str:  # pylint: disable=invalid-name
        return secrets.token_urlsafe(16)

    #
    # Database config
    #
    DB_TYPE = "MySQL"
    DB_HOST = "127.0.0.1"
    DB_USER = "root"
    DB_DATABASE = "koseki"
    DB_PASSWORD = "password"
    DB_SQLITE_PATH = "koseki.db"

    #
    # Email config
    #
    SMTP_USE_TLS = False
    SMTP_SERVER = "127.0.0.1"

    @property
    def SMTP_PORT(self) -> int:  # pylint: disable=invalid-name
        return 587 if self.SMTP_USE_TLS else 25
    EMAIL_FROM = "Koseki Member management <member@example.com>"
    EMAIL_SUBJECT = "Koseki Member management"

    #
    # Organisation config
    #
    ORG_NAME = "Example Org."
    ORG_EMAIL = "contact@example.com"

    #
    # User config
    #
    USER_USERNAME_ENABLED = False
    USER_ADDRESS_ENABLED = False
    USER_PHONE_NUMBER_ENABLED = False

    #
    # Payment config
    #
    PAYMENT_YEARLY_FEE = 200
    PAYMENT_DEBT_ENABLED = False
    PAYMENT_METHOD_BANKGIRO = "XXX-YYYY"
    PAYMENT_METHOD_SWISH = "123 XXX YY ZZ"

    #
    # Theme configs
    #
    # Theme names are always all-lowercase.
    THEME = "koseki"

    #
    # Plugins - Must be correctly capitalized!
    #
    # Default:
    #   CAS - Integration with Lund University login system (Central Authentication System)
    #   OIDC - Allows login to 3rd party systems with Koseki account
    #   Salto - Integration with Lund University card system
    #   Kiosk - Touch interface store solution
    #   Store - Handles product registration
    #   Print - Allows sending documents to CUPS for printing (Linux-only!)
    #
    PLUGINS: list[str] = ["CAS", "OIDC", "Salto", "Kiosk", "Store"]
    #PLUGINS: list[str] = list()
