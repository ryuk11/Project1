# -*- coding: utf-8 -*-
"""
This process read the converted csv scorecard and Yield SOL files from the respective source location
get the required columns ,do the data cleansing and transposition and finally store the final file in
the output location.
"""

# imports all the packages needed for the program
import os
from io import BytesIO, StringIO
from datetime import date, datetime
import sys
import pandas as pd
import time
from dateutil.parser import parse
import glob
import numpy as np
import re as re

MetricColumn = ['Sub-Metric', 'UOM', 'New_Target']

# Creating dictionary for Month Values
month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
              'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
              'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
              'YTD': 'YTD', 'Pre': 'Pre YTD'
              }

# creating dictionary for month Names
month_dict_name = {'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
                   'May': 'May', 'June': 'June', 'July': 'July', 'August': 'August',
                   'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec',
                   'YTD': 'YTD', 'Previous YTD': 'Pre YTD'
                   }


# Get the list of scorecard files from the input location
def get_list_of_files_sc(input_location_sc):
    input_files = [f for f in os.listdir(input_location_sc) if not f.startswith('~')]
    return input_files


# Get the list of yield sol files from the input location
def get_list_of_files_sol(input_location_sol):
    files = [f for f in os.listdir(input_location_sol) if not f.startswith('~')]
    return files


def write_csv_df(outputpath, df):
    pathfile = os.path.normpath(outputpath)
    # Use this function to search for any files which match your filename
    files_present = os.path.isfile(pathfile)
    # if no matching files, write to csv, if there are matching files, print statement
    if not files_present:
        df.to_csv(pathfile, index=False, sep=',', header=True, encoding='utf-8-sig')
    elif files_present:
        df.to_csv(pathfile, index=False, sep=',', header=True, encoding='utf-8-sig')
    else:
        print("Not a valid input. Data is NOT saved!\n")

#test~alex_scorecard.csv
#test~cairo_functional_scorecard.csv
#2021-P02-Cairo - Asia Pacific Plant Supply Chain Metrics Functional Scorecard.xlsx
# Reading input csv files for scorecards
def read_csv_files(input_location_sc, file, input_location_property, output_location,output_location_err):
#def read_csv_files(input_location_sc, file, output_location):
 
    plant_name = ''
    plant_name = file.split('~')[1].split('_scorecard')[0]
    print(plant_name)

    global get_current_period
    get_current_period = file.split('-p')[1].split('-')[0]
    #print(get_current_period)

    global get_current_month_no
    get_current_month_no=int(get_current_period)
    
    
    get_current_month=get_key(get_current_period)
    print("Current Month : " + get_current_month)


    global  Year
    Year = file.split('-p')[0]
    Year2 = int(Year) - 1
    Period = int(re.search(r'\d+', file.split('-')[1]).group())
    last_character_year = Year[-2:]
    #print(last_character_year)
    last_character_pre_year = int(last_character_year) - 1
    #print(last_character_pre_year)

    get_month_column=get_current_month+'-'+last_character_year
    print(get_month_column)

    # Reading property file
    readFile = pd.read_csv(os.path.join(input_location_sc, file), encoding='utf-8', sep=',',skiprows=1,
                           na_values=['#REF!'])
    read_property = pd.read_csv(os.path.join(input_location_property, 'all_plant_dim_data.csv'),encoding='utf-8',
                               sep=',')
    read_property['KPI'] = read_property['KPI'].apply(lambda x: re.sub('[^A-Za-z0-9]+', '', str(x)))
    read_property['Plant'] = read_property['Plant'].str.lower()

    print('Reading csv file for ' + plant_name + ' plant')
    print('Processing scorecard data')

    Targetcolumn = readFile.filter(regex='Target', axis=1)  # getting target column
    readFile['New_Target'] = Targetcolumn

    readFile = readFile[readFile['Sub-Metric'].notnull()]  # remove blank rows from the file
    readFile.drop(readFile[readFile['Sub-Metric'] == 'YIELD REPORT'].index,
                  inplace=True)  # removing extra rows in botany plant
    readFile.drop(readFile[readFile['Sub-Metric'] == 'Production SAP 101 & 102'].index, inplace=True)
    readFile.drop(readFile[readFile['Sub-Metric'].str.contains('SAP data')].index, inplace=True)

    print(get_month_column)
    month_column1=readFile.columns.get_loc(get_month_column)

    month_column2 = month_column1 - 1
    print(month_column1)
    print(month_column2)
	
	#getting current and previous month
	
    month_column = readFile.iloc[:, [month_column2, month_column1]]  # getting target column
    print(month_column)
	

    date_columns = month_column

    list_of_columns = readFile.columns
    rolling = [col for col in list_of_columns if 'rolling' in col]
    print(rolling)

    date_col_names_TG2 = [s for s in date_columns]
    date_col_names_TG = date_col_names_TG2 + rolling
    print(date_col_names_TG)


    # Creating dataframe with required date columns and metrics of current year
    actual_df = readFile.loc[:, MetricColumn + date_col_names_TG].replace('[\n]', '', regex=True)
    actual_df.reset_index(drop=True, inplace=True)
    scorecard_df11 = actual_df.melt(id_vars=MetricColumn, value_vars=date_col_names_TG,var_name='Date',
                                    value_name='Actual')

    scorecard_df = scorecard_df11
    scorecard_df.loc[scorecard_df['Date'].str.contains('YTD'), 'Date'] = 'YTD'

    scorecard_df['Year'] = scorecard_df['Date'].apply(lambda x: "20" + x[4:])
    scorecard_df.loc[scorecard_df['Date'].str.contains('YTD'), 'Year'] = Year
    scorecard_df['Month Name(SF)'] = scorecard_df['Date'].apply(lambda x: x[:3])
    scorecard_df['Period'] = scorecard_df['Date'].apply(lambda x: "P" + month_dict[x[0:3]])
    scorecard_df['Period'] = scorecard_df['Period'].replace('PYTD', 'YTD', regex=True)
    scorecard_df['Month No'] = scorecard_df['Date'].apply(lambda x: month_dict[x[0:3]])

   # scorecard_df.loc[~scorecard_df['Date'].str.contains('YTD'), 'Date'] = "".join(date_col_names_TG2)
    scorecard_df['Plant'] = plant_name
    scorecard_df['Plant'] = scorecard_df['Plant'].replace('_', ' ', regex=True)

    scorecard_df['Month No'] = scorecard_df['Month No'].replace('YTD', 0)
    scorecard_df.loc[(scorecard_df['Date'] == 'YTD') & (scorecard_df['Year'] == Year), 'Month No'] = Period
    scorecard_df['Sub KPI'] = ' '
    scorecard_df['Source Name'] = 'Excel_Scorecard'
    scorecard_df['Source Type'] = 'Scorecard'

    Sub_Category = ''
    Category = ''

    if plant_name == 'rayong_snacks':
        Sub_Category = 'Wholesome'
        Category = 'Snacks'

    elif plant_name in ('ernstek', 'enstek'):
        Sub_Category = 'Salty'
        Category = 'Snacks'

    else:
        Sub_Category = 'RTEC'
        Category = 'Cereal'

    scorecard_df['Category'] = Category
    scorecard_df['Sub_Category'] = Sub_Category

    final_scorecard_df = scorecard_df.rename({'New_Target': 'Target'}, axis=1)

    final_scorecard_df['Month Name(LF)'] = np.vectorize(get_key1)(final_scorecard_df['Month Name(SF)'])
    final_scorecard_df['Sub-Metric'] = final_scorecard_df['Sub-Metric'].apply(
        lambda x: re.sub('[^A-Za-z0-9]+', '', str(x)))
    read_property1 = read_property[['Plant', 'Function_Name', 'KPI','UOM']]

    read_property11 = read_property1.rename({'Function_Name': 'Metric', 'KPI': 'Sub-Metric'}, axis=1)
    final_scorecard_df1 = pd.merge(final_scorecard_df, read_property11, how='left',
                                   on=['Sub-Metric', 'Plant','UOM'])  # joining with property file to get metric values
    	
       
    #final_scorecard_df1.drop(final_scorecard_df1.loc[(final_scorecard_df1['Metric']=='Natural Resource Conservation') & (final_scorecard_df1['Date'] != get_month_column)],inplace=True)
   
    final_scorecard=final_scorecard_df1.drop(final_scorecard_df1[(final_scorecard_df1['Metric']!='Natural Resource Conservation') & 
                              (final_scorecard_df1['Date'] != get_month_column) & (final_scorecard_df1['Period'] != 'YTD')].index)
    
    final_scorecard['Load_Date'] = datetime.now().date()
    file1=(file.split('~')[0].replace('_-_','-')).upper()
    file_name=(file1+"_SC_UPLOAD_LOG_"+str(datetime.now()))
    print(file_name)
    print(final_scorecard.dtypes)

#2021-P02-Cairo - Asia Pacific Plant Supply Chain Metrics Functional Scorecard.xlsx



    print('***************************Incorrect KPI Name or UOM *****************************')

    print(final_scorecard['Metric'].isnull().values.any())
    print(final_scorecard['Target'].astype(str).str.contains(',').any())
    print(final_scorecard['Actual'].astype(str).str.contains(',').any())
     
    
    if final_scorecard['Actual'].astype(str).str.contains(',').any() or final_scorecard['Target'].astype(str).str.contains(',').any() or  final_scorecard['Metric'].isnull().values.any():   
        Error_result1=final_scorecard.loc[final_scorecard['Target'].astype(str).str.contains(',' ,na=False), ['Sub-Metric','UOM','Plant','Year','Period']]
        Error_result1['Error_description']='Actual contains comma in values.Please advise Plant Metric Owner to correct accordingly.'
        Error_result2=final_scorecard.loc[final_scorecard['Actual'].astype(str).str.contains(',' ,na=False), ['Sub-Metric','UOM','Plant','Year','Period']]
        Error_result2['Error_description']='Actual contains comma in values.Please advise Plant Metric Owner to correct accordingly.'
        Error_result3=final_scorecard.loc[final_scorecard['Metric'].isnull(),['Sub-Metric','UOM','Plant','Year','Period']]
        Error_result3['Error_description']='Either KPI name or UOM value is incorrect.Please advise Plant Metric Owner to correct accordingly.'
        Error_result=Error_result1.append([Error_result2,Error_result3])
        Error_result['File_name']=file
        Error_result['Load_date']=datetime.now()
        print(Error_result)
        #file_name=(str(Year)+"_"+str(file.split('-')[1])+"_"+plant_name+"_SC_UploadLog_"+str(datetime.now()))

        file1=(file.split('~')[0].replace('_-_','-')).upper()
        file_name=(file1+"_SC_UPLOAD_LOG_"+str(datetime.now()))
        print(file_name)
        #write_csv_df(os.path.join(output_location_err, file_name + ".csv"), Error_result)
        write_csv_df(os.path.join(output_location_err, file_name + ".csv"), Error_result)

        
    else:  
        print("All KPI ,UOM , Actual and Target values are getting matched successfully.")
        return final_scorecard


def get_key1(value):
    for i in month_dict_name.keys():
        if value in month_dict_name[i]:
            return i

def get_key(val):
    for key, value in month_dict.items():
         if val == value:
             return key
  



# Reading input csv files for yield sols

def creating_sol_file(input_location_sol, sheet, input_location_property, output_location, output_location_err):
    print('Processing Yield sol data')
    Data = pd.read_csv(os.path.join(input_location_sol, sheet), encoding='utf-8', sep=',', skiprows=14,
                       na_values=['#VALUE!', '#DIV/0!', '#REF!'])
    Data = Data[Data.columns.drop(list(Data.filter(regex='Unnamed:')))]


    read_property = pd.read_csv(os.path.join(input_location_property, 'all_plant_dim_data.csv'),encoding='utf-8',
                               sep=',')
    read_property['KPI'] = read_property['KPI'].apply(lambda x: re.sub('[^A-Za-z0-9]+', '', str(x)))
    read_property['Plant'] = read_property['Plant'].str.lower()

    Data_list = list(Data.columns)  # creating list for column names

    unwanted_col = {'Month', 'Yield SOLs', 'Remark', 'Unnamed: 14', 'Swee Remark (P3)', 'Swee remark (P3)',
                    'Unnamed: 16'}
    Data_list = [ele for ele in Data_list if ele not in unwanted_col]

    for smetric_col in Data_list:
        Data1 = Data[['Month', 'Yield SOLs', smetric_col]].assign(SM=smetric_col)
        Data1["Month"].fillna(method='ffill', inplace=True)

        #if smetric_col == "Target Yield (%)":
           # Data1[smetric_col].fillna(method='ffill', inplace=True)

        #Data1 = Data1.assign(Metric='Yield Source of Loss')


        # getting plant name from yield sol file

        plant_name = ''
        plant_name = sheet.split('~')[1].split('_yield')[0]
        # print(plant_name)

        UOM = ''
        UOM = smetric_col.split('(')[1].split(')')[0]

        Data1 = Data1.rename({smetric_col: 'Actual', 'SM': 'Sub-Metric', 'Yield SOLs': 'Sub KPI'}, axis=1)
        Data1.drop(
            Data1[Data1.Month == 'Additional Drill Down Data/Information for Reporting month can be added below'].index,
            inplace=True)
        Data1 = Data1.rename({'Month': 'Period'}, axis=1)

        Data1['Plant'] = plant_name
        Data1['Plant'] = Data1['Plant'].replace('_', ' ', regex=True)
        Data1['UOM'] = UOM
        Data1['Target'] = ' '
        Data1['Year'] = sheet.split('-p')[0]
        Data1['Source Name'] = 'Excel_YieldSOL'
        Data1['Source Type'] = 'Scorecard'
        Data1['Sub-Metric'] = Data1['Sub-Metric'].apply(lambda x: re.sub('[^A-Za-z0-9]+', '', str(x)))

        read_property1 = read_property[['Plant', 'Function_Name', 'KPI','UOM']]

        read_property11 = read_property1.rename({'Function_Name': 'Metric', 'KPI': 'Sub-Metric'}, axis=1)
        Data2 = pd.merge(Data1, read_property11, how='left',
                                  on=['Sub-Metric', 'Plant','UOM'])  # joining with property file to get metric values
        #print(Data2)

        cols1 = Data2.select_dtypes(['object']).columns
        Data2[cols1] = Data2[cols1].apply(lambda x: x.str.strip())
        Yield.append(Data2)
        
        continue

        return Data2


if __name__ == '__main__':
    try:

        Yield = []
        main_df_list = []
        
        input_location_sc = sys.argv[1]
        input_location_sol = sys.argv[2]
        input_location_property = sys.argv[3]
        output_location = sys.argv[4]
        output_location_err = sys.argv[5]
        
        print('Execution of Scorecard Parsing started')
        
        for file in get_list_of_files_sc(input_location_sc):
            statinfo = os.stat(os.path.join(input_location_sc, file))
            if ((os.path.join(input_location_sc, file)).endswith('.csv') and statinfo.st_size > 0):
                main_df_list.append(read_csv_files(input_location_sc, file, input_location_property, output_location,output_location_err))
                #main_df_list.append(read_csv_files(input_location_sc, file, output_location))
            else:
                print(file[:] + ' file extension is not .csv , Hence Data is Not Processed afterwards')
        
        final_df_sc = pd.concat(main_df_list)[
            ['Plant', 'Category', 'Sub_Category', 'Metric', 'Sub-Metric', 'Sub KPI', 'UOM', 'Date', 'Year', 'Period',
            'Month No', 'Month Name(SF)', 'Month Name(LF)', 'Actual', 'Target', 'Load_Date', 'Source Name', 'Source Type']]
        final_df_sc.loc[~final_df_sc['Date'].str.contains('YTD'), 'Date'] = '15-' + final_df_sc.loc[
            ~final_df_sc['Date'].str.contains('YTD'), 'Date']
        # write_csv_df(os.path.join(output_location, "only_scorecard_yieldsol_merged" + ".csv"), final_df_sc)
        
        for sheet in get_list_of_files_sol(input_location_sol):
            statinfo = os.stat(os.path.join(input_location_sol, sheet))
            if ((os.path.join(input_location_sol, sheet)).endswith('.csv') and statinfo.st_size > 0):
                Yield.append(creating_sol_file(input_location_sol, sheet,input_location_property, output_location,output_location_err))
            else:
                print(sheet[:] + ' file extension is not .csv , Hence Data is Not Processed afterwards')
        
        final_df_sol = pd.concat(Yield)[
            ['Plant', 'Source Name', 'Source Type', 'Metric','Sub-Metric', 'Sub KPI', 'UOM', 'Target','Actual', 'Period',
            'Year']]
        
        final_df_sc1 = final_df_sc[
            ['Date', 'Period', 'Year', 'Plant', 'Category', 'Sub_Category', 'Month No', 'Month Name(SF)',
            'Month Name(LF)', 'Load_Date']]
        
        final_df_sol = final_df_sol[final_df_sol['Sub KPI'].notnull()]
    
        # Adding year and date column to yield df from scorecaed based on month and plant	    
        Yield1 = pd.merge(final_df_sol, final_df_sc1, how='inner', on=['Plant', 'Period',
                                                                    'Year'])  
        Yield2 = Yield1.drop_duplicates()	           
        Yield2=Yield2[(Yield2['Month No']==(get_current_period)) | (Yield2['Month Name(SF)']== 'YTD')]
            
            
        Yield2 = Yield2[
            ['Plant', 'Category', 'Sub_Category',  'Metric','Sub-Metric', 'Sub KPI', 'UOM', 'Date', 'Year', 'Period',
            'Month No', 'Month Name(SF)', 'Month Name(LF)', 'Actual', 'Target', 'Load_Date', 'Source Name', 'Source Type']]
        
        print('Creating output with both scorecard and yield sol data')
        
    
        if Yield2['Actual'].astype(str).str.contains(',').any() or  Yield2['Metric'].isnull().values.any():
            plant_name1=Yield2.loc[Yield2['Actual'].astype(str).str.contains(',' ,na=False), ['Plant']]
            Error_result2=Yield2.loc[Yield2['Actual'].astype(str).str.contains(',' ,na=False), ['Metric','Sub-Metric', 'Sub KPI','UOM','Plant','Year','Period']]
            Error_result2['Error_description']='Actual contains comma in values.Please advise Plant Metric Owner to correct accordingly.'
            Error_result3=Yield2.loc[Yield2['Metric'].isnull(),['Metric','Sub-Metric', 'Sub KPI','UOM','Plant','Year','Period']]
            Error_result3['Error_description']='Either KPI name or UOM value is incorrect.Please advise Plant Metric Owner to correct accordingly.'
            Error_result=Error_result2.append([Error_result3])
            Error_result['File_name']=file
            Error_result['Load_date']=datetime.now()
            #file_name=(str(Year)+"_"+str(file.split('-')[1])+"_"+"yield_sol"+"_SC_UploadLog_"+str(datetime.now()))
            file1=(file.split('~')[0].replace('_-_','-')).upper()
            file_name=(file1+"_SC_UPLOAD_LOG_"+str(datetime.now()))
            print('Incorrect kpi  in yield sol file')
            print(Error_result) 
            write_csv_df(os.path.join(output_location_err, file_name + ".csv"), Error_result)
            #Error_result2.to_csv("/home/inka1j05/vijaybck/haima/gr55/"+file_name+".csv",index=False)
    
        
        else:
            merged_data = pd.concat([final_df_sc, Yield2], ignore_index=True)
        
            merged_data.columns = merged_data.columns.str.replace(r"[ .-]", "_")
            merged_data.columns = [x.lower() for x in merged_data.columns]
            print('final data is placed  output location')	    
            print('Python code completed successfully')
        
            write_csv_df(os.path.join(output_location, "scorecard_yieldsol_merged" + ".csv"), merged_data)
    
    
    except:
        print('Error Occured')
