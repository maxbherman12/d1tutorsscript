## D1 Tutors Script

This script was developed for the purpose of streamlining the administrative processes associated with running a
tutoring business. The script allows the user to manage clients, log sessions, get invoices, and keep track of finances.

*Feel free to take this code as a blueprint and adapt it to your own business administration*

The database used in this script is Google Sheets. The script interacts with the Google Sheets API using
the *gspread* python package

Follow this article to configure Google Console correctly to use gspread:
https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html

The script was built to be run in the command line. In my implementation on my local machine I accomplish this with a
short shell script to access the project file and run the main.py file.

Not included for privacy reasons are two files:
1. clients.txt - a file that contains all client information needed for the script which 
   updates as clients are added/removed
   

2. keys.json - json object that contains the keys necessary for connecting to the Google Sheets API with gspread