from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import Column, Integer, String, Float

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
database =  SQLAlchemy(app)
@app.route("/")
@app.route("/index")

def index():
    return "<h1> Hello World! </h1>"

@app.route('/super_simple')
def super_simple():
    return jsonify(message = "Hello from Planetary API")

# Creating Database Models #
class User(database.Model):
    __TableName__ = "Users"
    id = Column(Integer, primary_key = True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique = True)
    password = Column(String)

class Planets(database.Model):
    __TableName__ = "Planets"
    planet_id = Column(Integer, primary_key = True)
    planet_name = Column(String)
    planet_star = Column(String)
    planet_mass = Column(Float)
    planet_type = Column(String)
    planet_radius = Column(Float)
    planet_distance = Column(Float)

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()

