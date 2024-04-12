# from flask import Flask, request, make_response
# from flask_sqlalchemy import SQLAlchemy
# # from app import db, Student
# from flask_mysqldb import MySQL


# app = Flask(__name__)

 
# #  this connection is with mysql
# app.config['MYSQL_HOST'] = 'mcdahackathondb.cp0g6cm4mpmv.ca-central-1.rds.amazonaws.com'
# app.config['MYSQL_USER'] = 'admin'
# app.config['MYSQL_PASSWORD'] = 'mcdaPassword'
# app.config['MYSQL_DB'] = 'MCDAHackathon'
 
# mysql = MySQL(app)

# # this connection is with flask-sqlalchemy
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:mcdaPassword@mcdahackathondb.cp0g6cm4mpmv.ca-central-1.rds.amazonaws.com/MCDAHackathon'
# # db = SQLAlchemy(app)


# @app.route('/')
# def show():
#     return 'hello'
# # def show_users():
# #  #Executing SQL Statements
# #     cur = mysql.connection.cursor()
# #     cur.execute("SELECT * FROM ansell LIMIT 10")
# #     # Fetch the results
# #     data = cur.fetchall()
    
# #     # Close cursor
# #     cur.close()
    
# #     # Create a string to display the results
# #     result_string = ""
# #     for row in data:
# #         result_string += str(row) + "<br>"
    
# #     # Return the string response
# #     return result_string




# if __name__ == '__main__':
#     with app.app_context():
#         # Your Flask application logic here
#         # app.run(debug=True)
#         app.run(host='127.0.0.1', debug=True)