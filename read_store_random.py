import serial
import time
import sqlite3
import threading
import random
import numbers
random.seed()

lock = threading.Lock()

dbname='sensorsData.db'

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
		temp1=round(random.uniform(25.1, 29.9),2)
		temp2=round(random.uniform(30, 35),2)
		temp3=round(random.uniform(35, 39.9),2)
		temp4=15.0
		capacitance1=round(random.uniform(1.5, 1.7),2)
		capacitance2=round(random.uniform(1.0, 1.49),2)
		if (isinstance(temp1, numbers.Number)) and (isinstance(temp2, numbers.Number)) and (isinstance(temp3, numbers.Number)) and (isinstance(temp4, numbers.Number)) and (isinstance(capacitance1, numbers.Number)) and (isinstance(capacitance2, numbers.Number)):
			logData (temp1, temp2, temp3, temp4, capacitance1, capacitance2)
		#print ("list: "+"{:.2f}".format(temp2))
		time.sleep(1)
	except:
		print("Error")
		break
