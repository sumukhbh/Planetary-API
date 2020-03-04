from flask import Flask,jsonify

app = Flask(__name__)

@app.route("/")
@app.route("/index")

def index():
    return "<h1> Hello World! </h1>"

@app.route('/super_simple')
def super_simple():
    return jsonify(message = "Hello from Pluto")
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()

