"""Simple server to demonstrate how to use Google+ Sign-In."""
from flask import Flask
from flask import make_response
from flask import render_template
from flask import request
from flask import send_file
from flask import session
import googlemaps

import flask_googlemaps

APPLICATION_NAME = 'FoodeeTrendzapp'


app = Flask(__name__)
app.config['GOOGLEMAPS_KEY'] = "AIzaSyC0HM8yvrxNK1EcNfxeczoDA5HwGORYAc0"

flask_googlemaps.GoogleMaps(app)

@app.route('/', methods=['GET'])
def index():
  return render_template("index.html")

@app.route('/selectedlocation', methods=['POST','GET'])
def locationselected():
    latitude = request.form['latitude']
    longitude =request.form['longitude']
    return render_template("UserLocation.html",session=session)


if __name__ == '__main__':
  app.debug = True
  app.run()