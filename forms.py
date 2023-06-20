"""
Script that defines the form inputs used throughout the project
"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, SelectMultipleField


class WebApplicationForm(FlaskForm):
    """
    Form class that defines the form inputs used throughout the project
    """

    drp_select_period = SelectField('period', choices=[])
    drp_select_category = SelectField('category', choices=[])
    drp_select_plant = SelectField('plant', choices=[])
    drp_select_region = SelectField('Region', choices=[])
    drp_select_year = SelectField('year', choices=[])
    drp_select_function = SelectField('function_name', choices=[])
    drp_select_global_function = SelectField('function name', choices=[])
    drp_select_sub_category = SelectField('sub_category', choices=[])
    ytdSelect = SelectField('ytdmtd',
                            choices=[('', 'Select a Period'), ('MTD', 'MTD'), ('YTD', 'YTD')])
    typeSelect = SelectField('typeSelect',
                             choices=[('', 'Select a Type'), ('Adjusted Actual', 'Actual'),
                                      ('Current Month YTD', 'Current Month YTD')])
    drp_global_type_select = SelectField('drp_global_type_select',
                                         choices=[('', 'Select a Type'), ('Actual', 'Actual'),
                                                  ('Current Month YTD', 'Current Month YTD')])

    select_multi_kpi_name = SelectMultipleField('KPIlist', choices=[])
    select_global_multi_kpi_name = SelectMultipleField('Global KPIlist', choices=[])
    select_multi_plant_name = SelectMultipleField('multi_plant_name', choices=[])
    select_multi_user_access = SelectMultipleField('User Access',
                                                   choices=[('Regular User', 'Regular User'),
                                                            ('Regional User', 'Regional User'),
                                                            ('Admin User', 'Admin User')])
    btn_upload = SubmitField('Submit')
    btn_submit = SubmitField('Submit')
    btn_cancel = SubmitField('Cancel')
    btn_add = SubmitField('Add')
    btn_submit_admin = SubmitField('Submit')
    btn_clear_admin = SubmitField('Clear')
    btn_reset_password = SubmitField('Reset Password')
    btn_update_password = SubmitField('Update Password')
    btn_delete_user = SubmitField('Delete User')
    btn_search_user = SubmitField('Fetch User Details')
    btn_update_user = SubmitField('Update User')
    btn_u_cancel_user = SubmitField('Cancel')
