"""
Script to configure the application and fetch user details
Date Modified: 5th June 2020
"""

import pathlib
import os
import env_file
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf import CSRFProtect


import settings
from model import db


# Set environment variables in app config
def set_app_config(application):
    """
    Set environment vsriables as application configuration
    :param application: app object
    :return: None
    """
    env_file.load(f'{os.path.join(pathlib.Path(__file__).parent.absolute(), "config.env")}')
    settings.set_env_variables()
    env_vars = dict(os.environ)

    for var in env_vars:
        application.config[var] = os.environ.get(var)

    application.config["MAX_CONTENT_LENGTH"] = int(os.environ["MAX_CONTENT_LENGTH"])
    application.config["WTF_CSRF_ENABLED"] = True if os.environ.get("WTF_CSRF_ENABLED") == "True" else False
    application.config["BOOTSTRAP_SERVE_LOCAL"] = True if os.environ.get("BOOTSTRAP_SERVE_LOCAL") == "True" else False
    application.config["SESSION_PERMANENT"] = True if os.environ.get("SESSION_PERMANENT") == "True" else False
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True if os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS") == "True" else False
    application.config["DEBUG"] = True if os.environ.get("DEBUG") == "True" else False
    application.config["INFO"] = True if os.environ.get("INFO") == "True" else False
    application.config["TOASTR_TIMEOUT"] = int(os.environ["TOASTR_TIMEOUT"])


# Setup application
LOG_FOLDER = 'logs'
GLOBAL_FILE_NAME = 'global.log'
LOCAL_FILE_NAME = 'local.log'
application = Flask(__name__, template_folder='templates', static_folder='static')


application.jinja_env.trim_blocks = True
application.jinja_env.lstrip_blocks = True

# Set config variables
set_app_config(application)

# flask-csrf
csrf = CSRFProtect(application)
csrf.exempt("render_main_page")
# csrf.init_app(app)

# flask-login
loginmanager = LoginManager()
loginmanager.login_view = "render_main_page"
loginmanager.login_message = 'You need to login first.'
loginmanager.refresh_view = 'render_main_page'
loginmanager.needs_refresh_message = 'You need to login again!'
loginmanager.init_app(application)

# flask-bootstrap
Bootstrap(application)
db.init_app(application)

# import routing functions
from controller import *

# new code
from flask_toastr import Toastr

toastr = Toastr()
toastr.init_app(application)


# since the user_id is just the primary key of our user table, use it in the query for the user
@loginmanager.user_loader
def load_user(user_id):
    """
    Return the user details for a particular user_id value
    :param user_id: User ID of an user
    :return: User details - list
    """
    try:
        application.logger.info("User ID : " + str(Users.query.get(int(user_id))))
        return Users.query.get(int(user_id))
    except:
        return None


if __name__ == '__main__':
    application.run(debug=True, threaded=True, host='0.0.0.0', port=8000)
