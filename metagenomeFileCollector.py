#!/usr/bin/python
"""
This script extracts specified file types from tar.gz archives containing full SQM workflow outputs.
Input should be a file with sample ids (one per line, without 102.100.100/), and a file with file types desired 
(one per line, e.g., "sqm.21.stats").  These files are made from the data request.

The script will make and output directory per sample ID and extract the desired files to that directory.  
The output directories should not exist before running the script, if they do that sample will be skipped and a warning printed
"""


import glob
import tarfile
import os

#make a list of file types
with open('types.txt') as f:
    fileTypes = [line.rstrip() for line in f]
    #print(fileTypes)

#make a list of samples
with open('ids.txt') as f:
    samples = [line.rstrip() for line in f]
    #print(samples)


for sample in samples:
    print("processing "+sample)
    outdir = sample+"_out" #name ouput directory
    isExist = os.path.exists(outdir) # Check whether the specified path exists or not, TRUE/FALSE
    if not isExist:
        os.mkdir(outdir) # Create a new directory because it does not exist
        archive = glob.glob(sample+'*.tar.gz') #get the tar.gz file name for the sample SQM run
        #print("Archive = "+archive[0])
        t = tarfile.open(archive[0], 'r') #open the tar file
        for type in fileTypes:
            for member in t.getmembers(): #get the file contained in the acrhive
                if type in member.name: #if the file type is in the list extract it
                    print("extracting "+type)
                    t.extract(member, outdir)
    else:
        print("WARNING:  output directory "+outdir+" already exists") #print warning if exists

print("Extraction complete")
