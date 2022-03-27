# Flask app
from flask import Flask, request, jsonify, render_template
import boto3
import requests
import os
import base64
from botocore.exceptions import ClientError
import json
from flask_mysqldb import MySQL
from dotenv import load_dotenv
app = Flask(__name__)

load_dotenv('.env')
rds_host = os.environ['DBWRITER']
access_key_id = os.environ['ACCESS_KEY']
secret_access_key = os.environ['SECRET_KEY']
session_token = os.environ['SESSION_TOKEN']

# need to retrive the username and password for DB from secrets manager

landing_page = """
	<H1>Network & Security -- EC2 to RDS (Public to Private Subnet)</H1>
	<form action="/liststudents" method="get">
		<input type="submit" value="start">
	</form>
"""

list_students = """
	<H1>Network & Security -- EC2 to RDS (Public to Private Subnet)</H1>
	<h2>List of students:</h2>

"""
# getting aws session


def get_session():
    session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_seccret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name='us-east-1'
    )
    return session

# there needs to be 2 functions.
# one sends data to the db by sending it to the writer cluster
# the second gets the data from the reader cluser

# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developers/getting-started/python/


def get_secret():

    secret_name = "database-password"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name='us-east-1'
    )
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        print("hello world")
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret = json.loads(get_secret_value_response['SecretString'])
        print(secret)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
        secret = {'DBUsername': 'didnt work', 'DBPassword': 'didnt work'}
    return secret


def get_db():
    secret = get_secret()
    app.config['MYSQL_HOST'] = rds_host
    app.config['MYSQL_USER'] = secret['DBUsername']
    app.config['MYSQL_PASSWORD'] = secret['DBPassword']
    app.config['MYSQL_DB'] = 'drewsdb'
    db = MySQL(app)
    return db


@app.route("/")
def landing_page_func():
    return render_template("index.html")


@app.route("/storestudents", methods=['POST'])
def store_students():
    data = request.get_json()
    print(data)
    # removes the array of student objects from the data recieved
    student_list = data['students']
    # retrieves credentials from AWS secrets manager
    secret = get_secret()
    app.config['MYSQL_HOST'] = rds_host
    app.config['MYSQL_USER'] = secret['DBUsername']
    app.config['MYSQL_PASSWORD'] = secret['DBPassword']
    app.config['MYSQL_DB'] = 'drewsdb'
    mysql = get_db()
    print(mysql)

    # connects to the database
    # shouldn't work unti code is on the server
    cur = mysql.connection.cursor()
    for students in student_list:
        # adds the student to the database
        cur.execute("INSERT INTO students (first_name, last_name, banner) VALUES (%s, %s, %s)",
                    (students['first_name'], students['last_name'], students['banner']))
    mysql.connection.commit()

    cur.close()
    # connect to RDS server that is inside of a private subnet inside of the VPC
    # insert one react for each student in the students array
    # return 200 if successful, 400 and error message if not
    return {"status": 200}


@app.route("/liststudents", methods=['GET'])
def list_students_func():
    # connect to RDS that is on the private subnet insdie of the VPC
    # query the students table and a return a list of all students to display in
    # browser. Probably as a list in a html doc or something
    return render_template("liststudents.html")


if __name__ == "__main__":
    # running on host 0.0.0.0 ensures the app is being run on the public facing ip
    secret = get_secret()
    print(secret['DBUsername'])
    app.run(host="0.0.0.0", port=5000)
