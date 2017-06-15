# -*- coding: utf-8 -*-
import sys
import warnings
import logging
import os
import re

from datetime import timedelta
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "django-shared"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "django-gc-shared"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "sites"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "apps"))


DEBUG = False

# The available languages
LANGUAGES = (
    ('ru', 'Russian'),
    ('en', 'English'),
)
LANGUAGE_CODES = tuple(l[0] for l in LANGUAGES)

ROSETTA_LANGUAGE_GROUPS = True
ROSETTA_MAIN_LANGUAGE = "ru"

# The default language for the site. If not overriden in EXPLICIT_HOST_LANGUAGES, it is used.
LANGUAGE_CODE = 'en'

# Each language should define its hosts, see comments below
LANGUAGE_SETTINGS = {
    "ru": {
        # If HTTP_HOST(request.get_host()) matches the key,
        # the language is set via multilang.middleware.HostLanguageMiddleware
        # Also, there is a template loader "multilang.loaders.MultilangLoader", which searches
        # for the template in separate dirs
        "hosts": ('ru.arumcapital.eu', 'arum.uptrader.us', 'localhost:8000', 'localhost:8001'),
        # Used by multilang.middleware.GeoIPRedirectMiddleware
        "redirect_to": "https://ru.arumcapital.eu",
        # This field specifies URL prefixes that are used for language detection
        # I.e.: https://grandcapital.net/eng/bla/bla/bla
        "urls": (),
    },
    "en": {
        "hosts": ('arumcapital.eu', 'arum_eng.uptrader.us', 'en.localhost:8081', 'en.localhost:8001'),
        "redirect_to": "https://arumcapital.eu",
        "urls": ("eng",),
    },

}

ALLOWED_HOSTS = ['arum.uptrader.us', 'arum.dev.uptrader', 'arumcapital.eu', 'ru.arumcapital.eu']

LANGUAGE_NEUTRAL_URLS = (
)

# URLs matching these rules won't take part in GeoIP Redirect
LANGUAGE_REDIRECT_EXEMPT_URLS = (
    r'/office/accounts/deposit/(\d+/)?result/?', #This URL is used by payment systems robots, we don't wont to redirect them
    r'/my/office/accounts/deposit/(\d+/)?result/?', #This URL is used by payment systems robots, we don't wont to redirect them
    r'/accounts/partner/reg_html/', #Partner registration form, doesn't work in English version yet
    r'/my/accounts/partner/reg_html/', #Partner registration form, doesn't work in English version yet
    r'/accounts/partner/reg_action/', #Partner registration form, doesn't work in English version yet
    r'/my/accounts/partner/reg_action/', #Partner registration form, doesn't work in English version yet
)

#for locale-files in project root (https://code.djangoproject.com/ticket/5494)
LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

ADMINS = (
    ('Arum support', 'support@arumcapital.eu'),
    ('Vasily Alexeev', 'va@uptrader.us'),
)

ACCOUNT_REGISTRATION_CC_EMAIL = ''

MANAGERS = ADMINS

BACKOFFICE = ('Arum backoffice', 'backoffice@arumcapital.eu')

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 500,
        'BINARY': False,
        'KEY_PREFIX': "arum",
        'OPTIONS': {  # Maps to pylibmc "behaviors"
            'tcp_nodelay': True,
            'verify_keys': True,
        }
    },
    'important_data': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_important',
    }
}

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'arum_dev',                    # Or path to database file if using sqlite3.
        'USER': 'webuser',               # Not used with sqlite3.
        'PASSWORD': 'klyWakfo',          # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                  # Set to empty string for default. Not used with sqlite3.
#        'CONN_MAX_AGE': None,            # unlimited
    },
    'real': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gcmtsrv_real',
        'USER': 'webuser',
        'PASSWORD': 'V3fb^23J609G4$1',
        'HOST': '144.76.27.6',
        'CONN_MAX_AGE': 600,
    },
    'demo': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gcmtsrv_demo',
        'USER': 'webuser',
        'PASSWORD': 'V3fb^23J609G4$1',
        'HOST': '144.76.27.6',
        'CONN_MAX_AGE': 600,
    },
    'db_archive': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gcmtsrv_arch',
        'USER': 'webuser',
        'PASSWORD': 'V3fb^23J609G4$1',
        'HOST': '144.76.27.6',
        'CONN_MAX_AGE': 600,
    },
    'specifications': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'specifications',
        'USER': 'webuser',
        'PASSWORD': 'V3fb^23J609G4$1',
        'HOST': '144.76.27.6',
        'CONN_MAX_AGE': 600,
    },
    'config': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'config',
        'USER': 'webuser',
        'PASSWORD': 'V3fb^23J609G4$1',
        'HOST': '144.76.27.6',
        'CONN_MAX_AGE': 600,
    },
    'options': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'options',
        'USER': 'webuser',
        'PASSWORD': 'V3fb^23J609G4$1',
        'HOST': '144.76.27.6',
        'CONN_MAX_AGE': 600,
    },
    'mt4_externaldb': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gcwebsrv',
        'USER': 'webuser',
        'PASSWORD': 'V3fb^23J609G4$1',
        'HOST': '144.76.27.6',
        'CONN_MAX_AGE': 600,
    },
    'asterisk': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'asterisk',
        'USER': 'asterisk',
        'PASSWORD': 'PollyWantsASome543',
        'HOST': '138.201.206.11',
        'PORT': '',
    }
}

DATABASE_ROUTERS = [
    'platforms.mt4.external.routers.Mt4ExternalRouter',
    'contract_specs.routers.MultiDBRouter',
    'telephony.routers.AsteriskDBRouter',
]

TIME_ZONE = 'Europe/Moscow'

SITE_NAME = 'Arum Capital'

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'uploads')
MEDIA_URL = '/uploads/'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'sitestatic')
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
    os.path.join(PROJECT_ROOT, 'bower_components'),
    os.path.join(PROJECT_ROOT, 'node_modules'),
)


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'coffeescript.finders.CoffeescriptFinder',
)

CAPTCHA_SIZE = (175, 100)

ADMIN_MEDIA_PREFIX = '/static/admin/'

SECRET_KEY = 'O2_6xvnhC(W:f(Y-QKgQH{Ms6K;!.?4yTHzI*}]Z~@fl$-/8e4'
EMAIL_UNSUBSCRIBE_SECRET_KEY = 'Xm[~rRn/iFRZ4-qMIn8lpn!UfO[9B4aeI,17M)*D=9uSH2Ghb['

SSO_SECRET = SECRET_KEY

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['django-gc-shared/project/static/svg', ],
        'OPTIONS': {
            'loaders': [
                # Pyjade template loader conflicts with Hamlpy, so order is important!
                'hamlpy.template.loaders.HamlPyFilesystemLoader',
                'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
                ('pyjade.ext.django.Loader', (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                )),
                'multilang.loaders.MultilangLoader',
                'django.template.loaders.filesystem.Loader',
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'project.context_processors.settings',
                'multilang.context_processors.language_settings',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',

            ]
        },
    },
]


MIDDLEWARE_CLASSES = (
    'node.middleware.NodeUrlAliasMiddleware',
    'project.middleware.XForwardedForMiddleware',
    'project.middleware.ExceptionUserInfoMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'project.middleware.HeaderSessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'multilang.middleware.LanguageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'referral.middleware.AgentCodeMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'linaro_django_pagination.middleware.PaginationMiddleware',
    'visitor_analytics.middleware.UtmMiddleware',
    'log.middleware.LogMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
    'massmail.middleware.MassMailMiddleware',
    'crm.middleware.CorsMiddleware',
)

ROOT_URLCONF = 'sites.default.urls'

ROOT_HOSTNAME = "arum.uptrader.us"

INSTALLED_APPS = (
    # messages apps are here to work around a bug in south - conflicts with django.contrib.messages
    # Extras should be above messages
    'private_messages',
    'modeltranslation',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.webdesign',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.postgres',

    'project',

    # External.
    'notification',
    'treemenus',
    'ajax_validation',
    'ajax_select',
    'django_extensions',
    'rosetta',
    'ckeditor',
    'linaro_django_pagination',
    'paging',
    'pytils',
    'sorl.thumbnail',
    'djcelery',
    'pyjade.ext.django',
    'django_hstore',

    'registration',
    'sms',
    'profiles',
    'geobase',
    'payments',
    'issuetracker',
    'platforms',
    'platforms.mt4.external',
    'reports',
    'shared',
    'node',
    'uptrader_cms',
    'education',
    'video',
    'faq',
    'callback_request',
    'massmail',

    'referral',
    'requisits',
    'transfers',
    'currencies',
    'typical_comments',
    'friend_recommend',
    'i18n_extras',
    'coffeescript',
    'log',
    'django_otp',
    'visitor_analytics',
    'otp',
    'rest_framework',
    'raven.contrib.django.raven_compat',
    'private_office',
    'contract_specs',

    'crm',
    'gcrm',
    'telephony',
)

AJAX_LOOKUP_CHANNELS = {
    'indicator': {'model': 'uptrader_cms.indicator', 'search_field': 'name'}
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'project.rest_fields.exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'project.rest_fields.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'project.rest_serializers.CustomPaginationSerializer',
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.OrderingFilter',),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_METADATA_CLASS': 'project.rest_fields.ExtraMetadata',
    'UNICODE_JSON': False,
}

FIXTURE_DIRS = (
    "fixtures",
)

# -- Django debug toolbar
INTERNAL_IPS = (
    '127.0.0.1',
)

# --- contrib.gis.utils.GeoIP used in multilang.middleware.GeoIPRedirectMiddleware

GEOIP_PATH = "/usr/share/GeoIP"

#--- contrib.auth
AUTH_PROFILE_MODULE = 'profiles.UserProfile'
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "registration.backends.EmailBackend"
)

LOGIN_FOR = 14  # Number of days the user will be logged in.
LOGIN_URL = '/my/accounts/login/'
LOGIN_REDIRECT_URL = '/'

# --- contrib.sessions
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# --- mailing
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 2525
# EMAIL_HOST_USER = ""
# EMAIL_HOST_PASSWORD = ""
# EMAIL_USE_TLS = True

EMAIL_SUBJECT_PREFIX = '[Arum Capital] '
SERVER_EMAIL = 'Arum Capital <noreply@arumcapital.eu>'

EMAILS = {
    'default': SERVER_EMAIL,
}
DEFAULT_FROM_EMAIL = EMAILS['default']

# --- logging
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILENAME = os.path.join(LOG_DIR, 'django.log')
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# --- modeltranslation
MODELTRANSLATION_FALLBACK_LANGUAGES = ('en', 'ru')
DEFAULT_LANGUAGE = "en"

# -- django_nose
#
# Note(Sergei): commented out, not using tests anyway :(
#
# if DEBUG:
#     INSTALLED_APPS += ("django_nose", )
#     TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
#     NOSE_ARGS = (
#         "--rednose", "--nocapture", "--detailed-errors",
#         "--verbosity=1",
#         # Uncomment this, if you need pdb.
#         # "--pdb", "--pdb-failures",
#         "apps/"
#     )

# --- registration

# This is the number of days users will have to activate their accounts
# after registering. If a user does not activate within that period, the
# account will remain permanently inactive and may be deleted by maintenance
# scripts provided in django-registration.
ACCOUNT_ACTIVATION_DAYS = 14

# -- sms
SMS_BACKENDS = (
    "sms.backends.PlivoSMSBackend",
    # "sms.backends.SMSRuBackend",
    # "sms.backends.MTTBackend",
    # "sms.backends.WebSMSBackend",
)

SMS_BACKENDS_MASKS = (
#    (r'79[18]\d+', "sms.backends.WebSMSBackend"),  # 910-919 and 980-989 are all MTS
    (r'\+?79\d+', 'sms.backends.SMSRuBackend'), # Russia through sms.ru
    # (r'\+?[^+7]\d+', "sms.backends.PlivoSMSBackend"),  # Non-Russian numbers
)

SMSRU_API_ID = "649CEC2D-0FBA-3D16-42DF-9260E48ED259"
SMSRU_SENDER = ""

WEBSMS_USERNAME = ""
WEBSMS_PASSWORD = ""
WEBSMS_SENDER = ""
WEBSMS_DEBUG = ""

MTTSMS_USERNAME = ""
MTTSMS_PASSWORD = ""
MTTSMS_SENDER = ""

PLIVO_AUTH_ID = "MANTE4ZJYZNGNMZDYYMD"
PLIVO_AUTH_TOKEN = "ZWU4ZTQ1MDJhMTI2NTllMTY4MmRhNDNkNTE2ODli"
PLIVO_SENDER = "+12093171507"

UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads')

###########
# Massmail
###########

MASSMAIL_DEFAULT_FROM_EMAIL = "Arum News <news@arumcapital.eu>"
MASSMAIL_DEFAULT_REPLY_TO = "info@arumcapital.eu"
MASSMAIL_UNSUBSCRIBE_EMAIL = "list-unsubscribe@arumcapital.eu"
MASSMAIL_UNSUBSCRIBE_MAILBOX_PASSWORD = ""
MASSMAIL_UNSUBSCRIBE_MAILBOX_POP_SERVER = "localhost"

#####################################################################
############# PAYMENTS
#####################################################################

CHARGEBACK_PAYMENT_SYSTEMS = ()

PAYMENTS_UNAVAILABLE = False

###
# Accentpay settings
###

ACCENTPAY_ACCOUNT = "3515"
ACCENTPAY_SECRET = "JXFSsySEgY2G68a/4MxQ65qdAQA="

# The secret word MUST be any  lowercase string, submitted in the 'Merchant Tools' section.
MONEYBOOKERS_SECRET = "arumarum"
# Payee email address (this is where all the deposited funds will go eventually).
MONEYBOOKERS_TO = {
    "USD": "ceo@arumcapital.eu",
}

NETELLER_TEST_MERCHANT_ID = "33935"
NETELLER_TEST_MERCHANT_KEY = "542462"

NETELLER_MERCHANT_ID = "AAABW8S3jAUGCQKV"
NETELLER_SECRET_KEY = "0.BK2GLLgoicN9YBbrXCPw-fwhdS8NfFmgUnHX-UA6vjE.EAAQrysNthlgV66dxbf8fKhYsqUFGxE"

###
# Western Union, Migom, FastPost settings
###

PAYMENTS_RECEIVER = ""

# --- other
UPLOAD_PATH = 'uploads'

# --- reports
SAVED_REPORTS_PATH = os.path.join(PROJECT_ROOT, 'generated_reports/')
TRUSTED_REPORT_IPS = []  # These IPs are allowed to generate Excel reports

# Webtrader

WEBTRADER_MASTER_KEY = "password123"
WEBTRADER_PLUGIN_KEY = "TLJHBHGUYBVDRDFMKJUYQWEZXPNJKVLKG"

WEBTRADER_CONSOLE_LOGGING = False

# Default plugin passwords
MT4_SERVER_ENCODING = 'cp1251'
MT4_SERVER_SOCKET_TIMEOUT = 5
MT4_SERVER_SOCKET_RETRIES_NUMBER = 2
MT4_SERVER_SOCKET_RETRY_TIMEOUT = 2  # Seconds, for use in time.sleep()
MT4_MASTER_PASSWORD = 'Master102938'

MT4_PLUGIN_UINFO_MASTER_PASSWORD = 'f4ghB32dB5&&tr'
MT4_PLUGIN_UINFO_KEY = 'ADGHBVSDFERTASLKMHNBDGROPJDGFT'

WEBSOCKET_TORNADO_URL = 'wss://ws.grandcapital.net/'
ORDER_TRADES_URL = "http://localhost:8500/order_trades"

#--- Path to wkhtml executable
WKHTML_PATH = os.path.join(PROJECT_ROOT, 'wkhtmltopdf-amd64')
WKHTML_DEFAULT_ARGS = ['-T', '0', '-B', '0', '-L', '0', '-R', '0','--encoding', 'utf-8', ]

SESSION_COOKIE_AGE = 2592000  # 30 days
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

MT4_ACCOUNT_ENGINES_NAMES = ['default', 'db_archive', 'demo']
ENGINES = {
    #'default': {
    #    'sock': ('188.138.56.20', 443),
    #    'reporter_restart_url': 'http://95.215.1.135:8135/',
    #    'test_integrity': True,
    #},
    'default': {
        'db': 'mysql://webuser:V3fb^23J609G4$1@144.76.27.6/gcmtsrv_real?charset=utf8',
        'sock': ('88.198.194.84', 443),
        'test_integrity': False,
        'custom': ("88.198.194.84", 3001),  # основной мт4
        'custom2': ("88.198.194.84", 3002),  # зеркало мт4
        'custom3': ("88.198.194.84", 12345),  # mt4 trades info to websocket server
        'webtrading': ('88.198.194.84', 5444),
    },
    'db_archive': {
        'db': 'mysql://webuser:V3fb^23J609G4$1@144.76.27.6/gcmtsrv_arch?charset=utf8',
        'test_integrity': False,
    },
    'demo': {
        'db': 'mysql://webuser:V3fb^23J609G4$1@144.76.27.6/gcmtsrv_demo?charset=utf8',
        'sock': ('46.101.174.193', 7543),
        'test_integrity': False,
        'webtrading': ('88.198.194.84', 5444),
        'custom': ('46.101.174.193', 7101),
        'custom3': ("88.198.194.84", 12345),  # mt4 trades info to websocket server
    },
    'gtmarkets': {
        'sock': ('144.76.71.42', 2443),
        'custom2': ('144.76.71.42', 3002),
        'custom3': ('144.76.71.42', 12345),
        'webtrading': ('144.76.71.42', 5443),
    },
    'specifications': {
        'db': 'mysql://webuser:V3fb^23J609G4$1@144.76.27.6/specifications?charset=utf8',
        'sock': ('88.198.194.84', 443),
        'test_integrity': False,
    },
    'config': {
        'db': 'mysql://webuser:V3fb^23J609G4$1@144.76.27.6/config?charset=utf8',
        'sock': ('88.198.194.84', 443),
        'test_integrity': False,
    },
}

#--- CKEditor configuration (used in Node.Page)

CKEDITOR_UPLOAD_PATH = "ckeditor/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = "/static/js/vendor/jquery.js"

CKEDITOR_DEFAULT_TOOLBAR = [
    {"name": 'document', "groups": ['mode', 'document', 'doctools'], "items": ['Source']},
    {"name": 'styles', "items": ['Format']},
    {"name": 'clipboard', "groups": ['clipboard', 'undo'], "items": ['PasteFromWord', '-', 'Undo', 'Redo']},
    {"name": 'editing', "groups": ['find', 'selection', 'spellchecker'], "items": ['Scayt']},
    {"name": 'basicstyles', "groups": ['basicstyles', 'cleanup'],
     "items": ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
    {"name": 'paragraph', "groups": ['list', 'indent', 'blocks', 'align', 'bidi'],
     "items": ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-', 'JustifyLeft',
               'JustifyCenter', 'JustifyRight', '-', 'Language']},
    {"name": 'links', "items": ['Link', 'Unlink']},
    {"name": 'insert', "items": ['Image']},
    {"name": 'tools', "items": ['Maximize']},
]

CKEDITOR_CONFIGS = {
    'default': {
        'height': "450px",
        'width': "auto",
        'contentsCss': "/static/css/new_style.min.css",
        'toolbar': CKEDITOR_DEFAULT_TOOLBAR,
        'allowedContent': True,
        'entities': False,
        'basicEntities': False,
    },
}
CKEDITOR_CONFIGS['massmail'] = CKEDITOR_CONFIGS['default']


# Django 1.3 logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },

    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_FILENAME,
            'formatter': 'verbose',
        }
    },

    'root': {
        'level': 'DEBUG',
        'formatter': 'verbose',
        'handlers': ['file']
    },

    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django': {
            'handlers': ['null'],
            'level': 'ERROR',
            'propagate': True,
        },
        'mt4.api.DatabaseAPI.integrity': {
            'handlers': ['mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        'amqplib': {
            'level': 'ERROR',
            'handlers': ['file']
        }
    }
}

SILENCED_SYSTEM_CHECKS = ["1_6.W001", "1_6.W002", "fields.W342", "fields.W900", "fields.W122", "fields.W340"]

# I am not sure if we still need it, cause original django tests also work now
# This test runner loads the db from file instead of making it from django
#TEST_RUNNER = 'gcapital.testrunner.GCapitalTestSuiteRunner'

for path in os.path.join(MEDIA_ROOT, UPLOAD_PATH), LOG_DIR, CKEDITOR_UPLOAD_PATH:
    if not os.path.exists(path):
        os.makedirs(path)

if not os.path.exists(WKHTML_PATH):
    warnings.warn('wkhtml executable %s not found' % WKHTML_PATH)

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, filename=LOG_FILENAME)

TEMPLATE_DIRS = (
)
import djcelery
djcelery.setup_loader()

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_CACHE_BACKEND = "default"
CELERY_DISABLE_RATE_LIMITS = True
CELERY_RESULT_BACKEND = 'cache'
CELERYD_STATE_DB = os.path.join(PROJECT_ROOT, 'celery_state.db')

CELERY_QUEUES = {
    "celery": {
        "exchange": "celeryjb",
        "binding_key": "celeryjb"},
    "reports": {
        "exchange": "reports",
        "binding_key": "reports",
    },
}


CELERY_DEFAULT_QUEUE = "celery"
CELERY_DEFAULT_EXCHANGE = "celeryjb"
CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_DEFAULT_ROUTING_KEY = "celeryjb"


BROKER_URL = "amqp://guest:guest@127.0.0.1:5672/"

# django-coffeescript settings
COFFEESCRIPT_EXECUTABLE = "coffee"
COFFEESCRIPT_USE_CACHE = True
COFFEESCRIPT_CACHE_TIMEOUT = 60 * 60 * 24 * 30  # 30 days
COFFEESCRIPT_MTIME_DELAY = 10  # 10 seconds
COFFEESCRIPT_OUTPUT_DIR = "coffee/js/"  # relative to static/media root


# Domains for cross domain auth without scheme
# Example: XDOMAINS = ('example.ru', 'example.com', 'example.net')
XDOMAINS = ()


# Private offices settings
# Example:
# PRIVATE_OFFICES = {
#     "test-private-office": {
#         'css': "css/test.css",
#         'available_accounts': {
#             'real': ['standard', 'options', 'micro', 'ecn', 'contest', 'partnership'],
#             'demo': ['standard', 'options'],
#             'partnership': ['partnership']
#         },
#         'available_modules': ['trading', 'investment', 'master', 'contest', 'partnership']
#     }
# }
PRIVATE_OFFICES = {
}

# Strategy Store settings
SS_API_HOST = "https://148.251.86.217:81/"
SS_API_LOGIN = "api"
SS_API_TOKEN = "eFBxR84qJK9nBAWj"

# CFH settings
# Auth settings
DEMO_CFH_API_BROKER = "https://demows.cfhclearing.com:8090/BrokerDataAccess?wsdl"
DEMO_CFH_API_CLIENTADMIN = "https://demows.cfhclearing.com:8083/DemoClientAdmin?wsdl"
DEMO_CFH_API_LOGIN = "ArumProAdminDemo"
DEMO_CFH_API_PASSWORD = "ArumProAdmin2017"
CFH_API_BROKER = "https://ws.cfhclearing.com:8091/BrokerDataAccess?wsdl"
CFH_API_CLIENTADMIN = "https://ws.cfhclearing.com:8084/LiveClientAdmin?wsdl"
CFH_API_LOGIN = "ArumProAdmin"
CFH_API_PASSWORD = "ArumProAdmin2017"

# New account creation settings
CFH_BROKER_ID = 11244
DEMO_CFH_BROKER_ID = 173056
# Accounts for money transfers
CFH_DEPOSIT_ACCOUNT_ID = 25000
CFH_WITHDRAW_ACCOUNT_ID = 25000
DEMO_CFH_DEPOSIT_ACCOUNT_ID = 153641
DEMO_CFH_WITHDRAW_ACCOUNT_ID = 153641
# Margin requirements objects, dict in form leverage:obj_id
CFH_CLIENT_TEMPLATES = {
    '100': 115,
    '75': 117,
    '50': 116,
    '33': 120,
    '25': 121,
    '20': 122,
    '10': 123,
    '5': 124,
    '1': 126,
}
DEMO_CFH_CLIENT_TEMPLATES = {
    '100': 1188,
    '50': 1189,
    '33': 1190,
    '75': 1191,
    '25': 1192,
    '20': 1193,
    '10': 1194,
    '5': 1195,
    '1': 1196,
}

# CRM settings
PARTNER_SUPPORT_EMAIL = defaultdict(
    lambda: 'partner.global@grandcapital.net',  # alias for a.abizyaev@grandcapital.net
    {
       'ru': 'partner@grandcapital.net',
    },
)

###############################################################################
########## Load local settings for sure #######################################
###############################################################################
try:
    from local_settings import *
except ImportError:
    pass
