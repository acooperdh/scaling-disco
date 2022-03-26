# Flask app
from flask import Flask, request, jsonify
import boto3
import requests

app = Flask(__name__)


access_key_id = ""
secret_access_key = ""
rds_host = ""
rds_port = 3306
# need to retrive the username and password for DB from secrets manager

landing_page = """
	<H1>Network & Security -- EC2 to RDS (Public to Private Subnet)</H1>
	<form action="/liststudents" method="get">
		<input type="submit" value="start">
	</form>
"""

list_students = """
	<H1>Network & Security -- EC2 to RDS (Public to Private Subnet)</H1>
	<p>List of students:</p>

"""


@app.route("/")
def landing_page_func():
    return landing_page


@app.route("/storestudents", methods=['POST'])
def store_students():
    data = request.get_json()
    print(data)
    student_list = data['students']
    for student in student_list:
        print(student['first_name'])
    # Parse JSON from request
    # there will be a student object, which inside has a list of students
    # each student has their first name, last name, and banner number
    # connect to RDS server that is inside of a private subnet inside of the VPC
    # insert one react for each student in the students array
    # return 200 if successful, 400 and error message if not
    return {"status": 200}


@app.route("/liststudents", methods=['GET'])
def list_students_func():
    # connect to RDS that is on the private subnet insdie of the VPC
    # query the students table and a return a list of all students to display in
    # browser. Probably as a list in a html doc or something
    return list_students
