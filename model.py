from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from sqlalchemy.ext.hybrid import (hybrid_method, hybrid_property)

db = SQLAlchemy()


class Users(UserMixin, db.Model):
    """
    Model class for user table AMEA_USERS
    """
    __tablename__ = 'AMEA_USERS'
    ID = db.Column(db.Integer, primary_key=True)
    F_NAME = db.Column(db.String(100), nullable=False)
    L_NAME = db.Column(db.String(100), nullable=False)
    EMAIL = db.Column(db.String(400), unique=True, nullable=False)
    PLANT_NAME = db.Column(db.String(100), nullable=False)
    NETWORK_ID = db.Column(db.String(100), unique=True, nullable=False)
    PASSWORD = db.Column(db.String(500))
    ADMIN_ACCESS = db.Column(db.String(10))
    GLOBAL_DATA_ACCESS = db.Column(db.String(10))
    REGULAR_ACCESS = db.Column(db.String(10))

    def __init__(self, ID, F_NAME, L_NAME, EMAIL, PLANT_NAME, NETWORK_ID, PASSWORD, ADMIN_ACCESS,
                 GLOBAL_DATA_ACCESS, REGULAR_ACCESS):
        """
        Constructor
        """
        self.ID = ID
        self.F_NAME = F_NAME
        self.L_NAME = L_NAME
        self.EMAIL = EMAIL
        self.PLANT_NAME = PLANT_NAME
        self.NETWORK_ID = NETWORK_ID
        self.PASSWORD = PASSWORD
        self.ADMIN_ACCESS = ADMIN_ACCESS
        self.GLOBAL_DATA_ACCESS = GLOBAL_DATA_ACCESS
        self.REGULAR_ACCESS = REGULAR_ACCESS

    @hybrid_property
    def password(self):
        """
        Getter method for password
        :return: string
        """
        return self._PASSWORD

    @password.setter
    def set_password(self, plaintext_password):
        """
        Setter method for password
        :param plaintext_password:
        :return: none
        """
        self._password = sha256_crypt.encrypt(plaintext_password)

    @hybrid_method
    def is_correct_password(self, plaintext_password):
        """
        Function to verify if password is correct after encryption
        :param plaintext_password: password input
        :return: status of verification - bool
        """
        return sha256_crypt.verify(self.password, plaintext_password)

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False

    def get_network_id(self):
        """
        Getter method for user ID
        :return: user ID
        """
        return str(self.NETWORK_ID)

    def get_id(self):
        """
        Getter method for ID
        :return: Id
        """
        return str(self.ID)

    def get_first_name(self):
        """
        Getter method for first name
        :return: First name
        """
        return str(self.F_NAME)

    def __repr__(self):
        """
        String function
        :return: str
        """
        return "%s/%s/%s" % (self.F_NAME, self.NETWORK_ID, self.PASSWORD)


class Tokens(db.Model):
    """
    Model class for user token table AMEA_TOKENS
    """
    __tablename__ = 'AMEA_PASSWORD_RESET_TOKEN'
    ID = db.Column(db.Integer, primary_key=True)
    EMAIL = db.Column(db.String(400), unique=True, nullable=False)
    NETWORK_ID = db.Column(db.String(100), unique=True, nullable=False)
    TOKEN = db.Column(db.String(500))

    def __init__(self, ID, EMAIL, NETWORK_ID, TOKEN):
        """
        Constructor
        """
        self.ID = ID
        self.EMAIL = EMAIL
        self.NETWORK_ID = NETWORK_ID
        self.TOKEN = TOKEN

class TableKPIInsertValues(db.Model):
    """
    Model class for KPI insert table AMEA_MANUAL_WEB_VALUES_TEMP
    """
    __tablename__ = 'AMEA_MANUAL_WEB_VALUES_TEMP'
    ID = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    PERIOD = db.Column(db.String(20))
    CATEGORY = db.Column(db.String(50))
    PLANT = db.Column(db.String(20))
    KPI_NAME = db.Column(db.String(50))
    KPI_VALUES = db.Column(db.String(50))
    CURR_TIME = db.Column(db.DateTime)
    YEAR = db.Column(db.Integer)
    YTD_or_MTD = db.Column(db.String(40))
    DATA_TYPE = db.Column(db.String(10))
    SUB_CATEGORY = db.Column(db.String(50))
    FUNCTION_NAME = db.Column(db.String(100))
    NETWORK_ID = db.Column(db.String(50))

    def __init__(self, ID, PERIOD, CATEGORY, PLANT, KPI_NAME, KPI_VALUES, CURR_TIME, YEAR,
                 YTD_or_MTD, DATA_TYPE,
                 SUB_CATEGORY, FUNCTION_NAME, NETWORK_ID):
        """
        Constructor
        """
        self.ID = ID
        self.PERIOD = PERIOD
        self.CATEGORY = CATEGORY
        self.PLANT = PLANT
        self.KPI_NAME = KPI_NAME
        self.KPI_VALUES = KPI_VALUES
        self.CURR_TIME = CURR_TIME
        self.YEAR = YEAR
        self.YTD_or_MTD = YTD_or_MTD
        self.DATA_TYPE = DATA_TYPE
        self.SUB_CATEGORY = SUB_CATEGORY
        self.FUNCTION_NAME = FUNCTION_NAME
        self.NETWORK_ID = NETWORK_ID


class TableKPIData(db.Model):
    """
    Class model for AMEA_MANUAL_WEB_DIM
    """
    __tablename__ = 'AMEA_MANUAL_WEB_DIM'
    ID = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    PERIOD = db.Column(db.String(20))
    CATEGORY = db.Column(db.String(50))
    PLANT = db.Column(db.String(20))
    KPI_NAME = db.Column(db.String(50))

    def __init__(self, ID, PERIOD, CATEGORY, PLANT, KPI_NAME):
        """
        Constructor
        """
        self.ID = ID
        self.PERIOD = PERIOD
        self.CATEGORY = CATEGORY
        self.PLANT = PLANT
        self.KPI_NAME = KPI_NAME


class TableKPIInsertValuesOriginal(db.Model):
    """
    Class model for AMEA_MANUAL_WEB_VALUES
    """
    __tablename__ = 'AMEA_MANUAL_WEB_VALUES'
    ID = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    PERIOD = db.Column(db.String(20))
    CATEGORY = db.Column(db.String(50))
    PLANT = db.Column(db.String(20))
    KPI_NAME = db.Column(db.String(50))
    KPI_VALUES = db.Column(db.String(50))
    CURR_TIME = db.Column(db.DateTime)
    YEAR = db.Column(db.Integer)
    YTD_or_MTD = db.Column(db.String(10))
    DATA_TYPE = db.Column(db.String(40))
    SUB_CATEGORY = db.Column(db.String(50))
    FUNCTION_NAME = db.Column(db.String(100))
    NETWORK_ID = db.Column(db.String(50))

    def __init__(self, ID, PERIOD, CATEGORY, PLANT, KPI_NAME, KPI_VALUES, CURR_TIME, YEAR,
                 YTD_or_MTD, DATA_TYPE,
                 SUB_CATEGORY, FUNCTION_NAME, NETWORK_ID):
        """
        Constructor
        """
        self.ID = ID
        self.PERIOD = PERIOD
        self.CATEGORY = CATEGORY
        self.PLANT = PLANT
        self.KPI_NAME = KPI_NAME
        self.KPI_VALUES = KPI_VALUES
        self.CURR_TIME = CURR_TIME
        self.YEAR = YEAR
        self.YTD_or_MTD = YTD_or_MTD
        self.DATA_TYPE = DATA_TYPE
        self.SUB_CATEGORY = SUB_CATEGORY
        self.FUNCTION_NAME = FUNCTION_NAME
        self.NETWORK_ID = NETWORK_ID


class TableAMEAKPIDetailDim(db.Model):
    """
    Class model for AMEA_KPI_DETAIL_DIM
    """
    __tablename__ = 'AMEA_KPI_DETAIL_DIM'
    ID = db.Column(db.Integer, primary_key=True)
    PLANT_NAME = db.Column(db.String(50))
    CATEGORY = db.Column(db.String(50))
    SUB_CATEGORY = db.Column(db.String(50))
    FUNCTION_NAME = db.Column(db.String(100))
    KPI_NAME = db.Column(db.String(400))
    TYPE = db.Column(db.String(50))
    DATA_TYPE = db.Column(db.String(10))

    def __init__(self, ID, PLANT_NAME, CATEGORY, SUB_CATEGORY, FUNCTION_NAME, KPI_NAME, TYPE,
                 DATA_TYPE):
        """
        Constructor
        """
        self.ID = ID
        self.PLANT_NAME = PLANT_NAME
        self.CATEGORY = CATEGORY
        self.SUB_CATEGORY = SUB_CATEGORY
        self.FUNCTION_NAME = FUNCTION_NAME
        self.KPI_NAME = KPI_NAME
        self.TYPE = TYPE
        self.DATA_TYPE = DATA_TYPE


class TableAMEARegionalWebValuesTemp(db.Model):
    """
    Class model for AMEA_REGIONAL_WEB_VALUES_TEMP
    """
    __tablename__ = 'AMEA_REGIONAL_WEB_VALUES_TEMP'
    ID = db.Column(db.Integer, primary_key=True)
    REGION_NAME = db.Column(db.String(50))
    FUNCTION_NAME = db.Column(db.String(100))
    KPI_NAME = db.Column(db.String(255))
    KPI_VALUES = db.Column(db.String(50))
    YTD_or_MTD = db.Column(db.String(10))
    YEAR = db.Column(db.Integer)
    PERIOD = db.Column(db.String(50))
    DATA_TYPE = db.Column(db.String(50))
    CURR_TIME = db.Column(db.DateTime)
    NETWORK_ID = db.Column(db.String(50))

    def __init__(self, ID, REGION_NAME, FUNCTION_NAME, KPI_NAME, KPI_VALUES, YTD_or_MTD, YEAR,
                 PERIOD, DATA_TYPE,
                 CURR_TIME, NETWORK_ID):
        """ Constructor """
        self.ID = ID
        self.REGION_NAME = REGION_NAME
        self.FUNCTION_NAME = FUNCTION_NAME
        self.KPI_NAME = KPI_NAME
        self.KPI_VALUES = KPI_VALUES
        self.YTD_or_MTD = YTD_or_MTD
        self.YEAR = YEAR
        self.PERIOD = PERIOD
        self.DATA_TYPE = DATA_TYPE
        self.CURR_TIME = CURR_TIME
        self.NETWORK_ID = NETWORK_ID


class TableAMEAGlobalValuesWebDim(db.Model):
    """
    Class model for AMEA_GLOBAL_VALUES_WEB_DIM
    """
    __tablename__ = 'AMEA_GLOBAL_VALUES_WEB_DIM'
    ID = db.Column(db.Integer, primary_key=True)
    REGION_NAME = db.Column(db.String(50))
    FUNCTION_NAME = db.Column(db.String(50))
    KPI_NAME = db.Column(db.String(400))
    TYPE = db.Column(db.String(20))
    DATA_TYPE = db.Column(db.String(10))

    def __init__(self, ID, REGION_NAME, FUNCTION_NAME, KPI_NAME, TYPE, DATA_TYPE):
        """ Constructor """
        self.ID = ID
        self.REGION_NAME = REGION_NAME
        self.FUNCTION_NAME = FUNCTION_NAME
        self.KPI_NAME = KPI_NAME
        self.TYPE = TYPE
        self.DATA_TYPE = DATA_TYPE


class TableFiscCalDy(db.Model):
    """
    Class model for AMEA_FISC_CAL_DY
    """
    __tablename__ = 'AMEA_FISC_CAL_DY'
    FISC_DT = db.Column(db.String(50), primary_key=True)
    FISC_YR = db.Column(db.String(50))
    FISC_QTR = db.Column(db.String(50))
    FISC_PD = db.Column(db.String(50))
    FISC_WK = db.Column(db.String(50))
    FISC_DY = db.Column(db.String(50))
    FISC_WK_OF_PD = db.Column(db.String(50))
    FISC_DY_OF_PD = db.Column(db.String(50))
    FISC_DY_OF_WK = db.Column(db.String(50))
    FISC_WK_STRT_DT = db.Column(db.String(50))
    FISC_WK_END_DT = db.Column(db.String(50))
    FISC_YR_QTR = db.Column(db.String(50))
    FISC_YR_PD = db.Column(db.String(50))
    FISC_YR_WK = db.Column(db.String(50))
    FISC_YR_DY = db.Column(db.String(50))

    def __init__(self, FISC_DT, FISC_YR, FISC_QTR, FISC_PD, FISC_WK, FISC_DY, FISC_WK_OF_PD,
                 FISC_DY_OF_PD,
                 FISC_DY_OF_WK, FISC_WK_STRT_DT, FISC_WK_END_DT, FISC_YR_QTR, FISC_YR_PD,
                 FISC_YR_WK, FISC_YR_DY):
        """ Constructor """
        self.FISC_DT = FISC_DT
        self.FISC_YR = FISC_YR
        self.FISC_QTR = FISC_QTR
        self.FISC_PD = FISC_PD
        self.FISC_WK = FISC_WK
        self.FISC_DY = FISC_DY
        self.FISC_WK_OF_PD = FISC_WK_OF_PD
        self.FISC_DY_OF_PD = FISC_DY_OF_PD
        self.FISC_DY_OF_WK = FISC_DY_OF_WK
        self.FISC_WK_STRT_DT = FISC_WK_STRT_DT
        self.FISC_WK_END_DT = FISC_WK_END_DT
        self.FISC_YR_QTR = FISC_YR_QTR
        self.FISC_YR_PD = FISC_YR_PD
        self.FISC_YR_WK = FISC_YR_WK
        self.FISC_YR_DY = FISC_YR_DY
