'''
A script to retrieve a list of samples from an abundance table downloaded from Austrlain Microbiome bpa-otu.
Input is: 1) the downloaded table, comma seperated, typically with sampleID, ASVID, count and taxonomy information.
        2) a file comprising a list of sampleID's to keep, one per line.  
Output is the same format and a table comprising a subset of the original containing only the desired sample ID's
in the `Sample_only` column

'''
import readline
readline.parse_and_bind("tab: complete")

sample_file = input("PATH to sample ID list: ")
otuTABLE = input("PATH to 3 col format input table: ")
output_table = input("PATH to result table: ")

samples_to_keep=set()

def get_unique_samples():
   # samples_to_keep = set()
    with open(sample_file, 'r', encoding='utf-8-sig') as list_file:
        for line in list_file:
            if line.strip():
                samples_to_keep.add(line.strip())

def subset_3col_table():
    with open(otuTABLE, 'r') as otu_table:
        with open(output_table, 'w') as subset_table:
            subset_table.write(otu_table.readline())
            for line in otu_table:
                if set(line.split(',')[:-1]) & samples_to_keep:
                    subset_table.write(line)


get_unique_samples()
subset_3col_table()

