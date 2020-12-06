# this reads the csv seperated data stram coming from USB connected arduino and
# stores the resulting data in sqldb
# create the DB using following 
# more details at  https://github.com/Mjrovai/RPI-Flask-SQLite
# host>sqlite3 sensorsData.db 
# sqlite> BEGIN;
# sqlite> CREATE TABLE DHT_data (timestamp DATETIME,  temp1 NUMERIC, temp2 NUMERIC, temp3 NUMERIC, temp4 NUMERIC, capacitance1 NUMERIC, capacitance2 NUMERIC);
# sqlite> COMMIT;
# run this python script from directory where the sqlite DB is stored

import serial
import time
import sqlite3
import threading
import numbers

lock = threading.Lock()

dbname='sensorsData.db'
ser = serial.Serial('COM9', 115200)
ser.flushInput()

# log sensor data on database
def logData (temp1, temp2, temp3, temp4, capacitance1, capacitance2):
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	try:
		lock.acquire(True)
		curs.execute("INSERT INTO DHT_data values(datetime('now'), (?), (?), (?), (?), (?), (?))", (temp1, temp2, temp3, temp4, capacitance1, capacitance2))
		conn.commit()
		conn.close()
	finally:
		lock.release()

while True:
	try:
		temp1, temp2, temp3, temp4, capacitance1, capacitance2 = 0, 0, 0, 0, 0, 0
		# remove b' and \n' from sides
		ser_bytes = str(ser.readline())[2:-3]
		# convert csv to list
		list = ser_bytes.split (",")
		print ("list: ", list)
		temp1, temp2, temp3, temp4, capacitance1, capacitance2 = list
		if (isinstance(temp1, numbers.Number)) and (isinstance(temp2, numbers.Number)) and (isinstance(temp3, numbers.Number)) and (isinstance(temp4, numbers.Number)) and (isinstance(capacitance1, numbers.Number)) and (isinstance(capacitance2, numbers.Number)):
			logData (temp1, temp2, temp3, temp4, capacitance1, capacitance2)
	except:
		print("Error")
		break
