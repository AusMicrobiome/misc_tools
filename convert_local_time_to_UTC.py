'''
A script to convert local date and time stamps to UTC 

This script will open a csv file and use latitude and longitude information
to convert local date and time fields to UTC time. The output format is compatible 
with the required Australian Microbiome metadata format

Usage:
1) Create and save a csv file containing the following header names and relevant information:

Sample_ID,Date_sampled [YYYY-MM-DD],Time_sampled [hh:mm],Latitude_(decimal_degrees),Longitude_(decimal_degrees)

2) Upon running the script, the user will be prompted to enter the path and name of the csv file to be converted.
    The script will advise the user of the output file name and path.
 
5) The script will generate: 
    UTC_Date_sampled_(YYYY-MM-DD) = UTC date format that can be submitted to the AM
    UTC_Time_sampled_(hh:mm:ss) = UTC time format that can be submitted to the AM

   The zone column, highlights the geographical location the calculation was based on,
    the user is encouraged to check that the locations are accurate for the sample prior to submission. 

Note: If opening the output file in excel, it may automatically reformat the date stamp formats.

Troubleshooting

If the script fails to run please check the following:
        1) The required columns are named correctly
        2) The local Date and Time columns are in the correct format
        3) Ensure there are no blank lines in the csv file
if the problem persists please contact us.

'''
from timezonefinder import TimezoneFinder
import pandas as pd
import pytz, datetime
import readline
#import glob

readline.parse_and_bind("tab: complete")

input_file = input("PATH and name of csv file: ")

output_file = input_file.replace(".csv", "") + "_UTC_converted.csv"

print("output file is: " + output_file)

#read in the contents of the file and combine the date and time columns
df = pd.read_csv(input_file, parse_dates=[['Date_sampled [YYYY-MM-DD]', 'Time_sampled [hh:mm]']], engine='python')

#change Date and ctime columns to a simpler form
df = df.rename(columns={'Date_sampled [YYYY-MM-DD]_Time_sampled [hh:mm]': 'Local_Date_Time'})

#forat the time stamp to remove the seconds
df['Local_Date_Time'] = df['Local_Date_Time'].apply(lambda t: t.strftime('%Y-%m-%d %H:%M'))

tf = TimezoneFinder()

dt_UTC = [] #create an empty list for the UTC times
dt_zone = [] #create an empty list for the zones, just to check

for i in range(df.shape[0]):

    raw_dat = df.iloc[i].tolist()
    #Get store positions of the lat and lon columns in the dataframe
    lat_pos = df.columns.get_loc("Latitude_(decimal_degrees)")
    lon_pos= df.columns.get_loc("Longitude_(decimal_degrees)")
    #pass lat and lon positions
    latitude, longitude = raw_dat[lat_pos], raw_dat[lon_pos]
    zone=tf.timezone_at(lng=longitude, lat=latitude)
    dt_zone.append(zone)
    print("converting to UTC for timezone: " + zone)
    local = pytz.timezone (zone) #set local time zone string

    dt_pos = df.columns.get_loc("Local_Date_Time")
    naive = datetime.datetime.strptime (raw_dat[dt_pos], "%Y-%m-%d %H:%M")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    dt_UTC.append(utc_dt.strftime ("%Y-%m-%d %H:%M:%S"))
#make a columns for converted time and time zone

df["UTC"] = dt_UTC
df['zone'] = dt_zone
#Split the time into db friendly columns
df['UTC_Date_sampled_(YYYY-MM-DD)'] = df['UTC'].apply(lambda x: x).str.split(' ').str[0]
df['UTC_Time_sampled_(hh:mm:ss)'] = df['UTC'].apply(lambda x: x).str.split(' ').str[1]

#write out the dataframe to a csv file 
df.to_csv(output_file, index = False)
print("data written to: " + output_file)

