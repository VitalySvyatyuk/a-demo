import sys

from settings import DATABASES, PROJECT_ROOT
import os

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

STATIC_URL = '/static/'
CKEDITOR_JS_URL = '/JS'
LANGUAGE_CODE = 'ru'
CELERY_RESULT_BACKEND = 'cache'

DATABASES['default']['PORT'] = 5432
DATABASES['default']['HOST'] = 'localhost'
for db in ('real', 'demo'):
#     # DATABASES[db]['HOST'] = 'localhost'
#     # DATABASES[db]['PORT'] = '3306'
     DATABASES[db]['HOST'] = '10.0.0.30'
     DATABASES[db]['PORT'] = '6306'

WEBSOCKET_TORNADO_URL = 'ws://10.1.1.233:8500/quotes'

THUMBNAIL_DEBUG = False

SMS_BACKENDS = (
    "sms.backends.PrintBackend",
)

SMS_BACKENDS_MASKS = (
)
DATABASES['default'] = {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'arum',
        'USER': 'afanasev',               # Not used with sqlite3.
        'PASSWORD': 'qwe',          # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                  # Set to empty string for default. Not used with sqlite3.
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'WARN',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        }
    },

    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' + 'pathname=%(pathname)s lineno=%(lineno)s '
                       + 'funcname=%(funcName)s %(message)s '),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
        }
    }
}

ENGINES = {
    'default': {
        'db': 'mysql://webuser:V3fb^23J609G4$1@10.1.0.55:10445/gcmtsrv_real?charset=utf8',
        'sock': ('10.1.0.55', 10443),
        'custom': ("10.1.0.55", 10446),
        'custom2': ("10.1.0.55", 10447),
        'custom3': ("88.198.194.84", 12344),
        },
    'demo': {
        'db': 'mysql://webuser:V3fb^23J609G4$1@10.1.0.55:10445/gcmtsrv_demo?charset=utf8',
        'sock': ('10.1.0.55', 10444),
        'webtrading': ('10.1.0.55', 10449),
        'custom': ("10.1.0.55", 10450),
    },

}


# DATABASES['asterisk'] = {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'asterisk',
#         'USER': 'webuser',
#         'PASSWORD': 'klyWakfo',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }

USE_DEMO_ONLY = True

if USE_DEMO_ONLY:
    from settings import DEMO_CFH_API_PASSWORD, DEMO_CFH_API_BROKER, DEMO_CFH_API_CLIENTADMIN, DEMO_CFH_API_LOGIN,\
        DEMO_CFH_CLIENT_TEMPLATES, DEMO_CFH_DEPOSIT_ACCOUNT_ID, DEMO_CFH_WITHDRAW_ACCOUNT_ID, DEMO_CFH_BROKER_ID


    CFH_API_BROKER = DEMO_CFH_API_BROKER
    CFH_API_CLIENTADMIN = DEMO_CFH_API_CLIENTADMIN
    CFH_API_LOGIN = DEMO_CFH_API_LOGIN
    CFH_API_PASSWORD = DEMO_CFH_API_PASSWORD
    CFH_CLIENT_TEMPLATES = DEMO_CFH_CLIENT_TEMPLATES
    CFH_DEPOSIT_ACCOUNT_ID = DEMO_CFH_DEPOSIT_ACCOUNT_ID
    CFH_WITHDRAW_ACCOUNT_ID = DEMO_CFH_WITHDRAW_ACCOUNT_ID
    CFH_BROKER_ID = DEMO_CFH_BROKER_ID



LOCALE_PATHS = (
os.path.join(PROJECT_ROOT, 'locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/project/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/platforms/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/callback_request/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/contract_specs/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/currencies/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/education/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/faq/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/friend_recommend/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/gcrm/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/issuetracker/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/log/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/otp/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/payments/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/private_office/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/profiles/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/referral/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/registration/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/reports/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/requisits/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/transfers/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/uptrader_cms/locale'),
os.path.join(PROJECT_ROOT, 'django-gc-shared/massmail/locale'),

)

if any(map(lambda s: 'test' in s, sys.argv[:2])):
    del DATABASES['real']
    del DATABASES['demo']
    del DATABASES['asterisk']
    INSTALLED_APPS += (
    'test_without_migrations',)
