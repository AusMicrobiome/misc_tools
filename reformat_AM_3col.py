# -----------------------------------------------------------
# Converts a 3 column style OTU table to a rectangular XxY table
#
# 20200424
# -----------------------------------------------------------


"""
A script to convert long (3 col + taxonomy) format table as exported by AM database to wide format
(ASV'z X Samples (rows X cols) table.

Input is the *.csv table downloaded from the AM denoised dataportal https://data.bioplatforms.com/bpa/otu/.
This must have column names ['OTU','Amplicon','Kingdom','Phylum','Class','Order','Family','Genus','Species', 'Traits'] and be
csv.

Output is a rectangular table and includes the taxonomy contained in the downloaded 3 column table.

"""

infile=input("path to input file: ")
output=input("name of your output file: ")
expected_cols=['Sample ID','OTU','OTU Count','Amplicon','Kingdom','Phylum','Class','Order','Family','Genus','Species', 'Traits']
import pandas as pd
#read the long table in

print("Reading "+infile)

tableL = pd.read_csv(infile)


if tableL.columns.tolist()!=expected_cols:
    print("input table is not in expexted format")
else:
    print("pivoting "+infile)
    #pivot the table out to wide format, fill 'na' with 0 to make the OTU table
    tableW = tableL.pivot_table(index='OTU', columns='Sample ID', values='OTU Count').fillna(0)

if tableW.values.sum() == tableL['OTU Count'].sum(): #check the table values
    print("adding taxonomy")

    #add the taxonomy back in
    taxonomy = ['OTU','Amplicon','Kingdom','Phylum','Class','Order','Family','Genus','Species', 'Traits']
    taxL = tableL[taxonomy] #get the taxonomy data
    taxL1 = taxL.drop_duplicates(keep='first').set_index('OTU') #remove the duplicates
    merge=pd.merge(tableW,taxL1,left_index=True, right_index=True, how='inner') #merge the OTU abundance and taxonomies

else:
    print("error: abundance of input table != abundance of pivoted table")

if merge.drop(['Amplicon','Kingdom','Phylum','Class','Order','Family','Genus','Species', 'Traits'], axis=1).values.sum() ==  tableL['OTU Count'].sum():
    merge.to_csv(output+'.csv') #write the table out
    print(".....finished!")
else:
    print("error merging taxonomies")
