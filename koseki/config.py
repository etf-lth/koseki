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
    DB_HOST = "127.0.0.1"
    DB_USER = "root"
    DB_DATABASE = "koseki"
    DB_PASSWORD = "password"

    #
    # Email config
    #
    SMTP_USE_TLS = False
    SMTP_SERVER = "127.0.0.1"

    @property
    def SMTP_PORT(self) -> int:  # pylint: disable=invalid-name
        return 587 if self.SMTP_USE_TLS else 25
    EMAIL_FROM = "Koseki Member management <member@acme.nu>"
    EMAIL_SUBJECT = "Koseki Member management"

    #
    # Organisation config
    #
    ORG_NAME = "Koseki"
    ORG_EMAIL = "contact@acme.nu"

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
    #   Salto - Integration with Lund University card system
    #   Kiosk - Touch interface store solution
    #   Store - Handles product registration
    #   Print - Allows sending documents to CUPS for printing (Linux-only!)
    #
    PLUGINS: list[str] = ["CAS", "Salto", "Kiosk", "Store"]
    #PLUGINS: list[str] = list()
