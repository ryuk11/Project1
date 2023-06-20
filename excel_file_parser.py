# -*- coding: utf-8 -*-
"""
Script to parse the excel files for file upload
"""
import os
import re
from datetime import datetime

import numpy as np
import pandas as pd

from app import application


class DailyScoreCard:
    """ Daily Score Card excel parser class """

    def __init__(self, **input_dict):
        """ Constructor """
        self.daily_file = input_dict.get("daily_file")
        self.current_period = input_dict.get("current_period")
        self.current_year = input_dict.get("current_year")
        self.plant_nm = input_dict.get("plant_nm")
        self.sc_access = input_dict.get("sc_access")
        self.regional_access = input_dict.get("regional_access")
        self.sc_user = input_dict.get("sc_user")
        self.global_kpi_values = input_dict.get("global_kpi_values")
        self.plant_name_list = input_dict.get("plant_name_list")

        self.set_input_values()

    def set_input_values(self):
        """
        Set the initial input values needed in the future
        :return: None
        """
        self.metric_column = ['Metric', 'Sub-Metric', 'Sub-KPI', 'UOM']
        self.metric_column_target = ['Metric', 'Sub-Metric', 'Sub-KPI', 'UOM']
        self.metric_column_1 = ['Sub-Metric', 'UOM']

        # Creating dictionary for Month Values
        self.month_dict_1 = {'Jan': ['P01', '1'], 'Feb': ['P02', '2'], 'Mar': ['P03', '3'],
                             'Apr': ['P04', '4'],
                             'May': ['P05', '5'], 'Jun': ['P06', '6'], 'Jul': ['P07', '7'],
                             'Aug': ['P08', '8'],
                             'Sep': ['P09', '9'], 'Oct': ['P10', '10'], 'Nov': ['P11', '11'],
                             'Dec': ['P12', '12'],
                             'YTD': 'YTD'}

        # creating dictionary for month Names
        self.month_dict_name = {'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
                                'May': 'May', 'June': 'June', 'July': 'July', 'August': 'August',
                                'September': 'Sep', 'October': 'Oct', 'November': 'Nov',
                                'December': 'Dec'
                                }

        # creating dictionary for sub-metrics and their respective metric
        self.metric_dict = self.convert(self.global_kpi_values)

        self.list_3_sc = {'P01', 'P02', 'P03', 'P04', 'P05', 'P06', 'P07', 'P08', 'P09', 'P10',
                          'P11', 'P12',
                          'Metric', 'Sub-Metric', 'Sub-KPI', 'UOM', 'Unnamed: 0'
                          }

        self.list_3_target = {'Metric', 'Sub-Metric', 'Sub-KPI', 'UOM'}
        self.list_4_target = {'P01', 'P01 YTD', 'P02', 'P02 YTD',
                              'P03', 'P03 YTD', 'P04', 'P04 YTD', 'P05', 'P05 YTD', 'P06',
                              'P06 YTD',
                              'P07', 'P07 YTD', 'P08', 'P08 YTD', 'P09', 'P09 YTD', 'P10',
                              'P10 YTD',
                              'P11', 'P11 YTD', 'P12', 'P12 YTD'}

        self.column_transforms = {
            "Actual": {
                "rename_cols": {'Metric': 'METRIC',
                                'Sub-Metric': 'SUB_METRIC',
                                'Sub-KPI': 'SUB_KPI',
                                'Type (Actual/Planned)': 'TYPE_ACTUAL_PLANNED',
                                'UOM': 'UOM',
                                'Date': 'DATE',
                                'Week': 'WEEK', 'Network_Id': 'NETWORK_ID',
                                'Load_Date': 'UPLOAD_DATE',
                                'Actual': 'ACTUAL',
                                'Source Name': 'SOURCE_NAME',
                                'Source Type': 'SOURCE_TYPE',
                                'Plant': 'PLANT', 'Year': 'YEAR',
                                'Period': 'PERIOD',
                                'Month No': 'MONTH_NO',
                                'Month_sf': 'MONTH_SF',
                                'Month_lf': 'MONTH_LF',
                                'Category': 'CATEGORY',
                                'Sub_Category': 'SUB_CATEGORY'},

                "selected_cols": ['METRIC', 'SUB_METRIC',
                                  'SUB_KPI', 'TYPE_ACTUAL_PLANNED',
                                  'UOM',
                                  'DATE', 'ACTUAL', 'SOURCE_NAME',
                                  'SOURCE_TYPE',
                                  'PLANT', 'YEAR', 'PERIOD',
                                  'MONTH_NO', 'WEEK', 'MONTH_SF',
                                  'MONTH_LF',
                                  'CATEGORY', 'SUB_CATEGORY',
                                  'NETWORK_ID',
                                  'UPLOAD_DATE']
            },
            "Target": {
                "rename_cols": {'Metric': 'METRIC',
                                'Sub-Metric': 'SUB_METRIC',
                                'Sub-KPI': 'SUB_KPI',
                                'Type (Actual/Planned)': 'TYPE_ACTUAL_PLANNED',
                                'UOM': 'UOM',
                                'Date': 'DATE',
                                'Network_Id': 'NETWORK_ID',
                                'Load_Date': 'UPLOAD_DATE',
                                'Actual': 'ACTUAL',
                                'Source Name': 'SOURCE_NAME',
                                'Source Type': 'SOURCE_TYPE',
                                'Plant': 'PLANT', 'Year': 'YEAR',
                                'Period': 'PERIOD',
                                'Month No': 'MONTH_NO', 'Week': 'WEEK',
                                'Month_sf': 'MONTH_SF',
                                'Month_lf': 'MONTH_LF',
                                'Category': 'CATEGORY',
                                'Sub_Category': 'SUB_CATEGORY'},

                "selected_cols": ['METRIC', 'SUB_METRIC',
                                  'SUB_KPI', 'TYPE_ACTUAL_PLANNED',
                                  'UOM',
                                  'DATE', 'ACTUAL', 'SOURCE_NAME',
                                  'SOURCE_TYPE',
                                  'PLANT', 'YEAR', 'PERIOD',
                                  'MONTH_NO', 'WEEK', 'MONTH_SF',
                                  'MONTH_LF',
                                  'CATEGORY', 'SUB_CATEGORY',
                                  'NETWORK_ID',
                                  'UPLOAD_DATE']
            },
            "Regional": {

                "rename_cols": {'Region': 'REGION_NAME',
                                'Function_Name': 'FUNCTION_NAME',
                                'KPI': 'KPI_NAME',
                                'KPI_VALUES': 'KPI_VALUES',
                                'YTD_OR_MTD': 'YTD_or_MTD',
                                'Year': 'YEAR',
                                'Period': 'PERIOD',
                                'Data_Type': 'DATA_TYPE',
                                'Current_Time': 'CURR_TIME',
                                'Network_Id': 'NETWORK_ID'},
                "selected_cols": ['ID', 'REGION_NAME', 'FUNCTION_NAME',
                                  'KPI_NAME', 'KPI_VALUES', 'YTD_or_MTD',
                                  'YEAR', 'PERIOD', 'DATA_TYPE',
                                  'CURR_TIME',
                                  'NETWORK_ID']
            }
        }

    @classmethod
    def convert(cls, values):
        """
        Convert tuples to dictionary
        :param values: tuple values
        :return: dictionary
        """
        try:
            output_dict = {}
            for key, value in values:
                output_dict.setdefault(key, []).append(value)
            return output_dict
        except Exception as exp_msg:
            application.logger.error(str(exp_msg))

    @classmethod
    def get_key(cls, dictionary, value):
        """
        Get key based on value parameter from dictionary
        :param dictionary: Input dict
        :param value: value to be searched
        :return: key
        """

        try:
            key_val = None
            for key, val in dictionary.items():
                if value in val:
                    key_val = key
                    break

            return key_val

        except KeyError as key_error:

            application.logger.error(str(key_error))

    def get_final_static_values(self, scorecard_df, plant_name):
        """
        Function to fetch the final set of similar values of both Actual and Target file types
        :param scorecard_df: Initial dataframe input
        :param plant_name: Name of the plant
        :return: Scorecard dataframe
        """
        if plant_name.lower() == 'Rayong Snacks'.lower():
            sub_category = 'Wholesome'
            category = 'Snacks'

        elif plant_name.lower() in ('ernstek', 'enstek'):
            sub_category = 'Salty'
            category = 'Snacks'

        else:
            sub_category = 'RTEC'
            category = 'Cereal'

        scorecard_df['Category'] = category
        scorecard_df['Sub_Category'] = sub_category

        scorecard_df['Sub-Metric'] = scorecard_df['Sub-Metric'].apply(
            lambda x: re.sub('[^A-Za-z0-9]+', '', str(x)))
        new = scorecard_df['Date'].str.split(".", n=1, expand=True)
        scorecard_df['Date'] = new[0]
        scorecard_df['ID'] = np.arange(len(scorecard_df))
        scorecard_df['Network_Id'] = self.sc_user
        cols = scorecard_df.select_dtypes(['object']).columns
        scorecard_df[cols] = scorecard_df[cols].apply(
            lambda x: x.str.strip())
        scorecard_df['Load_Date'] = str(pd.Timestamp('now'))

        return scorecard_df

    @classmethod
    def get_static_scorecard_values(cls, scorecard_df, plant_name, year, file):
        """
        Function to fetch similar values of both Actual and Target file types
        :param scorecard_df: Initial dataframe input
        :param plant_name: Name of the plant
        :param year: Current Year
        :param file: type of file(Regional, actual and target)
        :return: Dataframe with static values
        """
        scorecard_df["Metric"].fillna(method='ffill', inplace=True)
        scorecard_df["Sub-Metric"].fillna(method='ffill', inplace=True)
        scorecard_df['Source Name'] = 'Excel_Daily_Scorecard'
        scorecard_df['Source Type'] = 'Scorecard'
        scorecard_df['Plant'] = plant_name
        scorecard_df['Year'] = year
        scorecard_df['Year'] = pd.to_numeric(scorecard_df['Year'])
        scorecard_df['Type (Actual/Planned)'] = file.split('(')[1].split(')')[0]
        scorecard_df['Actual'] = scorecard_df['Actual'].astype('str')

        return scorecard_df

    def get_scorecard_df(self, file, plant_name, read_file, column_transforms):
        """
        Function to create the dataframe for the excel file parsed
        :param file: type of file (Regional, Actual or Target)
        :param plant_name: Name of the plant
        :param read_file: initial dataframe input
        :param rename_cols: columns to be renamed
        :param cols_selected: columns to be selected
        :return: dataframe parsed from excel
        """

        try:
            new_df = None
            year = None
            target_dict = None

            var_name = None
            value_name = None

            if "Actual" in file:

                period = file.split('-')[1].split('-' + plant_name)[0]
                current_month = int(period.split('P')[1])

                if current_month >= 10:
                    current_month_YTD = 'P' + str(current_month) + ' YTD'
                else:
                    current_month_YTD = 'P0' + str(current_month) + ' YTD'

                period_end = read_file.columns.get_loc(current_month_YTD) + 1

                new_df = read_file.iloc[:, :period_end]
                target_dict = self.metric_column
                year = file.split('-')[0].split(') ')[1]
                var_name = "Date"
                value_name = "Actual"

            elif "Target" in file and 'Regional' not in file:
                new_df = read_file
                target_dict = self.metric_column_target
                year = (file.split('-')[0].split(')')[1]).strip()
                var_name = "Date"
                value_name = "Actual"
            elif "Regional" in file:
                new_df = read_file
                target_dict = self.metric_column_1
                var_name = "YTD_MTD"
                value_name = "KPI_VALUES"

            list_of_columns = new_df.columns

            date_columns = []
            for column in list_of_columns:
                # checking the date columns to be taken out from the
                # list of columns
                if 'Regional' in file:

                    if len(column) >= 7 and column != 'Sub-Metric':
                        date_columns.append(column)
                else:

                    if len(column) <= 7 and column != 'UOM' and column != 'Metric' \
                            and column != 'Sub-KPI' and 'Regional' not in file:
                        date_columns.append(column)

            application.logger.info("The number of columns in the {} file is {}".format(file, len(
                date_columns
            )))

            actual_df = new_df.loc[:, target_dict + date_columns].replace('[\n]',
                                                                          '',
                                                                          regex=True)
            actual_df.reset_index(drop=True, inplace=True)
            scorecard_df = actual_df.melt(id_vars=target_dict,
                                          value_vars=date_columns,
                                          var_name=var_name,
                                          value_name=value_name)

            if "Regional" not in file:
                scorecard_df = self.get_static_scorecard_values(scorecard_df=scorecard_df,
                                                                plant_name=plant_name,
                                                                year=year,
                                                                file=file)
                if "Actual" in file:
                    scorecard_df['Month No'] = \
                        scorecard_df['Date'].str.split("P", n=1, expand=True)[1]
                    scorecard_df['Month No'] = scorecard_df['Month No'].apply(
                        lambda x: re.sub('[^0-9]+', '', str(x)))

                    # removing characters from Month No column
                    scorecard_df['Month No'] = scorecard_df['Month No'].apply(
                        lambda x: x.zfill(2))

                    scorecard_df['Period'] = 'P' + scorecard_df['Month No'].astype(
                        str)
                    scorecard_df['Month No'] = pd.to_numeric(
                        scorecard_df['Month No'])
                    scorecard_df['Period'] = scorecard_df['Period'].map(
                        lambda x: x.strip())
                    scorecard_df['Period'] = np.where(
                        scorecard_df['Date'].str.contains("YTD"),
                        "YTD", scorecard_df['Period'])

                    scorecard_df['Month_sf'] = np.vectorize(self.get_key)(
                        self.month_dict_1,
                        scorecard_df['Month No'].astype(str))
                    scorecard_df['Month No'] = pd.to_numeric(
                        scorecard_df['Month No'])

                    scorecard_df['Month_lf'] = np.vectorize(self.get_key)(
                        self.month_dict_name,
                        scorecard_df['Month_sf'])
                    scorecard_df = scorecard_df[~scorecard_df.Date.str.contains('|'.join(['PD', 'WK']), case=False)]
                    scorecard_df = scorecard_df[scorecard_df['Actual'] != 'nan']
                    scorecard_df['Week'] = np.nan

                elif "Target" in file and 'Regional' not in file:
                    scorecard_df['Month No'] = \
                        scorecard_df['Date'].str.split("P", n=1, expand=True)[1]
                    scorecard_df['Month No'] = scorecard_df['Month No'].apply(
                        lambda x: re.sub('[^0-9]+', '', str(x)))

                    # removing characters from Month No column
                    scorecard_df['Month No'] = scorecard_df['Month No'].apply(
                        lambda x: x.zfill(2))

                    scorecard_df['Period'] = 'P' + scorecard_df['Month No'].astype(
                        str)
                    scorecard_df['Month No'] = pd.to_numeric(
                        scorecard_df['Month No'])
                    scorecard_df['Period'] = scorecard_df['Period'].map(
                        lambda x: x.strip())
                    scorecard_df['Period'] = np.where(
                        scorecard_df['Date'].str.contains("YTD"),
                        "YTD", scorecard_df['Period'])

                    scorecard_df['Month_sf'] = np.vectorize(self.get_key)(
                        self.month_dict_1,
                        scorecard_df['Month No'].astype(str))
                    scorecard_df['Month No'] = pd.to_numeric(
                        scorecard_df['Month No'])
                    scorecard_df['Week'] = np.nan
                    scorecard_df['Month_lf'] = np.vectorize(self.get_key)(
                        self.month_dict_name,
                        scorecard_df['Month_sf'])
                    scorecard_df = scorecard_df[scorecard_df['Actual'] != 'nan']

                scorecard_df = self.get_final_static_values(scorecard_df=scorecard_df,
                                                            plant_name=plant_name)

            else:

                scorecard_df['Function_Name'] = np.vectorize(self.get_key)(self.metric_dict,
                                                                           scorecard_df[
                                                                               'Sub-Metric'])
                drop_col1 = scorecard_df.index[
                    scorecard_df['Function_Name'] == 'None'].tolist()
                scorecard_df = scorecard_df.drop(
                    scorecard_df.index[drop_col1])

                new = scorecard_df['YTD_MTD'].str.split(" ", n=1,
                                                        expand=True)

                scorecard_df["YTD_MTD1"] = new[1]

                scorecard_df["Year"] = new[0]

                file_period = int(file.split('P')[1].split('-')[0])
                file_year = file.split('-')[0]
                event_dictionary = {
                    str(int(file_year) - 1) + " P" + str(
                        file_period) + " YTD": "Previous Year YTD",
                    str(int(file_year)) + " P" + str(
                        file_period) + " YTD": "Current Month YTD",
                    str(file_year) + " Target": "Target",
                    str(int(file_year)) + " P" + str(
                        file_period): "Actual"}

                scorecard_df['Data_Type'] = scorecard_df['YTD_MTD'].map(
                    event_dictionary)

                scorecard_df['YTD_MTD_2'] = scorecard_df['Data_Type'].str[-3:]
                scorecard_df['YTD_MTD_2'] = scorecard_df['YTD_MTD_2'].replace('ual', 'MTD')
                scorecard_df['YTD_MTD_2'] = scorecard_df['YTD_MTD_2'].replace('get', 'YTD')
                scorecard_df["YTD_MTD1"].replace(regex=True, inplace=True, to_replace=r'\D',
                                                 value=r'')

                scorecard_df['YTD_MTD1'] = "P" + scorecard_df['YTD_MTD1']

                scorecard_df['YTD_MTD1'] = scorecard_df['YTD_MTD1'].replace('P', 'YTD').replace(
                    'NULL',
                    'YTD')

                scorecard_df['Region'] = 'AMEA'
                scorecard_df['Current_Time'] = str(datetime.now())
                scorecard_df['Network_Id'] = self.sc_user
                scorecard_df = scorecard_df.rename(
                    {'Sub-Metric': 'KPI', 'YTD_MTD_2': 'YTD_OR_MTD',
                     'YTD_MTD1': 'Period'},
                    axis=1)
                scorecard_df = scorecard_df[scorecard_df['KPI'].notnull()]
                scorecard_df.reset_index(drop=True, inplace=True)
                scorecard_df['ID'] = np.arange(len(scorecard_df))
                scorecard_df['Year'] = pd.to_numeric(scorecard_df['Year'])

                scorecard_df.loc[scorecard_df['Data_Type'].str.contains('Target'),
                                 'Period'] = 'P' + str(file_period)

            scorecard_df = scorecard_df.rename(columns=column_transforms["rename_cols"])

            scorecard_df = scorecard_df[column_transforms["selected_cols"]]

            if 'Actual' in file:
                scorecard_df.replace(np.nan, 'NULL')

            return scorecard_df

        except Exception as exp_msg:
            application.logger.error(str(exp_msg))
            raise str(exp_msg)

    def read_daily_files(self):
        """
        Function to parse the excel files
        :return: Status of excel parser
        """
        # validating  user access
        data_frame, value = None, ''
        try:
            if self.sc_access == 'YES' or self.regional_access == 'YES':

                file_name_w_ext = os.path.basename(self.daily_file)
                stat_info = os.stat(self.daily_file)

                if stat_info.st_size > 0:
                    file, file_extension = os.path.splitext(file_name_w_ext)

                    application.logger.info("Name of the file is {} and it's "
                                            "extension is {}".format(file, file_extension))

                    sheets = ['Upload Sheet']

                    orig_plant_nm = list(self.plant_nm.split("~"))
                    plant_nm_1 = [x.lower() for x in orig_plant_nm]
                    self.plant_name_list = [plant.lower() for plant in self.plant_name_list]
                    for sheet in sheets:

                        skip_rows = 2 if 'Regional' in file else 1
                        application.logger.info("Reading the excel file as dataframe.")
                        read_file = pd.read_excel(self.daily_file, sheet_name=sheet,
                                                  skiprows=skip_rows)

                        list_1_sc = {col1 for col1 in read_file.columns if 'PD' in col1 or 'PD.' in
                                     col1}
                        list_2_sc = {col2 for col2 in read_file.columns if 'WK' in col2 or 'WK.' in
                                     col2}
                        list_1_am = {col1 for col1 in read_file.columns if
                                     'FY' in col1 or 'Target' in col1 or 'P' in col1}

                        if 'Actual' in file and list_2_sc.issubset(read_file.columns):
                            application.logger.info("File is of Actual type. Parsing the excel "
                                                    "for Actual type.")
                            if self.list_3_sc.issubset(read_file.columns) and list_1_sc.issubset(
                                    read_file.columns):

                                if self.sc_access == 'YES':

                                    plant_name = str(file.split('- AP')[0].split('-')[2]).replace(
                                        "_", " ").strip()

                                    if plant_name.lower() in plant_nm_1 and plant_name.lower() in self.plant_name_list:
                                        application.logger.info("Fetching the necessary values "
                                                                "for the dataframe")
                                        plant_name = orig_plant_nm[plant_nm_1.index(plant_name.lower())]
                                        scorecard_df = self.get_scorecard_df(file=file,
                                                                             plant_name=plant_name,
                                                                             read_file=read_file,
                                                                             column_transforms=
                                                                             self.column_transforms[
                                                                                 "Actual"]
                                                                             )
                                        data_frame = scorecard_df
                                        value = 'Scorecard'

                                        application.logger.info("Excel file {} parsed".format(file))
                                    elif plant_name.lower() in self.plant_name_list and not plant_name.lower() in plant_nm_1:
                                        application.logger.error("User {} does not have "
                                                                 "access to this plant".format(self.sc_user))
                                        data_frame, value = "User does not have access to this plant", \
                                                            "Scorecard"
                                    else:
                                        data_frame, value = 'Plant name is not valid in filename', \
                                                            'Scorecard'
                                else:

                                    data_frame, value = 'You don\'t have access for scorecard data', \
                                                        'Scorecard'
                            else:
                                data_frame, value = 'Scorecard format is not correct, ' \
                                                    'Please download the scorecard format ' \
                                                    'from above link', 'Scorecard'

                        elif 'Target' in file and self.list_4_target.issubset(read_file.columns) and 'Regional' not in file:
                            application.logger.info("File is of Target type. Parsing the excel "
                                                    "for Target type.")
                            if self.list_3_target.issubset(read_file.columns):
                                if self.sc_access == 'YES':

                                    plant_name = str(file.split('- AP')[0].split('-')[1]).replace(
                                        "_", " ").strip()

                                    if plant_name.lower() in plant_nm_1 and plant_name.lower() in self.plant_name_list:
                                        application.logger.info("Fetching the necessary values "
                                                                "for the dataframe")
                                        plant_name = orig_plant_nm[plant_nm_1.index(plant_name.lower())]
                                        scorecard_df = self.get_scorecard_df(file=file,
                                                                             plant_name=plant_name,
                                                                             read_file=read_file,
                                                                             column_transforms=
                                                                             self.column_transforms[
                                                                                 "Target"]
                                                                             )
                                        data_frame, value = scorecard_df, 'Scorecard'
                                        application.logger.info("Excel file {} parsed".format(file))
                                    elif plant_name.lower() in self.plant_name_list and not plant_name.lower() in plant_nm_1:
                                        application.logger.error("User {} does not have "
                                                                 "access to this plant".format(self.sc_user))
                                        data_frame, value = "User does not have access to this plant", \
                                                            "Scorecard"
                                    else:
                                        data_frame, value = 'Plant name is not valid in filename', \
                                                            'Scorecard'

                                else:

                                    data_frame, value = 'You don\'t have access for ' \
                                                        'scorecard data', 'Scorecard'

                            else:
                                data_frame, value = 'Scorecard format is not correct, Please ' \
                                                    'download the ' \
                                                    'scorecard format from above link', 'Scorecard'

                        # validating amea regional sheets
                        elif len(list_1_am) == 4 and 'Regional' in file and 'Monthly' in file:
                            application.logger.info("File is of Regional type. Parsing the excel "
                                                    "for Regional type.")

                            if list_1_am.issubset(read_file.columns):
                                if self.regional_access == 'YES':

                                    read_file.replace('', np.nan, inplace=True)
                                    read_file = read_file[
                                        read_file.columns.drop(list(read_file.filter(
                                            regex='Unnamed:')))]

                                    file_period = int(file.split('P')[1].split('-')[0])
                                    file_year = file.split('-')[0]

                                    column_1 = read_file.columns[3]

                                    column_1_yr = column_1.split(' ')[0]
                                    column_1_yr_1 = column_1.split(' ')[1]
                                    column_1_period = column_1_yr_1.split('P')[1]

                                    column_2 = read_file.columns[4]
                                    column_2_yr = column_2.split(' ')[0]
                                    column_2_yr_1 = column_2.split(' ')[1]
                                    column_2_period = column_2_yr_1.split('P')[1]

                                    column_3 = read_file.columns[5]
                                    column_3_yr = column_3.split(' ')[0]

                                    # validating amea regional structure
                                    if (str(column_1_yr) == str(file_year) and
                                            str(column_2_yr) == str(file_year) and
                                            str(column_3_yr) == str(file_year)):

                                        if (str(column_1_period) == str(column_2_period) and
                                                str(column_2_period) == str(file_period)):

                                            application.logger.info("Fetching the necessary values "
                                                                    "for the dataframe")

                                            scorecard_df = self.get_scorecard_df(file=file,
                                                                                 plant_name=None,
                                                                                 read_file=
                                                                                 read_file,
                                                                                 column_transforms=
                                                                                 self.column_transforms[
                                                                                     "Regional"]
                                                                                 )

                                            data_frame, value = scorecard_df, 'Regional'
                                            application.logger.info(
                                                "Excel file {} parsed".format(file))
                                        else:
                                            data_frame, value = 'Periods are not matching as per ' \
                                                                'current period', \
                                                                'Regional'
                                    else:
                                        data_frame, value = 'Year value is different from current ' \
                                                            'year', 'Regional'
                                else:
                                    data_frame, value = 'You don\'t have access for regional data', \
                                                        'Regional'

                            else:
                                data_frame, value = 'Scorecard format is not correct, Please ' \
                                                    'download the scorecard format from above link', \
                                                    'Regional'
                        elif 'Regional' in file and 'Annually' in file:
                            application.logger.info("Processing Regional Annual file")
                            df = pd.DataFrame()
                            period_columns = [
                                'P1',
                                'P2',
                                'P3',
                                'P4',
                                'P5',
                                'P6',
                                'P7',
                                'P8',
                                'P9',
                                'P10',
                                'P11',
                                'P12'
                            ]
                            kpi_value_list = []
                            kpi_name_list = []
                            period_list = []
                            for period in period_columns:
                                kpi_value_list.extend(read_file[period])
                                kpi_name_list.extend(read_file['Sub-Metric'])
                                period_list.extend([period] * len(read_file[period]))
                            try:
                                application.logger.info(f"Processing {file}")
                                df['KPI_NAME'] = kpi_name_list
                                df['KPI_VALUES'] = kpi_value_list
                                df['PERIOD'] = period_list
                                df['YTD_or_MTD'] = ['YTD']*len(period_list)
                                df['YEAR'] = ([file.split('-')[0]] * len(period_list))
                                df['DATA_TYPE'] = ['Target'] * len(period_list)
                                df['CURR_TIME'] = [datetime.today()]* len(period_list)
                                df['NETWORK_ID'] = [self.sc_user] * len(period_list)
                                df['REGION_NAME'] = ['AMEA'] * len(period_list)
                                df['ID'] = np.arange(len(df))
                                df['FUNCTION_NAME'] = np.vectorize(self.get_key)(self.metric_dict, df['KPI_NAME'])
                                df = df[['ID', 'REGION_NAME', 'FUNCTION_NAME', 'KPI_NAME',
                                        'KPI_VALUES', 'YTD_or_MTD', 'YEAR', 'PERIOD',
                                        'DATA_TYPE', 'CURR_TIME', 'NETWORK_ID']]
                                df = df[df['KPI_VALUES'].notna()]
                                data_frame, value = df, 'Regional'
                            except Exception as e:
                                application.logger.log("Exception occured")
                                if e:
                                    application.logger.log(e)
                        else:
                            data_frame, value = 'File format is not correct, Please download ' \
                                                'the scorecard format from above link', 'Both'
                else:
                    data_frame, value = 'File size is less than 0 KB', 'Regional'

            else:
                data_frame, value = 'You don\'t have access for regional data and Scorecard', 'Both'

            return data_frame, value

        except ValueError as value_error:
            application.logger.error(str(value_error))
        except IndexError as index_error:
            application.logger.error(str(index_error))
        except Exception as exp_msg:

            if self.sc_access == 'YES' and self.regional_access == 'YES':
                data_frame, value = 'Please upload correct Scorecard or Regional data File', 'Both'
            elif self.sc_access == 'NO' and self.regional_access == 'YES':
                data_frame, value = 'Please upload correct Regional data File', 'Both'
            elif self.sc_access == 'YES' and self.regional_access == 'NO':
                data_frame, value = 'Please upload correct Scorecard File', 'Both'
            application.logger.error(data_frame)
            application.logger.error(str(exp_msg))
            return data_frame, value
