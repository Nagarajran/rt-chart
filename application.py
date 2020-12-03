# mix of 
# https://github.com/Mjrovai/RPI-Flask-SQLite -  sqlite sensor value recording + flask
# https://github.com/johnsliao/flask-sqlite3-chartjs-toy - initial chart
# https://github.com/roniemartinez/real-time-charts-with-flask - realtime chart updates with Flask Server Side Event SSE, no sockets used
# put corresponding index_chart.html file in template folder
# reading serial csv sensor data from arduino and storing in sqlite handlened by another script
# 
import json
import time
from datetime import datetime
from flask import Flask, Response, render_template, make_response, request
import io
import threading
import sqlite3

lock = threading.Lock()

application = Flask(__name__)

conn=sqlite3.connect('../sensorsData.db', check_same_thread=False)
curs=conn.cursor()
global numSamples
numSamples=1

def getHistData (numSamples):

	try:
		lock.acquire(True)
	
		curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT "+str(numSamples))
		data = curs.fetchall()
		times = []
		temps1 = []
		temps2 = []
		temps3 = []
		temps4 = []
		capacitance1s = []
		capacitance2s = []
		for row in reversed(data):
			times.append(row[0])
			temps1.append(row[1])
			temps2.append(row[2])
			temps3.append(row[3])
			temps4.append(row[4])
			capacitance1s.append(row[5])
			capacitance2s.append(row[6])
		return times, temps1, temps2, temps3, temps4, capacitance1s, capacitance2s
	finally:
		lock.release()
		


@application.route('/')
def index():
	# send last 100 data to browser to render initial chart
	time1s, temps1, temps2, temps3, temps4, capacitance1s, capacitance2s = getHistData(100)
	return render_template('index_chart.html', time1s=time1s, temps1=temps1, temps2=temps2, temps3=temps3, temps4=temps4, capacitance1s=capacitance1s, capacitance2s=capacitance2s )


@application.route('/chart-data')
def chart_data():
	# send updated data since initial start to live update chart.js  on client side
	def send_updates():
		maxNumberRows_old=1
		while True:
			try:
				lock.acquire(True)
				for row in curs.execute("select COUNT(temp1) from  DHT_data"):
					maxNumberRows=row[0]		
				if maxNumberRows_old<maxNumberRows:
					for row in curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT 1"):
						time1 = row[0]
						temp1 = row[1]
						temp2 = row[2]
						temp3 = row[3]
						temp4 = row[4]
						capacitance1 = row[5]
						capacitance2 = row[6]
						maxNumberRows_old=maxNumberRows
					json_data = json.dumps({'time1': time1, 'temp1': temp1, 'temp2': temp2 , 'temp3': temp3, 'temp4': temp4, 'capacitance1': capacitance1, 'capacitance2': capacitance2})
					yield f"data:{json_data}\n\n"
			finally:
				lock.release()
		
			time.sleep(1)
		
	return Response(send_updates(), mimetype='text/event-stream')



if __name__ == "__main__":
   application.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
