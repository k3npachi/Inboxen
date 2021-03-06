##
#    Copyright (C) 2015 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen  If not, see <http://www.gnu.org/licenses/>.
##

import os
import warnings

from django.core import exceptions

import configobj
import validate

##
# Most configuration can be done via settings.ini
#
# The file is searched for in the follow way:
# 1. The environment variable "INBOXEN_CONFIG", which contains an absolute path
# 2. ~/.config/inboxen/settings.ini
# 3. settings.ini in the root of the git repo (i.e. the same directory as "manage.py")
#
# See inboxen/config_spec.ini for defaults, see below for comments
##

# Shorthand for Django's default database backends
db_dict = {
    "postgresql": "django.db.backends.postgresql_psycopg2",
    "mysql": "django.db.backends.mysql",
    "oracle": "django.db.backends.oracle",
    "sqlite": "django.db.backends.sqlite3",
}

# Shorthand for Django's default database backends
cache_dict = {
    "database": "django.core.cache.backends.db.DatabaseCache",
    "dummy": "django.core.cache.backends.dummy.DummyCache",
    "file": "django.core.cache.backends.filebased.FileBasedCache",
    "localmem": "django.core.cache.backends.locmem.LocMemCache",
    "memcached": "django.core.cache.backends.memcached.PyLibMCCache",
}

is_testing = int(os.getenv('INBOXEN_TESTING', '0')) > 0

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if is_testing:
    CONFIG_PATH = ""
elif os.path.exists(os.getenv('INBOX_CONFIG', '')):
    CONFIG_PATH = os.getenv('INBOX_CONFIG')
elif os.path.exists(os.path.expanduser("~/.config/inboxen/settings.ini")):
    CONFIG_PATH = os.path.expanduser("~/.config/inboxen/settings.ini")
elif os.path.exists(os.path.join(BASE_DIR, "settings.ini")):
    CONFIG_PATH = os.path.join(BASE_DIR, "settings.ini")
else:
    raise exceptions.ImproperlyConfigured("You must provide a settings.ini file")

config_spec = os.path.join(BASE_DIR, "inboxen/config_spec.ini")

config = configobj.ConfigObj(CONFIG_PATH, configspec=config_spec)
config.validate(validate.Validator())

# TODO: These could be merged into a custom validator
try:
    SECRET_KEY = config["general"]["secret_key"]
except KeyError:
    if is_testing:
        warnings.warn("You haven't set 'secret_key' in your settings.ini", ImportWarning)
    else:
        raise exceptions.ImproperlyConfigured("You must set 'secret_key' in your settings.ini")

if len(config["general"]["admin_names"]) != len(config["general"]["admin_emails"]):
    raise exceptions.ImproperlyConfigured("You must have the same number of admin_names as admin_emails settings.ini")

# Admins (and managers)
ADMINS = zip(config["general"]["admin_names"], config["general"]["admin_emails"])

# List of hosts allowed
ALLOWED_HOSTS = config["general"]["allowed_hosts"]

# Enable debugging - DO NOT USE IN PRODUCTION
DEBUG = config["general"]["debug"]

# Allow new users to register
ENABLE_REGISTRATION = config["general"]["enable_registration"]

# Allow admins to edit users
ENABLE_USER_EDITING = config["general"]["enable_user_editing"]

# Cooloff time, in minutes, for failed logins
LOGIN_ATTEMPT_COOLOFF = config["general"]["login_attempt_cooloff"]

# Maximum number of unsuccessful login attempts
LOGIN_ATTEMPT_LIMIT = config["general"]["login_attempt_limit"]

# Language code, e.g. en-gb
LANGUAGE_CODE = config["general"]["language_code"]

# Where `manage.py collectstatic` puts static files
STATIC_ROOT = os.path.join(BASE_DIR, config["general"]["static_root"])

# Media files get uploaded to this dir
MEDIA_ROOT = os.path.join(BASE_DIR, config["general"]["media_root"])

# Email the server uses when sending emails
SERVER_EMAIL = config["general"]["server_email"]

# Site name used in page titles
SITE_NAME = config["general"]["site_name"]

# Link to source code
SOURCE_LINK = config["general"]["source_link"]

# Time zone
TIME_ZONE = config["general"]["time_zone"]

# Length of the local part (bit before the @) of autogenerated inbox addresses
INBOX_LENGTH = config["inbox"]["inbox_length"]

# Maximum number of free inboxes before a request for more will be generated
MIN_INBOX_FOR_REQUEST = config["inbox"]["min_inbox_for_request"]

# Increase the pool amount by this number when a user request is granted
REQUEST_NUMBER = config["inbox"]["request_number"]

# Where Celery looks for new tasks and stores results
BROKER_URL = config["tasks"]["broker_url"]

# Number of Celery processes to start
CELERYD_CONCURRENCY = config["tasks"]["concurrency"]

# Runs tasks synchronously
CELERY_ALWAYS_EAGER = config["tasks"]["always_eager"]

# Path where liberation data is stored
LIBERATION_PATH = os.path.join(BASE_DIR, config["tasks"]["liberation"]["path"])
LIBERATION_PATH = LIBERATION_PATH.rstrip("/")

# Which method should be used to accelerate liberation data downloads
SENDFILE_BACKEND = "sendfile.backends.{}".format(config["tasks"]["liberation"]["sendfile_method"])

# Databases!
DATABASES = {
    'default': {
        'ENGINE': db_dict[config["database"]["engine"]],
        'USER': config["database"]["user"],
        'PASSWORD': config["database"]["password"],
        'HOST': config["database"]["host"],
        'PORT': config["database"]["port"],
    }
}

# "name" is a path for sqlite databases
if config["database"]["engine"] == "sqlite":
    DATABASES["default"]["NAME"] = os.path.join(BASE_DIR, config["database"]["name"])
else:
    DATABASES["default"]["NAME"] = config["database"]["name"]

# Caches!
CACHES = {
    'default': {
        'BACKEND': cache_dict[config["cache"]["backend"]],
        'TIMEOUT': config["cache"]["timeout"],
    }
}

if config["cache"]["backend"] == "file":
    if config["cache"]["location"] == "":
        # sane default for minimum configuration
        CACHES["default"]["LOCATION"] = os.path.join(BASE_DIR, "inboxen_cache")
    else:
        CACHES["default"]["LOCATION"] = os.path.join(BASE_DIR, config["cache"]["location"])
else:
    CACHES["default"]["LOCATION"] = config["cache"]["location"]

# populate __all__
__all__ = [item for item in dir() if item.isupper()]
