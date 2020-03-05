from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail,Message


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'secret'
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '20705b3089ae45'
app.config['MAIL_PASSWORD'] = '23bef27c1c7ce8'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

database = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)

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

# Authenticating user login requests #
@app.route('/authenticate',methods=['POST'])
def authenticate():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    test_user = User.query.filter_by(email=email,password=password).first()
    if test_user:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login Successful.",access_token=access_token)
    else:
        return jsonify(message="Login Failed.You have entered a incorrect username or password."),401

# Method to retrieve password and send it to user email #
@app.route('/retrieve_pwd/<string:email>', methods=['GET'])
def retrieve_pwd(email:str):
    user = User.query.filter_by(email=email).first()
    if user:
        message = Message("Your password is : "+ user.password, sender="admin@planetaryAPI.com", recipients=[email])
        mail.send(message)
        return jsonify(message="Password sent to "+ user.email)
    else:
        return jsonify(message="Email doesn't exist")

# Method to fetch planet details #
@app.route('/fetch_details/<int:planet_id>', methods=['GET'])
def fetch_details(planet_id:int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message="Planet does not exist!"),404

# Method to add new planets #
@app.route('/add_planet', methods=['POST'])
@jwt_required
def add_planet():
    planet_name = request.form['planet_name']
    test_planet = Planet.query.filter_by(planet_name=planet_name).first()
    if test_planet:
        return jsonify("There is already a planet by that name"), 409
    else:
        planet_type = request.form['planet_type']
        planet_star = request.form['planet_star']
        planet_mass = float(request.form['planet_mass'])
        planet_radius = float(request.form['planet_radius'])
        planet_distance = float(request.form['planet_distance'])

        new_planet = Planet(planet_name=planet_name,
                            planet_type=planet_type,
                            planet_star=planet_star,
                            planet_mass=planet_mass,
                            planet_radius=planet_radius,
                           planet_distance=planet_distance)
        database.session.add(new_planet)
        database.session.commit()
        return jsonify(message="You added a planet"), 201

# Method to delete a planet #
@app.route('/delete_planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id: int):
    planet_delete = Planet.query.filter_by(planet_id=planet_id).first()
    if planet_delete:
        database.session.delete(planet_delete)
        database.session.commit()
        return jsonify(message="Planet deleted."), 202
    else:
        return jsonify(message="Planet does not exist"), 404

# Method to update planet details #
@app.route('/update_planet', methods=['PUT'])
#@jwt_required
def update_planet():
    planet_id = int(request.form['planet_id'])
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.form['planet_name']
        planet.planet_type = request.form['planet_type']
        planet.planet_star = request.form['planet_star']
        planet.planet_mass = float(request.form['planet_mass'])
        planet.planet_radius = float(request.form['planet_radius'])
        planet.planet_distance = float(request.form['planet_distance'])
        database.session.commit()
        return jsonify(message="Planet updated."), 202
    else:
        return jsonify(message="Planet does not exist."), 404

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
