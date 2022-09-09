#!/usr/bin/python

'''
convert_CSBP_to_AM.py

A script to convert CSBP metadata sheets to AM format

Usage:
python convert_CSBP_to_AM.py

    > Follow the instructions issued by the script and enter the required path/filename information at the prompts 

This script has been tested using on:
    - windows powershell 7 (x64), python version 3.9.13
    - macOS 10.15.7, python version 3.7.3
    - Linux 5.3.18-150300.59.63, python version 3.9.4
Note: The pip or conda installation of the optional dependency 'xlrd' may be required
        e.g., `pip install xlrd`
'''

import pandas as pd
import numpy as np
import glob
import os

def formatIDs(df):
    #make sure sample_id column is set as a string (if IDs are short form then it may be a number)
    df['sample_id'] = df['sample_id'].astype(str)
    #Check Sample ID format
    id_prefix="102.100.100/"
    #these are known variations of badly formatted prefixes found on CSBP sheets
    badIDs = ['100/','102-100-100/','102.100.100.','102.100..100']
    for ele in badIDs:
        df['sample_id'] = df['sample_id'].str.replace('^' + ele, id_prefix, regex=True)
    #Reset the ID list incase there were any changes made
    IDs = df['sample_id'].tolist()
    for i in df.index:
        ID = df.loc[i, 'sample_id']
        #If the correct prefix is not present we will add it, and the ID flag for manual checking
        if id_prefix not in ID:
            fixedID = id_prefix + ID
            df.loc[i, 'sample_id'] = fixedID

print("\t*** CSBP to Australian Microbiome (AM) metadata converter ***\n")
print("This script will convert SOIL and Water CSBP excel files to a format compliant with the AM Database.")
print("Before you start, make sure:")
print("\t1) The CSBP sheet retains its original formatting (No deleted or renamed columns)")
print("\t2) All non-AM samples are deleted from the sheet\n")
print("The script will: ")
print("\t1) Convert CSBP units to AM units for the following:")
print("\t\tWater - Ammonium Nitrogen (mg/L N) to ammonium in umol/l N")
print("\t\tWater - Nitrate Nitrogen (mg/L N) to nitrate_nitrite in umol/l N")
print("\t\tWater - Conductivity (dS/m) to conductivity_aqueous in S/m")
print("\t2) Add standard AM method numbers for each analysis (If using a non-standard AM/CSBP analysis do not use this script)")
print("\t3) Save your file(s) as a AM *_UPDATE.xlsx file")
print("\n NOTE: This script will delete DEPTH values entered on the CSBP sheet. Ensure this information is included in your AM submission sheet.")

print("\n Output files will be saved to the same path as the input files")
print(" Do you want to convert multiple files or a single file?")
print("\tEnter 1 for multiple files (non-CSBP sheets will be ignored)")
print("\tEnter 2 for a single file")
user_choice =''
user_choice = input("Enter 1 or 2: ")

if user_choice == '1':
    filePath = input("Enter the path where files are located (hit enter if in the current directory): ")
    suffix = "*.xl*"
    search_files = os.path.join(filePath,suffix)
    print(search_files)

if user_choice == '2':
    search_files = input("Drag and drop the file to be converted or enter its path/name: ")
    #dragged and dropped paths may be in quotes or have trailing linebreaks/whitespace, so we will strip them
    search_files = search_files.replace("\"",'').rstrip()
    os.path.normpath(search_files)
    print(search_files)
filenames = glob.glob(search_files)

#define known header format of CSBP Soil and water analysis files. Note these names are stripped of trailing whitespace
known_water_cols = ['Lab Number', 'Unnamed: 1', 'Name', 'Unnamed: 3', 'Code', 'Customer', 'Ammonium Nitrogen', 'Nitrate Nitrogen', 'Unnamed: 8', 'Boron', 'Sodium', 'Magnesium', 'Phosphorous', 'Sulfur', 'Chloride', 'Potassium', 'Calcium', 'Manganese', 'Iron', 'Copper', 'Zinc', 'Bicarb', 'Carbonate', 'Conductivity', 'pH']
known_soil_cols = ['Lab Number', 'Unnamed: 1', 'Name', 'Unnamed: 3', 'Code', 'Customer', 'Depth', 'Colour', 'Unnamed: 8', 'Gravel', 'Texture', 'Ammonium Nitrogen', 'Nitrate Nitrogen', 'Phosphorus Colwell', 'Potassium Colwell', 'Sulfur', 'Organic Carbon', 'Conductivity', 'pH Level (CaCl2)', 'pH Level (H2O)', 'DTPA Copper', 'DTPA Iron', 'DTPA Manganese', 'DTPA Zinc', 'Exc. Aluminium', 'Exc. Calcium', 'Exc. Magnesium', 'Exc. Potassium', 'Exc. Sodium', 'Boron Hot CaCl2', 'Total Nitrogen', '% Clay', '% Course Sand', '% Fine Sand', '% Sand', '% Silt']

for filename in filenames:
    #set file identifier flags for incoming file
    water_file = False
    soil_file = False
    #check if csbp headers are present if not we will skip the file, if it is we will read it in gain skipping them
    data = pd.read_excel(filename)
    if set(['Customer']).issubset(data.columns):
        #skip the first 3 rows of the CSPB header
        data = pd.read_excel(filename, skiprows=3,dtype='str')
        #drop row at index 0 as it contains units
        data = data.drop([data.index[0]]).reset_index(drop=True)
        #remove any trailing whitespace from the incoming column names
        data.columns = data.columns.str.rstrip()
        #list incoming columns to check if the incoming file meets known CSBP SOIL or Water analysis files and format appropriately      
        incoming_cols = data.columns.tolist()
        
        #Lets do some preformatting
        #convert txt nulls to numpy nan - we will drop any extra columns containing all nan
        data.replace(['None', 'nan'], np.nan, inplace=True)
        data.dropna(axis=1, how='all', inplace=True)
        #Drop known unused columns
        drops= ['Lab Number', 'Code','Customer']
        data.drop(drops,axis=1,inplace=True)
        
        #Check if its a water or soil file and process appropriately
        ############ WATER Files ############
        if len(set(known_water_cols).difference(set(incoming_cols))) > 0:
            #set a flag and move on 
            water_file = False
        else:
            print("\nProcessing water file: " + filename)
            water_file = True
            #make a output filename
            file, file_extension = os.path.splitext(filename)
            outfile=filename.replace(file_extension, "_AM_WATER_format_UPDATE.xlsx")
            print("File will be saved as: " + outfile)
            
            #define Water columns that need to be converted to AM units
            convert_cols = ['Ammonium Nitrogen','Nitrate Nitrogen','Conductivity']
            #define molecular weights
            N_mw = 14.006720
            for col in convert_cols:
                print("Converting: " + col)
                for i in data.index:
                    if 'Ammonium Nitrogen' == col:
                        inVal = data.loc[i,col]
                        if "<" in str(inVal) or ">" in str(inVal) or pd.isnull(inVal):
                            data.loc[i,'ammonium'] = data.loc[i,col]
                        else:
                            data.loc[i,'ammonium'] = (float(inVal)*1000)/N_mw
                    if 'Nitrate Nitrogen' == col:
                        inVal = data.loc[i,col]
                        if "<" in str(inVal) or ">" in str(inVal) or pd.isnull(inVal):
                            data.loc[i,'nitrate_nitrite'] = data.loc[i,col]
                        else:
                            data.loc[i,'nitrate_nitrite'] = (float(inVal)*1000)/N_mw
                    if 'Conductivity' == col:
                        inVal = data.loc[i,col]
                        if "<" in str(inVal) or ">" in str(inVal) or pd.isnull(inVal):
                            data.loc[i,'conductivity_aqueous'] = data.loc[i,col]
                        else:
                            data.loc[i,'conductivity_aqueous'] = float(inVal)/10
            #drop the columns once they have been converted
            data.drop(convert_cols, axis=1, inplace=True)
            
            #Convert the headers to AM format fields using the dictionary of known headings
            column_dictionary = {'Name':'sample_id','ammonium':'ammonium','nitrate_nitrite':'nitrate_nitrite','conductivity_aqueous':'conductivity_aqueous','Boron':'icp_te_boron','Sodium':'sodium','Magnesium':'magnesium','Phosphorous':'icp_te_phosphorus','Sulfur':'icp_te_sulfur','Chloride':'chloride','Potassium':'potassium','Calcium':'icp_te_calcium','Manganese':'icp_te_manganese','Iron':'icp_te_iron','Copper':'icp_te_copper','Zinc':'icp_te_zinc','Bicarb':'bicarbonate','Carbonate':'carbonate','pH':'ph'}
            data.columns = data.columns.to_series().map(column_dictionary)
            
            #Define the ouput columns and fill for CSBP water methods columns
            column_order = ['sample_id']
            analysis_columns = ['ammonium', 'bicarbonate', 'carbonate', 'chloride', 'conductivity_aqueous', 'icp_te_boron', 'icp_te_calcium', 'icp_te_copper', 'icp_te_iron', 'icp_te_manganese', 'icp_te_phosphorus', 'icp_te_sulfur', 'icp_te_zinc', 'magnesium', 'nitrate_nitrite', 'ph', 'potassium', 'sodium']
            method_number = "2.1"
        
        ############ SOIL Files ############
        if len(set(known_soil_cols).difference(set(incoming_cols))) > 0:
            #set a flag and move on 
            soil_file = False
        else:
            print("\nProcessing soil file: " + filename)
            soil_file = True
            #make output filename
            file, file_extension = os.path.splitext(filename)
            outfile=filename.replace(file_extension, "_AM_SOIL_format_UPDATE.xlsx")
            print("File will be saved as: " + outfile)
            
            #Convert the headers to AM format fields using the dictionary of known headings. column headers stripped of trailing whitespace
            column_dictionary = {'Name': 'sample_id', 'Depth': 'depth', 'Colour': 'color', 'Gravel': 'gravel', 'Texture': 'texture', 'Ammonium Nitrogen': 'ammonium_nitrogen_wt', 'Nitrate Nitrogen': 'nitrate_nitrogen', 'Phosphorus Colwell': 'phosphorus_colwell', 'Potassium Colwell': 'potassium_colwell', 'Sulfur': 'sulphur', 'Organic Carbon': 'organic_carbon', 'Conductivity': 'conductivity', 'pH Level (CaCl2)': 'ph', 'pH Level (H2O)': 'ph_solid_h2o', 'DTPA Copper': 'dtpa_copper', 'DTPA Iron': 'dtpa_iron', 'DTPA Manganese': 'dtpa_manganese', 'DTPA Zinc': 'dtpa_zinc', 'Exc. Aluminium': 'exc_aluminium', 'Exc. Calcium': 'exc_calcium', 'Exc. Magnesium': 'exc_magnesium', 'Exc. Potassium': 'exc_potassium', 'Exc. Sodium': 'exc_sodium', 'Boron Hot CaCl2': 'boron_hot_cacl2', 'Total Nitrogen': 'total_nitrogen', '% Clay': 'clay', '% Course Sand': 'coarse_sand', '% Fine Sand': 'fine_sand', '% Sand': 'sand', '% Silt': 'silt'}
            data.columns = data.columns.to_series().map(column_dictionary)
            
            #Drop the depth column as it should be provided on the AM submission sheet
            data.drop(['depth'], axis=1, inplace=True)
            
            #Define the ouput columns and fill for CSBP SOIL methods columns
            column_order = ['sample_id']
            analysis_columns = ['color', 'gravel', 'texture', 'ammonium_nitrogen_wt', 'nitrate_nitrogen', 'phosphorus_colwell', 'potassium_colwell', 'sulphur', 'organic_carbon', 'conductivity', 'ph', 'ph_solid_h2o', 'dtpa_copper', 'dtpa_iron', 'dtpa_manganese', 'dtpa_zinc', 'exc_aluminium', 'exc_calcium', 'exc_magnesium', 'exc_potassium', 'exc_sodium', 'boron_hot_cacl2', 'total_nitrogen', 'clay', 'coarse_sand', 'fine_sand', 'sand', 'silt']
            method_number = "2.1"
        #if no matches we will throw a warning to advise and move on
        if water_file == False and soil_file == False:
            print("WARNING: " + filename + " does not appear to be a properly formatted CSBP water or soil analysis file")
            continue
        
        ######### Common mods to both Soil and Water #########
        #remove any badly formatted IDs and replace with long format ID
        formatIDs(data)

        #Fill analysis columns based on the specific Soil or Water lists
        for col in analysis_columns:
            meth_col = col + "_meth"
            if col == "water_content":
                meth_col = water_content_soil_meth
            data[meth_col] = np.nan
            #append the incoming columns to the column order list so we can order the dataframe
            column_order.append(col)
            column_order.append(meth_col)
            #populate the method number if the analysis isnt null
            for i in data.index:
                if (pd.isna(data.loc[i,col])):
                    print(col, i)
                    continue
                else:
                    data.loc[i,meth_col] = method_number

        data = data[column_order]
        #save the file 
        data.to_excel(outfile, index=False)
    else:
        print()
        print(filename + " Not in CSBP format")
        continue  

print("Finished converting files - Please check the converted files manually")
