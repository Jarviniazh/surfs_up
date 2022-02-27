# Import the Basic Dependency
import datetime as dt
from keyring import set_keyring
import numpy as np
import pandas as pd

# Import dependencies for SQLAIchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import flask dependency
from flask import Flask, jsonify
from sympy import re

# Set up the database
# Access an query SQLite database file
engine = create_engine("sqlite:///hawaii.sqlite")
# Reflect the database into classes
Base = automap_base()
# Reflect the database
Base.prepare(engine, reflect=True)
# Get each class's name
Base.classes.keys()
# Create a variable for each class
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create a session link from python to database
session = Session(engine)

# Setup Flask
# Create a New Flask App Instance
app = Flask(__name__)

# Create Flask Routes for welcome
@app.route("/")
def welcome():
    return ("""
    Welcome to the Climate Analysis API!<br/>
    Available Routes:<br/>
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/temp/start/end <br>
    """)

# Create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the most recent date
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Write a query to get the date and precipitation for the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    # Create a dictionary with the date as the key and the precipitation as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# Create satation routes
@app.route("/api/v1.0/stations")
def stations():
    # Get all stations in the database
    results = session.query(Station.station).all()
    # Unravel results into a one-dimensional array (np.ravel()) 
    # And convert unraveled results into a list (list())
    stations = list(np.ravel(results))
    # Jsonify the list and return it as JSON
    return jsonify(stations=stations)

# Create monthly temperature route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Calculate the date one year ago from the most recent date
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Query the primary station for all the temperature observations
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= prev_year).all()
    # Unravel results into a one-dimensional array (np.ravel()) 
    # And convert unraveled results into a list (list())
    temps = list(np.ravel(results))
    # Jsonify the list and return it as JSON
    return jsonify(temps = temps)

# Create statistics route
# Provide both a starting and ending date
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
# Create stats() function and add start and end parameters
def stats(start=None, end=None):
    # Create a query to select the minimum, average, and maximum temperatures from our SQLite database
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)]
    # Determine the starting and ending date
    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
    
    results = session.query(*sel).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))    
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
