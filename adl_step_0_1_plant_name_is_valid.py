import pandas as pd
import os, re, sys

def plant_is_invalid(property_file_location, sc_name):
    plant = str(sc_name.split("-")[2]).lower().strip()
    read_property = pd.read_csv(os.path.join(property_file_location, 'all_plant_dim_data.csv'),encoding='utf-8',sep=',',engine='python')
    #print(plant)
    #print(list(map(lambda plant_name: plant_name.lower().strip(),read_property['Plant'].unique())))
    if plant not in list(map(lambda plant_name: plant_name.lower().strip(),read_property['Plant'].unique())):
        return True, plant
    else:
        return False, plant


if __name__ == '__main__':
    input_property_file_location = sys.argv[1]
    input_sc_file_name = sys.argv[2]
       
    #Check file pattern
    #file_pattern = re.search(r"^(\d+)-P(\d{2})-([A-Za-z0-9_ ]+)-([A-Za-z ]+)(\..*$)",input_sc_file_name.replace(' ',''))
    file_pattern = re.search(r"^(\d{4})-P(\d{2})-([A-Za-z0-9_ ]+)-([A-Za-z ]+)(\..*$)",input_sc_file_name.replace(' ',''))
    if file_pattern: 
        result, plant_name = plant_is_invalid(input_property_file_location,input_sc_file_name)
        if result:
            sys.exit('Invalid plant name : {}'.format(plant_name))
        else:
            print('File name format and plant name {} is valid'.format(plant_name))
    else:
        sys.exit('{} : File name format is invalid'.format(input_sc_file_name))

