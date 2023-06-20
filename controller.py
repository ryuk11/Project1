"""
Script which invokes the backend API methods.
"""
import datetime
import logging
import os
from datetime import date

import pandas as pd
from flask import (request, render_template, flash, session, jsonify, make_response)
from flask_login import (login_required, logout_user, login_user, current_user)
from itsdangerous import URLSafeTimedSerializer
from passlib.hash import sha256_crypt
from werkzeug.exceptions import HTTPException

from app import application
from excel_file_parser import DailyScoreCard
from forms import WebApplicationForm
from model import (db, Users, TableKPIInsertValues, TableAMEAKPIDetailDim,
                   TableKPIInsertValuesOriginal, TableAMEARegionalWebValuesTemp,
                   TableAMEAGlobalValuesWebDim, TableFiscCalDy, Tokens)
from utils import (get_decrypted_value, allowed_file, send_password_reset_email,
                   insert_file_process, send_mail, check_file_pattern, encrypt_decrypt_string, insert_token)

UNAME = ''
STR_NETWORK_ID = ''


@application.errorhandler(Exception)
def handle_error(error_msg):
    """
    Function that return the 505 page incase of error
    """
    code = 500
    if isinstance(error_msg, HTTPException):
        code = error_msg.code
    application.logger.error(str(error_msg))
    send_mail("Please check attached log file.", "amea_analytics_core@kellogg.com",
              "Exception in Web Portal")
    return render_template('505.html'), code


@application.errorhandler(404)
def not_found_error(error):
    """
    Function that return Resource Not Found error
    """
    return render_template('404.html'), 404


@application.errorhandler(401)
def unauthorized_error(error):
    """
    Function that returns Unauthorized access page
    """

    return render_template('401.html', error_msg=error), 401


@application.after_request
def after_request(response):
    """
    Function to ensure that responses aren't cached
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@application.route('/index')
@application.route('/')
def render_home_page(form=None, flased_msg_show=None, flashed_msg=None):
    """
    Function to redirect to login page
    """
    try:
        if not session.get('logged_in'):
            application.logger.info("Login page accessed")
            if flased_msg_show:
                flash(flashed_msg, 'success')
                flashed_msg_show = True
            else:
                flashed_msg_show = False

            return render_template('login.html', form=form, flased_msg_show=flashed_msg_show)
        else:
            user_name = request.cookies.get('username')
            user_name = encrypt_decrypt_string(user_name, "decrypt")
            admin_flag = session.get("admin_access")
            if admin_flag == "YES":
                return render_template('admin.html', form=form, username=user_name,
                                       admin_access=session.get('admin_access'),
                                       global_data_access=session.get('global_data_access'),
                                       regular_access=session.get('regular_access'))

            else:
                return render_template('main.html', form=form, username=user_name,
                                       admin_access=session.get('admin_access'),
                                       global_data_access=session.get('global_data_access'),
                                       regular_access=session.get('regular_access'))


    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/main_as_home')
def render_main_as_home_page(form=None):
    """
    Function to render the user access page
    """

    try:

        if session.get('logged_in'):
            application.logger.info("User %s accessing Main Page", current_user.NETWORK_ID)
            user_name = request.cookies.get('username')
            user_name = encrypt_decrypt_string(user_name, "decrypt")
            network_id = request.cookies.get('network_id')
            network_id = encrypt_decrypt_string(network_id, "decrypt")
            application.logger.info('Manual Session User: ' + str(user_name))
            application.logger.info('Manual Network ID: ' + str(network_id))

            return render_template('main.html', form=form, username=user_name,
                                   admin_access=session.get('admin_access'),
                                   global_data_access=session.get('global_data_access'),
                                   regular_access=session.get('regular_access'))

        return render_template('login.html', form=form, flased_msg_show=False)
    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route("/logout")
@login_required
def logout():
    """
    Function to logout of the web application
    """
    try:
        form = WebApplicationForm()
        user = current_user
        user.authenticated = False
        session.clear()
        application.logger.info('Logging out user %s', current_user.NETWORK_ID)
        logout_user()
        application.logger.info('User logged out successfully')
        return render_template('login.html', form=form, flased_msg_show=False)
    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/admin_page')
def render_admin_page(form=None):
    """
    Function to render the admin home page
    """
    try:
        form = WebApplicationForm()
        if session.get('logged_in'):
            admin_flag = current_user.ADMIN_ACCESS
            if admin_flag == "YES":
                application.logger.info("User %s accessed admin page.", current_user.NETWORK_ID)
                logging.info("Admin Page")
                user_name = request.cookies.get('username')
                user_name = encrypt_decrypt_string(user_name, "decrypt")

                application.logger.info('Admin Session User ' + str(user_name))
                form.select_multi_plant_name.choices = list(
                    set([(dim.PLANT_NAME, dim.PLANT_NAME) for dim in
                         TableAMEAKPIDetailDim.query.all()]))
                return render_template('admin.html', username=current_user.F_NAME, form=form,
                                       admin_access=current_user.ADMIN_ACCESS)
            else:
                error_msg = "User {} not allowed to access admin home page.".format(
                    current_user.NETWORK_ID)
                application.logger.info(
                    "User {} not allowed to access admin home page.".format(
                        current_user.NETWORK_ID))
                return unauthorized_error(error_msg)

        return render_template('login.html', form=form, flased_msg_show=False)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/login', methods=['POST'])
def render_main_page():
    """
    Function to render the home page of regular or admin user
    """
    try:
        form = WebApplicationForm()
        if request.method == "POST":

            encrypted_uname = str(request.form["txt_name_uname"]).strip()
            encrypted_password = str(request.form["txt_name_pwd"]).strip()

            str_network_id = get_decrypted_value(encrypted_uname)
            str_network_id = str_network_id.lower()
            passwd = get_decrypted_value(encrypted_password)

            application.logger.info("Processing login for : %s", str_network_id)

            # Fetch one record and return result
            login = Users.query.filter_by(NETWORK_ID=str_network_id).first()

            if login is not None and sha256_crypt.verify(passwd, login.PASSWORD):
                u_name = str(login.F_NAME).strip()
                application.logger.info("Login successful for : %s", u_name)
                global_data_access = str(login.GLOBAL_DATA_ACCESS).strip()
                admin_access = str(login.ADMIN_ACCESS).strip()
                regular_access = str(login.REGULAR_ACCESS).strip()

                session['global_data_access'] = global_data_access
                session['admin_access'] = admin_access

                session['regular_access'] = regular_access

                today = date.today()
                cal_data = TableFiscCalDy.query.filter_by(FISC_DT=str(today)).first()

                window_open = "YES" if int(cal_data.FISC_DY_OF_PD) <= 31 else "NO"

                session['window_open'] = window_open
                # Admin Access only

                if admin_access == 'YES':
                    session['logged_in'] = True
                    session['uname'] = UNAME
                    session['network_id'] = str_network_id
                    login_user(login)
                    application.logger.info("Admin logged in.")
                    ''' form.select_multi_plant_name.choices = list(
                        set([(dim.PLANT_NAME, dim.PLANT_NAME) for 
                        dim in TableAMEAKPIDetailDim.query.all()]))'''

                    resp = make_response(render_admin_page(form))

                    encrypted_uname = encrypt_decrypt_string(UNAME, "encrypt")
                    encrypted_network_id = encrypt_decrypt_string(str_network_id, "encrypt")
                    resp.set_cookie('username', encrypted_uname)  # , expires=expire_date)
                    resp.set_cookie('network_id', encrypted_network_id)  # , expires=expire_date)
                    return resp
                else:
                    # Create session data, we can access this data in other routes
                    session['logged_in'] = True
                    session['uname'] = UNAME
                    session['network_id'] = str_network_id
                    login_user(login)
                    logging.info('Navigating to Main Page')
                    resp = make_response(render_main_as_home_page(form))

                    encrypted_uname = encrypt_decrypt_string(UNAME, "encrypt")
                    encrypted_network_id = encrypt_decrypt_string(str_network_id, "encrypt")
                    resp.set_cookie('username', encrypted_uname)  # , expires=expire_date)
                    resp.set_cookie('network_id', encrypted_network_id)  # , expires=expire_date)
                    return resp
            else:
                application.logger.error("Wrong credentials for %s", str_network_id)
                flash('Invalid credentials entered!', 'error')
                return render_home_page(form)
        return render_home_page(form)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/file_upload')
def render_file_upload_page(form=None):
    """
    Function to render the file upload page for normal users
    """
    try:
        form = WebApplicationForm()
        if session.get('logged_in'):
            global_data_flag = session.get('global_data_access')
            regular_flag = session.get('regular_access')
            if global_data_flag == "YES" or regular_flag == "YES":
                application.logger.info("User %s accessed file upload page.",
                                        current_user.NETWORK_ID)
                return render_template('upload.html', form=form, username=session.get('uname'),
                                       admin_access=session.get('admin_access'),
                                       global_data_access=global_data_flag,
                                       regular_access=regular_flag,
                                       window_open=session.get('window_open'))
            else:
                error_msg = "User is not allowed to access file upload user page."
                application.logger.info(
                    "User {} not allowed to access file upload user page.".format(
                        current_user.NETWORK_ID))
                return unauthorized_error(error_msg)

        return render_template('login.html', form=form, flased_msg_show=False)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/add_user')
def render_add_user_page(form=None):
    """
    function to render the add user page for admin user
    """

    try:
        form = WebApplicationForm()
        if session.get('logged_in'):
            admin_flag = current_user.ADMIN_ACCESS

            if admin_flag == "YES":
                application.logger.info("User %s accessed add user page.",
                                        current_user.NETWORK_ID)
                form.select_multi_plant_name.choices = list(
                    set([(dim.PLANT_NAME, dim.PLANT_NAME) for dim in
                         TableAMEAKPIDetailDim.query.all()]))
                return render_template('add_user.html', username=current_user.F_NAME, form=form,
                                       admin_access=admin_flag)
            else:
                error_msg = "User is not allowed to access add user page."
                application.logger.info("User {} not allowed to access add user page.".format(
                    current_user.NETWORK_ID))
                return unauthorized_error(error_msg)

        return render_template('login.html', form=form, flased_msg_show=False)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/update_user')
def render_update_user_page(form=None):
    """
    Function to render the update user page for admin user
    """
    try:
        form = WebApplicationForm()
        if session.get('logged_in'):
            admin_flag = current_user.ADMIN_ACCESS
            if admin_flag == "YES":
                application.logger.info("User %s accessed update user page.",
                                        current_user.NETWORK_ID)

                fetched_user_details = 'NO'
                logging.info("Update User Page")
                return render_template('update_user.html', username=current_user.F_NAME, form=form,
                                       admin_access=current_user.ADMIN_ACCESS,
                                       fetched_user_details=fetched_user_details)
            else:
                error_msg = "User is not allowed to access update user page."
                application.logger.info("User {} not allowed to access update user page.".format(
                    current_user.NETWORK_ID))
                return unauthorized_error(error_msg)

        return render_template('login.html', form=form, flased_msg_show=False)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/delete_user')
def render_delete_user_page(form=None):
    """
    Function to render Delete user page for admin users
    """

    try:
        form = WebApplicationForm()
        if session.get('logged_in'):
            admin_flag = current_user.ADMIN_ACCESS
            if admin_flag == "YES":
                application.logger.info("User %s accessed delete user page.",
                                        current_user.NETWORK_ID)
                return render_template('delete_user.html', username=current_user.F_NAME, form=form,
                                       admin_access=current_user.ADMIN_ACCESS)
            else:
                error_msg = "User is not allowed to access delete user page."
                application.logger.info(
                    "User {} not allowed to access delete user page.".format(
                        current_user.NETWORK_ID))
                return unauthorized_error(error_msg)

        return render_template('login.html', form=form, flased_msg_show=False)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/lnk_forgot_password')
def render_forgot_password_page(form=None):
    """
    Function to render the forgot password reset page
    """
    try:
        form = WebApplicationForm()
        application.logger.info("Accessing forgot password page.")
        return render_template('forgot_password.html', form=form)
    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    """
    Function to render the reset password page and reset the password
    """
    try:

        form = WebApplicationForm()
        application.logger.info("Accessing Reset Password.")
        password_reset_serializer = URLSafeTimedSerializer('SECRET_KEY')
        str_email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=600)

        token_data = Tokens.query.filter_by(TOKEN=token, EMAIL=str_email).first()

        if not token_data:
            raise Exception(f"Token {token} is no longer active!")

        if request.method == "POST" and 'btn_update_password' in request.form:
            form = WebApplicationForm()
            if str(request.form['password'].strip()) == str(request.form['cnf_password'].strip()):
                update_values = Users.query.filter_by(EMAIL=str_email).update(
                    dict(PASSWORD=sha256_crypt.encrypt(request.form['password'])))
                Tokens.query.filter_by(EMAIL=str_email, TOKEN=token, NETWORK_ID=token_data.NETWORK_ID).delete()
                db.session.commit()
                application.logger.info("Password reset successful.")
                flash("Password reset successful.", "success")
                return render_home_page(form)
            else:
                flash('Password does not match', 'error')
                application.logger.error('Password does not match!!!')
                return render_template('reset_password.html', form=form, token=token,
                                       password=str(request.form['password'].strip()),
                                       cnf_password=str(request.form['cnf_password'].strip()))

        else:
            validate_values = Users.query.filter_by(EMAIL=str_email).count()
            if validate_values == 1:
                return render_template('reset_password.html', form=form, token=token)
            else:
                application.logger.error("Invalid Link! Please contact your system administrator")
                return "Invalid Link! Please contact your system administrator"

    except Exception as exp_msg:
        application.logger.error(exp_msg)
        return "Link has been expired !! Please reset your password again!!"


@application.route("/forgot_password", methods=['POST'])
def forgot_password():
    """
    Function to render the forgot password form
    """
    try:
        form = WebApplicationForm()

        str_email = str(request.form['email']).strip().lower()
        str_network_id = str(request.form['networkid']).strip().lower()
        application.logger.info("Processing forgot password request for %s", str_network_id)
        validate_values = Users.query.filter_by(NETWORK_ID=str_network_id, EMAIL=str_email).first()
        if validate_values is not None:
            token = send_password_reset_email(str_email)
            insert_token(str_email, str_network_id, token)
            flash("Reset password link has been sent to your registered mail ID")

            return render_home_page(form)
        else:
            application.logger.error('Email Id or Network Id is Incorrect')
            flash('Email Id or Network Id is incorrect', 'error')
            return render_template('forgot_password.html', form=form)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/manual_fill')
def populate_manual_entry():
    """
    Function to populate the form value of Category in the manual data entry form
    """

    try:
        form = WebApplicationForm()
        if session.get("logged_in"):
            regular_access = session.get('regular_access')
            if regular_access == "YES":
                application.logger.info("Manual data entry access by %s", current_user.NETWORK_ID)
                today = date.today()
                cal_data = TableFiscCalDy.query.filter_by(FISC_DT=str(today)).first()
                drp_year_values = [
                    (str(int(cal_data.FISC_YR) + val), str(int(cal_data.FISC_YR) + val))
                    for val in [-1, 0]]
                data = Users.query.filter_by(NETWORK_ID=session.get('network_id')).first()
                plant_names = data.PLANT_NAME.split("~")
                form.drp_select_category.choices = [('', 'Select a Category')] + list(
                    set([(data.CATEGORY, data.CATEGORY) for data in
                         TableAMEAKPIDetailDim.query.all() if
                         data.PLANT_NAME in plant_names]))

                form.drp_select_plant.choices = [('', 'Select a Plant')]
                form.drp_select_sub_category.choices = [('', 'Select a Sub Category')]
                form.drp_select_function.choices = [('', 'Select a Function')]
                form.drp_select_year.choices = [('', 'Select a Year')] + drp_year_values
                form.drp_select_period.choices = [('', 'Select a Period')]

                form.drp_select_category.process_data('')
                form.drp_select_year.process_data('')
                form.ytdSelect.process_data('')
                form.typeSelect.process_data('')
                application.logger.info("Data for Category dropdown is fetched.")

                application.logger.info('Selected KPI\'s values are loaded into the form.')

                return render_template('manual_entry.html', form=form,
                                       username=session.get('uname'),
                                       admin_access=session.get('admin_access'),
                                       window_open=session.get('window_open'))
            else:
                error_msg = "User is not allowed to access file upload user page."
                application.logger.info(
                    "User {} not allowed to access file upload user page.".format(
                        current_user.NETWORK_ID))
                return unauthorized_error(error_msg)

        return render_template('login.html', form=form, flased_msg_show=False)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route("/regional_data")
def populate_regional_data_form(form=None):
    """
    Function to populate the form value of Period in the regional data entry form
    """

    try:

        form = WebApplicationForm()

        if session.get("logged_in"):
            global_data_access = session.get("global_data_access")

            if global_data_access == "YES":
                application.logger.info("Regional data entry page accessed by %s",
                                        current_user.NETWORK_ID)
                today = date.today()
                cal_data = TableFiscCalDy.query.filter_by(FISC_DT=str(today)).first()
                if current_user.ADMIN_ACCESS == 'NO':

                    if int(cal_data.FISC_DY_OF_PD) <= 31:
                        form.drp_select_period.choices = [('', 'Select a Period')] + \
                                                         list(
                                                             [("P" + str(int(cal_data.FISC_PD) - 3),
                                                               "P" + str(
                                                                   int(cal_data.FISC_PD) - 3)),
                                                              ("P" + str(int(cal_data.FISC_PD) - 2),
                                                               "P" + str(
                                                                   int(cal_data.FISC_PD) - 2)),
                                                              ("P" + str(int(cal_data.FISC_PD) - 1),
                                                               "P" + str(
                                                                   int(cal_data.FISC_PD) - 1))])
                    else:
                        form.drp_select_period.choices = [('', 'Select a Period')] + list(
                            [("P" + str(cal_data.FISC_PD),
                              "P" + str(cal_data.FISC_PD))])
                else:
                    form.drp_select_period.choices = [('', 'Select a Period')] + list(
                        [('P1', 'P1'), ('P2', 'P2'), ('P3', 'P3'), ('P4', 'P4'), ('P5', 'P5'),
                         ('P6', 'P6'),
                         ('P7', 'P7'),
                         ('P8', 'P8'), ('P9', 'P9'), ('P10', 'P10'), ('P11', 'P11'),
                         ('P12', 'P12')])

                today = date.today()
                cal_data = TableFiscCalDy.query.filter_by(FISC_DT=str(today)).first()
                drp_year_values = [
                    (str(int(cal_data.FISC_YR) + val), str(int(cal_data.FISC_YR) + val)) for
                    val
                    in [-1, 0]]
                form.drp_select_year.choices = [('', 'Select a Year')] + drp_year_values
                form.drp_select_region.choices = [('', 'Select a Region')] + list(
                    set([(data.REGION_NAME, data.REGION_NAME) for data in
                         TableAMEAGlobalValuesWebDim.query.all()]))
                form.drp_select_global_function.choices = [('', 'Select a Function')]

                form.drp_select_region.process_data('')
                form.drp_select_global_function.process_data('')
                form.drp_select_year.process_data('')
                form.drp_select_period.process_data('')
                form.drp_global_type_select.process_data('')
                form.ytdSelect.process_data('')

                return render_template('regional.html', form=form, username=current_user.F_NAME,
                                       admin_access=current_user.ADMIN_ACCESS,
                                       window_open=session.get('window_open'))
            else:
                error_msg = "User is not allowed to access global values page."
                application.logger.info(
                    "User {} not allowed to access global values page.".format(
                        current_user.NETWORK_ID))
                return unauthorized_error(error_msg)

        return render_template('login.html', form=form, flased_msg_show=False)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/insert_regional_data', methods=['POST'])
def insert_regional_data():
    """
    Insert the regional data into SQL database
    """
    try:
        application.logger.info("Method insert_regional_data called by %s", current_user.NETWORK_ID)
        form = WebApplicationForm()
        df_regional_values = pd.DataFrame(
            columns=['ID', 'REGION_NAME', 'FUNCTION_NAME', 'KPI_NAME', 'KPI_VALUES', 'YTD_or_MTD',
                     'YEAR', 'PERIOD',
                     'DATA_TYPE', 'CURR_TIME', 'NETWORK_ID'])
        if 'btn_submit' in request.form:
            if 'drp_select_period' in request.form:
                str_drp_period = request.form['drp_select_period']
            else:
                str_drp_period = 'YTD'

            str_drp_name_region = request.form['drp_select_region']
            str_drp_select_function = request.form['drp_select_global_function']
            str_drp_name_ytd_select = request.form['ytdSelect']
            int_drp_name_year = int(request.form['drp_select_year'])

            # Logic to check if previous year selected and change type column value
            curr_date = (datetime.datetime.now().strftime('%Y-%m-%d'))
            filtered_data = TableFiscCalDy.query.with_entities(TableFiscCalDy.FISC_YR).filter_by(
                FISC_DT=curr_date).first()

            str_drp_name_type_select = request.form['drp_global_type_select']
            str_all_textbox_names = request.form['hiddn_dynamic_txtbox_names'].split(",")
            all_textbox_names = list(
                filter(lambda txt_bx_name: 'target' not in txt_bx_name and txt_bx_name != '',
                       str_all_textbox_names))
            id_count = 0
            # Creating a dataframe for individual KPI values
            for str_txt_box_name in all_textbox_names:
                id_count += 1
                str_txt_hiddn_name = 'txt_hiddn_no_' + str(str_txt_box_name.split("_")[-1])
                str_txt_box_kpi_val = request.form[str_txt_box_name]
                str_txt_hiddn_kpi_name = request.form[str_txt_hiddn_name]
                df_regional_values = df_regional_values.append(pd.Series(
                    [id_count, str_drp_name_region, str_drp_select_function, str_txt_hiddn_kpi_name,
                     str_txt_box_kpi_val,
                     str_drp_name_ytd_select, int_drp_name_year, str_drp_period,
                     str_drp_name_type_select,
                     str(datetime.datetime.now()), current_user.NETWORK_ID],
                    index=df_regional_values.columns), ignore_index=True)

            df_regional_values = df_regional_values.to_dict(orient='records')

            application.logger.info("Inserting the global values into the database.")
            db.engine.execute(TableAMEARegionalWebValuesTemp.__table__.insert(),
                              df_regional_values)

            db.session.commit()

            flash("Selected global values are added successfully", 'success')
            application.logger.info("Selected global values are added successfully")

            return populate_regional_data_form(form)

        if 'btn_cancel' in request.form:
            form = WebApplicationForm()

            return populate_regional_data_form(form)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/insert_manual_entry', methods=['POST'])
def insert_manual_entry():
    """
    Insert the manual data entries into SQL database
    """

    try:
        application.logger.info("Method insert_manual_entry called by %s", current_user.NETWORK_ID)
        form = WebApplicationForm()
        df_kpi_values = pd.DataFrame(
            columns=['ID', 'PERIOD', 'CATEGORY', 'PLANT', 'KPI_NAME', 'KPI_VALUES', 'CURR_TIME',
                     'YEAR',
                     'YTD_or_MTD',
                     'DATA_TYPE', 'SUB_CATEGORY', 'FUNCTION_NAME', 'NETWORK_ID'])

        if 'btn_submit' in request.form:
            if 'drp_select_period' in request.form:
                str_drp_period = request.form['drp_select_period']
            else:
                str_drp_period = 'NULL'

            str_drp_name_category = request.form['drp_select_category']
            str_drp_name_plant = request.form['drp_select_plant']
            int_drp_name_year = int(request.form['drp_select_year'])
            str_drp_name_ytd_select = request.form['ytdSelect']
            str_drp_name_type_select = request.form['typeSelect']
            str_drp_select_sub_category = request.form['drp_select_sub_category']
            str_drp_select_function = request.form['drp_select_function']
            str_all_textbox_names = request.form['hiddn_dynamic_txtbox_names'].split(",")

            all_textbox_names = list(
                filter(lambda txt_bx_name: 'target' not in txt_bx_name and txt_bx_name != '',
                       str_all_textbox_names))

            id_count = 0

            for str_txt_box_name in all_textbox_names:
                id_count += 1

                str_txt_hiddn_name = 'txt_hiddn_no_' + str(str_txt_box_name.split("_")[-1])
                str_txt_box_kpi_val = request.form[str_txt_box_name]
                str_txt_hiddn_kpi_name = request.form[str_txt_hiddn_name]

                df_kpi_values = df_kpi_values.append(pd.Series(
                    [id_count, str_drp_period, str_drp_name_category, str_drp_name_plant,
                     str_txt_hiddn_kpi_name,
                     str_txt_box_kpi_val, datetime.datetime.now(), int_drp_name_year,
                     str_drp_name_ytd_select,
                     str_drp_name_type_select, str_drp_select_sub_category, str_drp_select_function,
                     current_user.NETWORK_ID],
                    index=df_kpi_values.columns), ignore_index=True)
            df_kpi_values = df_kpi_values.to_dict(orient='records')
            application.logger.info("Inserting the manual entries into database")

            db.engine.execute(TableKPIInsertValues.__table__.insert(), df_kpi_values)

            db.session.commit()

            flash('Manual entry added successfully!', 'success')

            return populate_manual_entry()

        if 'btn_cancel' in request.form:
            return populate_manual_entry()


    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/insert_upload_file_to_db', methods=['POST'])
def insert_upload_file_to_db():
    """
    Insert the uploaded file into SQL database
    """

    try:
        if 'btn_upload' in request.form:
            application.logger.info("Method insert_upload_file_to_db called by "
                                    "%s", current_user.NETWORK_ID)
            file = request.files['file']
            if file and allowed_file(file.filename):
                today = date.today()
                user_data = Users.query.filter_by(NETWORK_ID=current_user.NETWORK_ID).first()
                cal_data = TableFiscCalDy.query.filter_by(FISC_DT=str(today)).first()
                file.save(os.path.join(os.environ.get("UPLOAD_FOLDER"), file.filename))
                application.logger.info("Excel file {} uploaded".format(file.filename))

                message, status = check_file_pattern(file.filename)

                if status == "error":
                    application.logger.error(message)

                else:
                    global_kpi_values = list(set([(data.FUNCTION_NAME, data.KPI_NAME)
                                                  for data in TableAMEAGlobalValuesWebDim.query.all()]))

                    plant_name_list = list(set([dim.PLANT_NAME for dim in
                                                TableAMEAKPIDetailDim.query.all()]))

                    # Parse the excel file and return the dataframe
                    file_path = DailyScoreCard(
                        daily_file=os.path.join(os.environ.get("UPLOAD_FOLDER"), file.filename),
                        current_period=int(cal_data.FISC_PD) - 1,
                        current_year=int(cal_data.FISC_YR),
                        plant_nm=user_data.PLANT_NAME,
                        sc_access=user_data.REGULAR_ACCESS,
                        regional_access=user_data.GLOBAL_DATA_ACCESS,
                        sc_user=current_user.NETWORK_ID,
                        global_kpi_values=global_kpi_values,
                        plant_name_list=plant_name_list
                    )
                    data_frame, tab_name = DailyScoreCard.read_daily_files(file_path)

                    # Insert the dataframe into SQL Database
                    message, status = insert_file_process(data_frame, tab_name)

                    if status == "error":
                        application.logger.error(message)
                    else:
                        application.logger.info(message)
                # Remove the uploaded excel file

                os.remove(os.path.join(os.environ.get("UPLOAD_FOLDER"), file.filename))
                application.logger.info("Removed the uploaded file " + file.filename)
                form = WebApplicationForm()
                flash(message, status)
                return render_file_upload_page(form)
    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/frm_delete_user_page', methods=['POST'])
def delete_user():
    """
    Function to delete the user. Performed by Admin
    """

    try:
        form = WebApplicationForm()
        if request.method == "POST" and 'btn_delete_user' in request.form:
            network_id = str(request.form['networkid']).lower()

            if network_id != 'admin':
                user_count = int(Users.query.filter_by(NETWORK_ID=network_id.strip()).count())

                if user_count > 0:
                    user_detail = Users.query.filter_by(NETWORK_ID=network_id.strip()).first()
                    db.session.delete(user_detail)
                    db.session.commit()
                    application.logger.info("Deleted User details for User ID : {}".format(
                        network_id))
                    flash('User deleted successfully', 'success')
                    return render_delete_user_page(form)
                else:
                    msg = " is not exist**"
                    application.logger.info("User {} doesn't exist".format(network_id))
                    flash('User does not exist', 'error')
                    return render_template('delete_user.html', form=form, username=UNAME,
                                           networkid=network_id,
                                           netid_color="red",
                                           netid_msg=msg, admin_access=current_user.ADMIN_ACCESS)
            else:
                flash('Can not delete the user!', 'error')
                application.logger.info("Can't delete user as User ID is admin.")
                return render_template('delete_user.html', form=form, username=UNAME,
                                       admin_access=current_user.ADMIN_ACCESS)
        elif request.method == "POST" and 'btn_cancel' in request.form:
            return render_admin_page(form)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/frm_add_user_page', methods=['POST'])
def add_user():
    """
    Function to add user to SQL database. Performed by Admin
    """

    try:
        form = WebApplicationForm()
        if request.method == "POST" and 'btn_submit_admin' in request.form:

            form.select_multi_plant_name.choices = [('', 'Select a Plant')] + list(
                set([(dim.PLANT_NAME, dim.PLANT_NAME) for dim in
                     TableAMEAKPIDetailDim.query.all()]))
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            email = str(request.form['emailid']).lower()
            plant_name = "~".join(request.form.getlist('select_multi_plant_name'))
            network_id = request.form['networkid']
            network_id = network_id.lower()
            password = sha256_crypt.encrypt(request.form['password'])
            admin_access, regular_access, regional_access = ['NO', 'NO', 'NO']

            if 'admin_access' in request.form:
                admin_access = 'YES'
            if 'regular_access' in request.form:
                regular_access = 'YES'
            if 'regional_access' in request.form:
                regional_access = 'YES'

            count = int(
                Users.query.filter_by(NETWORK_ID=network_id.strip(), EMAIL=email.strip()).count())
            email_count = int(Users.query.filter_by(EMAIL=email.strip()).count())
            user_count = int(Users.query.filter_by(NETWORK_ID=network_id.strip()).count())

            if count == 1 or email_count + user_count >= 2:
                msg = "User ID already exists."
                application.logger.info("User ID {} already exists".format(network_id))
                flash(msg, 'error')
                return render_template('add_user.html', username=UNAME,
                                       form=form, firstname=first_name, lastname=last_name,
                                       emailid=email, networkid=network_id,
                                       email_color="red", netid_color="red", netid_msg=msg,
                                       email_msg=msg, admin_access=current_user.ADMIN_ACCESS)
            else:

                if email_count == 1 and user_count == 0:
                    msg = " already used**"
                    application.logger.info("Email {} already exists".format(email))
                    flash("Email ID already exists", "error")
                    return render_template('add_user.html', username=UNAME, form=form,
                                           firstname=first_name,
                                           lastname=last_name,
                                           emailid=email, networkid=network_id, email_color="red",
                                           email_msg=msg, admin_access=current_user.ADMIN_ACCESS)

                elif email_count == 0 and user_count == 1:
                    msg = " already used**"
                    flash("User ID already exists", 'error')
                    application.logger.info("User ID {} already exists".format(network_id))
                    return render_template('add_user.html', username=UNAME, form=form,
                                           firstname=first_name,
                                           lastname=last_name,
                                           emailid=email, networkid=network_id, netid_color="red",
                                           netid_msg=msg, admin_access=current_user.ADMIN_ACCESS)
                else:
                    max_id = len(list([dim.ID for dim in Users.query.all()]))
                    max_id = 0 if max_id == 0 else max(list([dim.ID for dim in Users.query.all()]))
                    new_eg = Users(max_id + 1, first_name, last_name, email, plant_name,
                                   network_id,
                                   password,
                                   admin_access,
                                   regional_access, regular_access)
                    db.session.add(new_eg)
                    application.logger.info("Adding user : {}".format(network_id))
                    db.session.commit()
                    flash("User added successfully", "success")
                    return render_add_user_page(form)
    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/frm_update_user', methods=['GET', 'POST'])
def update_user(form=None):
    """
    Function to update the existing user in SQL database. Performed by Admin
    """

    try:
        form = WebApplicationForm()
        if request.method == "POST" and 'btn_search_user' in request.form:
            network_id = str(request.form['networkid1']).lower()
            netid_count = int(Users.query.filter_by(NETWORK_ID=network_id.strip()).count())
            # Search data corresponding to a network_id
            if netid_count == 1:
                application.logger.info("Found the details for {}".format(str(network_id)))
                fetched_user_details = 'YES'
                chk_admin_access, chk_regular_access, chk_regional_access = ['unchecked',
                                                                             'unchecked',
                                                                             'unchecked']
                user_data = Users.query.filter_by(NETWORK_ID=network_id.strip()).first()
                first_name = user_data.F_NAME
                last_name = user_data.L_NAME
                email_id = user_data.EMAIL
                network_id = user_data.NETWORK_ID
                hidden_plants = str(user_data.PLANT_NAME)
                if user_data.ADMIN_ACCESS == 'YES':
                    chk_admin_access = 'checked'
                if user_data.REGULAR_ACCESS == 'YES':
                    chk_regular_access = 'checked'
                if user_data.GLOBAL_DATA_ACCESS == 'YES':
                    chk_regional_access = 'checked'
                form.select_multi_plant_name.choices = list(
                    set([(dim.PLANT_NAME, dim.PLANT_NAME) for dim in
                         TableAMEAKPIDetailDim.query.all()]))

                return render_template('update_user.html', username=UNAME, form=form,
                                       admin_access=current_user.ADMIN_ACCESS,
                                       fetched_user_details=fetched_user_details,
                                       firstname=first_name,
                                       lastname=last_name,
                                       emailid=email_id, networkid=network_id,
                                       hidden_plants=hidden_plants,
                                       chk_regular_access=chk_regular_access,
                                       chk_regional_access=chk_regional_access,
                                       chk_admin_access=chk_admin_access)

            else:
                msg = " is not present**"
                application.logger.info("User detail not found for user ID {}".format(network_id))
                fetched_user_details = 'NO'
                flash("User details not found", "error")
                return render_template('update_user.html', username=UNAME, form=form,
                                       admin_access=current_user.ADMIN_ACCESS,
                                       fetched_user_details=fetched_user_details, netid_msg=msg,
                                       netid_color="red")

        elif request.method == "POST" and 'btn_update_user' in request.form:
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            email = request.form['emailid']
            plant_name = "~".join(request.form.getlist('select_multi_plant_name'))
            network_id = request.form['hidden_netid']
            admin_access, regular_access, regional_access = ['NO', 'NO', 'NO']
            if 'admin_access' in request.form:
                admin_access = 'YES'
            if 'regular_access' in request.form:
                regular_access = 'YES'
            if 'regional_access' in request.form:
                regional_access = 'YES'
            application.logger.info("Updating the entries for user ID : {}".format(str(network_id)))
            update_values = Users.query.filter_by(NETWORK_ID=network_id).update(
                dict(F_NAME=first_name, L_NAME=last_name, EMAIL=email, PLANT_NAME=plant_name,
                     ADMIN_ACCESS=admin_access,
                     REGULAR_ACCESS=regular_access, GLOBAL_DATA_ACCESS=regional_access))
            db.session.commit()
            flash("Updated the user details", "success")

            return render_update_user_page(form)

        elif request.method == "POST" and 'btn_u_cancel_user' in request.form:
            return render_update_user_page(form)
        elif request.method == "POST" and 'btn_cancel' in request.form:
            return render_admin_page(form)

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/drp_select_sub_category/<category>')
def populate_sub_category_field(category):
    """
    Function to populate subcategory in manual entry form based on the value
    selected in Category dropdown input.
    """

    try:
        str_category_data = TableAMEAKPIDetailDim.query.filter_by(CATEGORY=category).all()
        data = Users.query.filter_by(NETWORK_ID=current_user.NETWORK_ID).first()
        plant_data = data.PLANT_NAME.split("~")

        str_plant_array = []

        application.logger.info("Retreiving sub category values for category : {}".format(str(
            category)))

        for plant in str_category_data:
            if plant.PLANT_NAME in plant_data:
                plant_dict = {}
                plant_dict['id'] = plant.SUB_CATEGORY
                plant_dict['name'] = plant.SUB_CATEGORY
                str_plant_array.append(plant_dict)

        first_field = [{'id': '', 'name': 'Select a Sub Category'}]
        str_plant_array = list({v['id']: v for v in str_plant_array}.values())
        return jsonify({'str_category_data': first_field + str_plant_array})

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/drp_select_plant/<sub_category>')
def populate_plants_field(sub_category):
    """
    Function to populate plant values in manual entry form based on the value
    selected in Sub Category dropdown input.
    """

    try:

        str_category_data = TableAMEAKPIDetailDim.query.filter_by(SUB_CATEGORY=sub_category).all()
        data = Users.query.filter_by(NETWORK_ID=current_user.NETWORK_ID).first()
        plant_data = data.PLANT_NAME.split("~")

        str_plant_array = []
        application.logger.info("Retreiving plant values for sub category : {}".format(str(
            sub_category)))

        for plant in str_category_data:
            if plant.PLANT_NAME in plant_data:
                plant_dict = {}
                plant_dict['id'] = plant.PLANT_NAME
                plant_dict['name'] = plant.PLANT_NAME
                str_plant_array.append(plant_dict)

        first_field = [{'id': '', 'name': 'Select a Plant'}]
        str_plant_array = list({v['id']: v for v in str_plant_array}.values())
        return jsonify({'str_category_data': first_field + str_plant_array})

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/drp_select_function/<selected_type>')
def populate_function_name_field(selected_type):
    """
    Function to populate function_name in manual entry form based on the value
    selected in selected_type dropdown input.
    """
    try:
        selected_plant = selected_type.split(";")

        str_type = 'Actual' if selected_plant[0].strip() == 'Adjusted Actual' else 'Target'

        str_category_data = TableAMEAKPIDetailDim.query.filter_by(PLANT_NAME=selected_plant[1],
                                                                  TYPE=str_type).all()
        str_plant_array = []
        application.logger.info("Retrieving function names based on the selected type {}".format(
            str(selected_type)))
        for plant in str_category_data:
            plant_dict = {}
            plant_dict['id'] = plant.FUNCTION_NAME
            plant_dict['name'] = plant.FUNCTION_NAME
            str_plant_array.append(plant_dict)

        first_field = [{'id': '', 'name': 'Select a Function'}]
        str_plant_array = list({v['id']: v for v in str_plant_array}.values())
        return jsonify({'str_category_data': first_field + str_plant_array})

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/select_multi_kpi_name/<function_name>')
def populate_kpi_values_field(function_name):
    """
    Function to fetch the selected KPI values based on the function name value selected in the
    manual entry form.
    """

    try:
        selected_values = function_name.split(";")
        str_type = 'Actual' if selected_values[1].strip() == 'Adjusted Actual' else 'Target'

        str_plant_data = TableAMEAKPIDetailDim.query.filter_by(PLANT_NAME=selected_values[2],
                                                               FUNCTION_NAME=selected_values[0],
                                                               TYPE=str_type).all()

        str_kpi_array = []
        str_kpi_data_type_array = []
        str_period_array = []

        application.logger.info("Retrieving KPI values based on the selected function name " + str(
            function_name))

        for plant in str_plant_data:
            kpi_dict = {}

            kpi_dict['key'] = plant.KPI_NAME
            kpi_dict['value'] = plant.KPI_NAME

            if plant.DATA_TYPE == 'string':
                str_kpi_data_type_array.append(plant.KPI_NAME)

            str_kpi_array.append(kpi_dict)

        str_kpi_array = list({v['key']: v for v in str_kpi_array}.values())

        today = date.today()
        # Fetch selected KPI values
        if selected_values[0].strip().lower() == 'Natural Resource Conservation'.strip().lower() \
                and current_user.ADMIN_ACCESS == 'NO':

            str_period_arr = [('Select a Period')]

            for period in str_period_arr:
                str_period_obj = {}

                str_period_obj['key'] = period
                str_period_obj['value'] = period

                str_period_array.append(str_period_obj)

            str_period_array = list({v['key']: v for v in str_period_array}.values())

        elif selected_values[0].strip().lower() != 'Natural Resource Conservation'.strip().lower() \
                and current_user.ADMIN_ACCESS == 'NO':

            str_period_arr = [('Select a Period')]

            for period in str_period_arr:
                str_period_obj = {}

                str_period_obj['key'] = period
                str_period_obj['value'] = period

                str_period_array.append(str_period_obj)

            str_period_array = list({v['key']: v for v in str_period_array}.values())

        elif current_user.ADMIN_ACCESS == 'YES':

            str_period_array = 'NO'

        str_kpi_array = list({v['key']: v for v in str_kpi_array}.values())

        return jsonify(
            {'str_plant_data': str_kpi_array, 'str_kpi_data_type_array': str_kpi_data_type_array,
             'str_period_array': str_period_array})

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/multi_drp_kpi_click/<all_values>')
def check_kpi_values(all_values):
    """
    Function to check whether the KPI exists based on the all_values input parameter
    """

    try:
        str_kpi_array = all_values.split(";")

        if str(str_kpi_array[4]).strip() == 'Target':
            target_value = int(
                TableKPIInsertValuesOriginal.query.filter_by(PLANT=str_kpi_array[1],
                                                             CATEGORY=str_kpi_array[0],
                                                             KPI_NAME=str_kpi_array[3].replace(
                                                                 '~',
                                                                 '/'),
                                                             YEAR=str_kpi_array[2],
                                                             DATA_TYPE='Target',
                                                             PERIOD=str_kpi_array[5]).count())
            if target_value == 0:
                val = 'NO'
            else:
                val = 'YES'
        else:
            val = 'NO'
        if val == "NO":
            application.logger.info("KPI values doesn't exist")
        else:
            application.logger.info("KPI values exist")

        return jsonify({'kpi_exist': str(val)})

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/drp_select_global_function/<selected_region>')
def populate_global_function_name_field(selected_region):
    """
    Function to fetch the function name value based on the region value in the Global Access
    entry form
    """

    try:
        str_function_data = TableAMEAGlobalValuesWebDim.query.filter_by(
            REGION_NAME=selected_region).all()
        str_function_array = []
        application.logger.info("Fetching the function name based on the selected region {}".format(
            selected_region))
        for region in str_function_data:
            function_obj = {}
            function_obj['id'] = region.FUNCTION_NAME
            function_obj['name'] = region.FUNCTION_NAME
            str_function_array.append(function_obj)

        first_field = [{'id': '', 'name': 'Select a Function'}]
        str_function_array = list({v['id']: v for v in str_function_array}.values())
        return jsonify({'str_function_data': first_field + str_function_array})

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/select_global_multi_kpi_name/<function_name>')
def populate_global_kpi_field(function_name):
    """
    Function to fetch the selected KPI values based on the function name value selected in the
    Global value entry form.
    """

    try:
        selected_values = function_name.split(";")

        if str(selected_values[1]) not in ['Actual', 'Target']:
            str_type = 'Target'
        else:
            str_type = 'Actual'
        str_plant_data = TableAMEAGlobalValuesWebDim.query.filter_by(
            FUNCTION_NAME=selected_values[0],
            TYPE=str_type,
            REGION_NAME=selected_values[2]).all()
        str_kpi_array = []
        str_kpi_data_type_array = []
        str_period_array = []

        application.logger.info("Fetching KPI values based on the function name : {} ".format(
            str(function_name)))
        for plant in str_plant_data:
            kpi_dict = {}

            kpi_dict['key'] = plant.KPI_NAME
            kpi_dict['value'] = plant.KPI_NAME

            if plant.DATA_TYPE == 'string':
                str_kpi_data_type_array.append(plant.KPI_NAME)

            str_kpi_array.append(kpi_dict)
        today = date.today()
        cal_data = TableFiscCalDy.query.filter_by(FISC_DT=str(today)).first()
        # Check if KPI values are selected
        if selected_values[0].strip().lower() == 'Natural Resource Conservation'.strip().lower() \
                and current_user.ADMIN_ACCESS == 'NO':

            str_period_arr = [('Select a Period')] + list(
                ["P" + str(int(cal_data.FISC_PD) - 3), "P" + str(int(cal_data.FISC_PD) - 2),
                 "P" + str(int(cal_data.FISC_PD) - 1)])

            for period in str_period_arr:
                str_period_obj = {}

                str_period_obj['key'] = period
                str_period_obj['value'] = period

                str_period_array.append(str_period_obj)

            str_period_array = list({v['key']: v for v in str_period_array}.values())

        elif selected_values[0].strip().lower() != 'Natural Resource Conservation'.strip().lower() \
                and current_user.ADMIN_ACCESS == 'NO':

            str_period_arr = list(
                ['Select a Period', "P" + str(int(cal_data.FISC_PD) - 3),
                 "P" + str(int(cal_data.FISC_PD) - 2),
                 "P" + str(int(cal_data.FISC_PD) - 1)])

            for period in str_period_arr:
                str_period_obj = {}
                str_period_obj['key'] = period
                str_period_obj['value'] = period

                str_period_array.append(str_period_obj)

            str_period_array = list({v['key']: v for v in str_period_array}.values())

        elif current_user.ADMIN_ACCESS == 'YES':

            str_period_array = 'NO'

        str_kpi_array = list({v['key']: v for v in str_kpi_array}.values())

        return jsonify(
            {'str_plant_data': str_kpi_array, 'str_kpi_data_type_array': str_kpi_data_type_array,
             'str_period_array': str_period_array})

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')


@application.route('/drp_select_period/<str_year>')
def populate_period_field(str_year):
    """
    Function to fetch the periods based on the year value in the global access entry form.
    """

    try:
        str_period_array = []
        today = date.today()
        cal_data = TableFiscCalDy.query.filter_by(FISC_DT=str(today)).first()
        if int(str_year) < int(cal_data.FISC_YR):
            str_period_arr = list(["P" + str(pd) for pd in range(1, 13)])
        else:
            #str_period_arr = list(["P" + str(pd) for pd in range(1, int(cal_data.FISC_PD) + 1)])
            str_period_arr = list(["P" + str(pd) for pd in range(1, int(cal_data.FISC_PD))])

        application.logger.info("Fetching the periods for the year {}".format(str(str_year)))
        for period in str_period_arr:
            str_period_obj = {}

            str_period_obj['key'] = period
            str_period_obj['value'] = period

            str_period_array.append(str_period_obj)

        str_period_array = list({v['key']: v for v in str_period_array}.values())

        first_field = [{'key': '', 'value': 'Select a Period'}]
        return jsonify({'str_period_data': first_field + str_period_array})

    except Exception as exp_msg:
        application.logger.error(str(exp_msg))
        return render_template('505.html')
