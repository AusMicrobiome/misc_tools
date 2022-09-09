# misc_tools
miscellaneous scripts to share.  See detailed comments in script comments for usage instructions.

**reformat_AM_3col.py**:  Reformat a 3 column table to a wide format (OTUs x Samples = Rows x Cols) table  

**convert_local_time_to_UTC.py**:  Convert local time to UTC time format.  Takes *csv* with format described as input

**add_sample_name.sh**:  Add Australian microbiome sampleID, plate ID and amplicon information to the definition lines of fasta formatted sequence files
  
**sub_sample_AM_zotuTABLE_by_sample_id.py**: Subsample an abundance table downloaded from Australian Micrbiome processed data portal to keep only sampleID's of interest.

**convert_CSBP_to_AM.py**: Convert CSBP analysis metadata sheets for sample types `SOIL` or `WATER` to a format compatible with the AM metadata database. Input is one or more CSBP excel spreadsheets, output is one more AM formatted excel spreadsheets. Output filenames mirror input filenames but with suffix `*_AM_<SAMPLE_TYPE>_format_UPDATE.xlsx`. 
