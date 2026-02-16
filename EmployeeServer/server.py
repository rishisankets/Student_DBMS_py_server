from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)
# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Rishi123#',
    'database': 'employee'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        raise Exception("Error while connecting to MySQL", e)
    return None

@app.route('/version',methods=['GET'])
def version():
    return jsonify({"version": "v1.0.0"}), 200
    
    

@app.route('/list/employee',methods=['GET'])
def index():
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees LIMIT 100;")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(rows)

###################################POST

@app.route('/new/employee', methods=['POST'])
def newEmployee():
    data = request.get_json()
    print(data)
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to database"}), 500
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT max(emp_no) FROM employees")
        maxRow = cursor.fetchone()
        max=0
        if (maxRow[0] == None) :
            max = 0
        else :
            max = maxRow[0]
            max = max + 1
            
        hireDate = datetime.now(timezone.utc)
        formatted_time = hireDate.strftime("%Y-%m-%d")
        dob = data["dob"]
        dob = dob.replace('Z', '').split('.')[0]
        dob = datetime.fromisoformat(dob)
        dob = dob.strftime("%Y-%m-%d")
        print(data)
        strArg =  f"INSERT INTO employees (emp_no, birth_date, first_name, last_name, gender, hire_date) VALUES ({max},'{dob}','{data["firstName"]}','{data["lastName"]}','{data["gender"]}','{formatted_time}')"
        print(strArg)
        cursor.execute(strArg)
        connection.commit()
        cursor.close()
        connection.close()
    except Error as e:
        print(e)
        return jsonify({'error': f"Database error: {str(e)}"}), 500

    return jsonify({'message': f"User {data["firstName"]} with hire date {formatted_time} added successfully."}), 201








@app.route('/employee/<empid>', methods=['DELETE'])
def delEmployee(empid):
    # data = request.get_json()
    # print(data)
    msg = ""
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to database"}), 500
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM employee.employees where emp_no={empid}")
        emp = cursor.fetchone()
        if (emp != None) :
            cursor.execute(f"DELETE FROM employees WHERE emp_no={empid}")
            connection.commit()
            msg = f"Employee {empid} deleted successfully."
        else:
            msg = f"Employee {empid} does not exist."
        cursor.close()
        connection.close()
    except Error as e:
        print(e)
        return jsonify({'error': f"Database error: {str(e)}"}), 500

    return jsonify({'message': msg})

if __name__ == '__main__':
    app.run(debug=True,port=5001)
    
    