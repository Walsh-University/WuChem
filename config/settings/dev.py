from dotenv import load_dotenv

load_dotenv(override=True)  # Use local development values from .env

from .base import *  # noqa: E402

DEBUG = True

# local defaults
if not ALLOWED_HOSTS:  # noqa
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"]

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
