from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')


database = SQLAlchemy(app)
ma = Marshmallow(app)

# create database command #
@app.cli.command('database_create')
def database_create():
    database.create_all()
    print('Database created')

# drop database command #
@app.cli.command('database_drop')
def database_drop():
    database.drop_all()
    print('Database dropped')

# database seed command #
@app.cli.command('database_seed')
def database_seed():
    mercury = Planet(planet_name='Mercury',
                     planet_type='Rocky',
                     planet_star='Sun',
                     planet_mass=2.258e23,
                     planet_radius=1516,
                     planet_distance=35.98e6)

    venus = Planet(planet_name='Venus',
                         planet_type='Rocky',
                         planet_star='Sun',
                         planet_mass=4.867e24,
                         planet_radius=3760,
                         planet_distance=67.24e6)

    earth = Planet(planet_name='Earth',
                     planet_type='Rocky',
                     planet_star='Sun',
                     planet_mass=5.972e24,
                     planet_radius=3959,
                     planet_distance=92.96e6)

    database.session.add(mercury)
    database.session.add(venus)
    database.session.add(earth)

    test_user = User(first_name='Sumukh',
                     last_name='Bharadwaj',
                     email='sumukhbh@usc.edu',
                     password='abcdef')

    database.session.add(test_user)
    database.session.commit()
    print('Database seeded!')


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/super_simple')
def super_simple():
    return jsonify(message='Hello from the Planetary API.'), 200


@app.route('/not_found')
def not_found():
    return jsonify(message='That resource was not found'), 404

# Retreiving a list of planets in JSON format #
@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)

# Method for registering new users #
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test_val = User.query.filter_by(email=email).first()
    if test_val:
        return jsonify(message="User already exists"),409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name,last_name=last_name,email=email,password=password)
        database.session.add(user)
        database.session.commit()
        return jsonify(message= "User registered successfully."),201



# Creating database models #
class User(database.Model):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String,unique=True)
    password = Column(String)



class Planet(database.Model):
    __tablename__ = 'Planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    planet_star = Column(String)
    planet_mass = Column(Float)
    planet_radius = Column(Float)
    planet_distance = Column(Float)

# using marshmallow for serialization #
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'planet_star', 'planet_mass', 'planet_radius', 'planet_distance')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)


if __name__ == '__main__':
    app.debug = True
    app.run()
