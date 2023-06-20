"""
Scripts that contains the utility functions that sends email, decrypts values and check extensions
"""

import datetime
import re
import smtplib
import socket
import time
from base64 import b64decode, b64encode
from datetime import date
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from Crypto.Cipher import AES
from flask import render_template, url_for
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import text
from sqlalchemy.sql.expression import func

from app import application
from decryption import Decryption
from model import (db, TableAMEARegionalWebValuesTemp, TableFiscCalDy, Tokens)

PASS_PHRASE = r"Gigantic '\Gloomily '\Greeter '\Family '\Cotton '\Dyslexic '\Specks " \
              r"'\Derived '\Everglade '\Bagging '\Spongy '\Shortwave"

ALLOWED_EXTENSIONS = {'xlsx'}


def allowed_file(filename):
    """
    Function that returns the allowed extensions
    :param filename: filename to be checked
    :return: Boolean
    """
    try:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    except IndexError as index_error:
        application.logger.error(str(index_error))
    except Exception as exp_msg:
        application.logger.error(str(exp_msg))


def get_decrypted_value(encrypted_key):
    """
    Function to get the decrypted value of the input
    :param encrypted_key: Input to be decrypted
    :return: Decrypted value - str
    """
    try:
        decrypted_value = Decryption().decrypt(encrypted_key).decode('utf-8')
        return decrypted_value
    except Exception as exp_msg:
        application.logger.error(str(exp_msg))


def send_password_reset_email(user_email):
    """
    Function to send password reset email
    :param user_email: Reciever of the email
    :return: None
    """
    server_host, server_port = 'smtpe2k.us.kellogg.com', 25
    try:
        password_reset_serializer = URLSafeTimedSerializer('SECRET_KEY')
        password_reset_url = url_for('reset_password',
                                     token=password_reset_serializer.dumps(user_email,
                                                                           salt='password-reset-salt'),
                                     _external=True)
        token = password_reset_url.split("/")[-1]

        html = render_template('email_password_reset.html', password_reset_url=password_reset_url)
        sender = "noreply@kellogg.com"
        receiver = str(user_email)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Password reset for Web Application"
        msg['From'] = sender
        msg['To'] = receiver
        text = "Hi!\nHow are you?\nHere is the link you wanted:\n" + html
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        smtp_connection = smtplib.SMTP(server_host, server_port)
        smtp_connection.sendmail(sender, receiver, msg.as_string())
        return token
    except socket.error as error:
        application.logger.error("Could not connect to " + str(server_host) + ":" + str(
            server_port) + "-" + str(error))
    except Exception as exp_msg:
        application.logger.error("Unknown error:", str(exp_msg))
    finally:
        if smtp_connection != None:
            smtp_connection.quit()


def send_mail(message, receipient, subject):
    """
    Function to send an email
    :param message: Message to be sent
    :param receipient: Reciever of the email
    :param subject: Subject of the Email
    :return: None
    """
    server_host = 'smtpe2k.us.kellogg.com'
    server_port = 25
    try:
        sender = "noreply@kellogg.com"
        receiver = receipient
        msg = EmailMessage()
        msg["From"] = sender
        msg["Subject"] = subject
        msg["To"] = receiver
        msg.set_content(message)
        msg.add_attachment(open('logs/application.log', "r").read(), filename="application.log")
        smtp_connection = smtplib.SMTP(server_host, server_port)
        smtp_connection.sendmail(sender, receiver, msg.as_string())
    except socket.error as e:
        application.logger.error("Could not connect to " + str(server_host) + ":" + str(
            server_port))
    except Exception as exp_msg:
        application.logger.error("Unknown error:", str(exp_msg))
    finally:
        if smtp_connection != None:
            smtp_connection.quit()


def insert_token(email, network_id, token):
    """
    Funtion to insert or update the token table
    :param email: Email
    :param network_id: User ID
    :param token: Token for password reset
    :return:
    """
    try:
        token_data = Tokens.query.filter_by(NETWORK_ID=network_id, EMAIL=email).first()
        if token_data:
            token_data.TOKEN = token
        else:
            max_id = db.session.query(func.max(Tokens.ID)).scalar()
            max_id = 1 if not max_id else int(max_id) + 1

            token_obj = Tokens(ID=max_id, NETWORK_ID=network_id, EMAIL=email, TOKEN=token)
            db.session.add(token_obj)

        application.logger.info("Password reset token added to Tokens table")
        db.session.commit()

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))


def insert_file_process(df_input, tab_name):
    """
    Function to insert the excel file records into SQL tables
    :param df: Data frame containing the data to inserted
    :param tab_name: Table to be inserted
    :return: Result of the insertion
    """

    try:
        if tab_name == 'Regional' and 'str' not in str(type(df_input)):

            df_file = df_input.fillna('NULL')

            df_not_null = df_file[df_file['KPI_VALUES'] != 'NULL'].copy()

            df_not_null = df_not_null.to_dict(orient='records')
            db.engine.execute(TableAMEARegionalWebValuesTemp.__table__.insert(), df_not_null)
            db.session.flush()
            db.session.commit()
            str_msg = "Global values are loaded successfully"
            result = 'success'
        elif tab_name == 'Scorecard' and 'str' not in str(type(df_input)):

            df_file = df_input.fillna('null')
            df_file['MONTH_NO'] = df_file['MONTH_NO'].apply(pd.to_numeric)

            df_not_null = df_file[df_file['ACTUAL'] != 'nan'].copy()
            temp1 = time.time()
            df_not_null = df_not_null.fillna('null')
            df_not_null = df_not_null.replace(['nan'], ['null'])

            query = """"""
            iter = 0
            UPLOAD_DATE = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(df_not_null[df_not_null['DATE'] == 'P10'])
            print(len(df_not_null))
            for i, ROW in df_not_null.iterrows():
                # print(ROW)
                UOM = ROW.UOM.replace("'", "''")
                iter += 1
                conditions = f"""WHERE METRIC = '{ROW.METRIC}'
                                                           AND SUB_METRIC = '{ROW.SUB_METRIC}'
                                                           AND SUB_KPI = '{ROW.SUB_KPI}'
                                                           AND TYPE_ACTUAL_PLANNED = '{ROW.TYPE_ACTUAL_PLANNED}'
                                                           AND UOM = '{UOM}'
                                                           AND DATE = '{ROW.DATE}'
                                                           AND SOURCE_NAME = '{ROW.SOURCE_NAME}'
                                                           AND SOURCE_TYPE = '{ROW.SOURCE_TYPE}'
                                                           AND PLANT = '{ROW.PLANT}'
                                                           AND YEAR = '{ROW.YEAR}'
                                                           AND PERIOD = '{ROW.PERIOD}'
                                                           AND CATEGORY = '{ROW.CATEGORY}'
                                                           AND SUB_CATEGORY = '{ROW.SUB_CATEGORY}'
                                                           AND WEEK = '{ROW.WEEK}'"""
                query += f""" DELETE FROM [dbo].[AMEA_DAILY_FILE_UPLOAD_WEB_VALUES]
                                                                       {conditions};
                                                            INSERT INTO [dbo].[AMEA_DAILY_FILE_UPLOAD_WEB_VALUES] (METRIC,SUB_METRIC, 
                                                            SUB_KPI,TYPE_ACTUAL_PLANNED,UOM,DATE,ACTUAL,SOURCE_NAME,SOURCE_TYPE,PLANT,YEAR, 
                                                            PERIOD,MONTH_NO,MONTH_SF,MONTH_LF,CATEGORY,SUB_CATEGORY,WEEK,NETWORK_ID, UPLOAD_DATE
                                                            ) VALUES ('{ROW.METRIC}', '{ROW.SUB_METRIC}', 
                                                            '{ROW.SUB_KPI}', '{ROW.TYPE_ACTUAL_PLANNED}', 
                                                            '{UOM}', '{ROW.DATE}',
                                                           '{ROW.ACTUAL}', '{ROW.SOURCE_NAME}', 
                                                           '{ROW.SOURCE_TYPE}', '{ROW.PLANT}', 
                                                           '{ROW.YEAR}', '{ROW.PERIOD}', 
                                                           '{ROW.MONTH_NO}', '{ROW.MONTH_SF}', 
                                                           '{ROW.MONTH_LF}', '{ROW.CATEGORY}', 
                                                           '{ROW.SUB_CATEGORY}', '{ROW.WEEK}', 
                                                           '{ROW.NETWORK_ID}', '{UPLOAD_DATE}');\n"""
                if iter % 220 == 0:
                    # print(iter)
                    res = db.engine.execute(text(query).execution_options(autocommit=True))
                    query = """"""
            if query:
                res = db.engine.execute(text(query).execution_options(autocommit=True))
            str_msg = "Data has been loaded successfully"
            result = 'success'
        elif tab_name == 'Both':
            str_msg = df_input
            result = 'error'

        else:
            str_msg = df_input
            result = 'error'
        return str_msg, result
    except KeyError as key_error:
        application.logger.error(str(key_error))
    except Exception as exp_msg:
        application.logger.error(str(exp_msg))


def check_file_pattern(file_name):
    """
    Function to check the file name pattern
    :param file_name: Name of the file
    :return: Status of the file check
    """

    try:
        file_pattern = ""
        if "Actual" in file_name:
            file_pattern = re.search(r"^\(([A-Za-z]+)\) (\d+)-P(\d{2})-([A-Za-z0-9_ ]+) - ([A-Za-z ]+)-(Plant-KPI|Functional-KPI)(\..*$)",
                                     file_name)
        elif "Target" in file_name and 'Regional' not in file_name:
            file_pattern = re.search(r"^\(([A-Za-z]+)\) (\d+)-([A-Za-z0-9_ ]+) - ([A-Za-z ]+)(\..*$)", file_name)
        elif "Regional" in file_name:
            file_pattern1 = re.search(r"^(\d+)-P(\d{2})-([A-Za-z ]+)-(Monthly)(\..*$)", file_name)
            file_pattern2 = re.search(r"^(\d+)-([A-Za-z ]+)-(Annually)(\..*$)", file_name)
            file_pattern = file_pattern1 or file_pattern2

        if 'Annually' in file_name:
            today = date.today()
            cal_data = TableFiscCalDy.query.filter_by(FISC_DT=str(today)).first()
            year = int(file_pattern.group(1))
            if year > int(cal_data.FISC_YR):
                message, status = "File name with future year is invalid", "error"
            else:
                message, status = "{} is a valid file name".format(file_name), "success"

            return message, status

        if file_pattern:
            today = date.today()
            cal_data = TableFiscCalDy.query.filter_by(FISC_DT=str(today)).first()
            if "Target" not in file_name:

                year = int(file_pattern.group(2)) if "Actual" in file_name else int(file_pattern.group(1))
                period = int(file_pattern.group(3)) if "Actual" in file_name else int(file_pattern.group(2))

                if year > int(cal_data.FISC_YR):
                    message, status = "File name with future year is invalid", "error"
                else:

                    if year == int(cal_data.FISC_YR):
                        year_end = int(cal_data.FISC_PD)
                    else:
                        year_end = 12

                    period_flag = True if period in range(1, year_end + 1) else False

                    if not period_flag:
                        if period <= 12:
                            message, status = "File name with future period is invalid", "error"
                        else:
                            message, status = "Invalid period value in file name", "error"
                    else:
                        message, status = "{} is a valid file name".format(file_name), "success"
            else:
                message, status = "{} is a valid file name".format(file_name), "success"
        else:
            message, status = "Please enter a valid file name!", "error"

        return message, status

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))


def encrypt_decrypt_string(data, function):
    try:
        key_value = '7061737323313233'.encode('utf-8')
        iv_value = '7061737323313233'.encode('utf-8')
        cipher = AES.new(key_value, AES.MODE_CFB, iv_value)

        if function == "encrypt":
            encrypted_data = cipher.encrypt(data.encode("utf-8"))
            changed_data = b64encode(encrypted_data).decode("utf-8")
        else:
            raw = b64decode(data.encode("utf-8"))
            changed_data = cipher.decrypt(raw)
            changed_data = changed_data.decode("utf-8")

        return changed_data

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
