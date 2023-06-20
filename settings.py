import os
import urllib
from uuid import uuid4


def set_env_variables():
    os.environ["basedir"] = os.path.abspath(os.path.dirname(__file__))
    os.environ["UPLOAD_FOLDER"] = os.path.dirname(os.path.abspath(__file__)) + '\\uploads\\'
    os.environ["DIR_PATH"] = os.path.dirname(os.path.realpath(__file__))
    os.environ["params"] = urllib.parse.quote_plus('Driver={driver};'
                                                   'Server={server};'
                                                   'Database={database};'
                                                   'Trusted_Connection={trusted_connection};'.format(
        driver=os.environ.get("Driver"), server=os.environ.get("Server"), database=os.environ.get("Database"),
        trusted_connection=os.environ.get("Trusted_Connection")
    ))

    os.environ["STATIC_ROOT"] = os.path.dirname(os.environ["basedir"]) + os.environ.get("STATIC_URL")

    os.environ["SECRET_KEY"] = str(uuid4())

    os.environ["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc:///?odbc_connect=%s" % os.environ.get("params")

    os.environ["MAX_CONTENT_LENGTH"] = str(8 * 1024 * 1024)
