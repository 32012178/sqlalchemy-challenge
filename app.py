import numpy as np
import sqlalchemy
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into to a new model
Base = automap_base()

# Reflect the tables 
Base.prepare(engine, reflect=True)

# Save references 
print(Base.classes.keys())
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Set up
app = Flask(__name__)

# Flask Routes 
@app.route("/")
def home():
    """List all available routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received a request for precipitation")
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query dates and precipitaion
    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= '2016-08-23').group_by(Measurement.date).order_by(Measurement.date).all()

    Session.close()

    # create a dictionary using 'date' as the key and 'prcp' as the value
    precipitation_list = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        precipitation_list.append(precipitation_dict)
   

    # return the list of all dates and prcp
    return jsonify(precipitation_list)

# 2) Stations Route
@app.route("/api/v1.0/stations")
def stations():
    
    # Query all distinct stations
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the station name
    result = session.query(Station.station).all()

    session.close()

    #create a list of stations
    station_list = []
    for station in result:
        station_list.append(station)

    #Return a JSON list of stations from the dataset
    return jsonify(station_list)

# 3) Tobs Routes
@app.route("/api/v1.0/tobs")
def tobs():
    # Query
    session = Session(engine)
     #Query the dates and temperature observations of the most active station
    Results =  session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').filter(stations.station == Measurement.station).filter(stations.name == 'WAIHEE 837.5, HI US').all()
    
    session.close()

    #Return a JSON list of temperature observations (TOBS)
    tobs_list = []
    for date, tobs in Results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs 
        tobs_list.append(tobs_dict)

    #Return a JSON list of tobs from the dataset
    return jsonify(tobs_list)
    
@app.route("/api/v1.0/&ltstart&gt")
def start_date(start):
    session = Session(engine) 

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    # Create query for minimum, average, and max tobs where query date is greater than or equal to the date the user submits in URL
    start_date_tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close() 

    # Create a list of min,max,and average temps that will be appended with dictionary values for min, max, and avg tobs queried above
    start_date_tobs_values =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    
    return jsonify(start_date_tobs_values)


# Create a route that when given the start date only, returns the minimum, average, and maximum temperature observed for all dates greater than or equal to the start date entered by a user

@app.route("/api/v1.0/&ltstart&gt/&ltend&gt")

# Define function, set start and end dates entered by user as parameters for start_end_date decorator
def Start_end_date(start, end):
    session = Session(engine)

    """Return a list of min, avg and max tobs between start and end dates entered"""
    
    # Create query for minimum, average, and max tobs where query date is greater than or equal to the start date and less than or equal to end date user submits in URL

    start_end_date_tobs_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()
  
    # Create a list of min,max,and average temps that will be appended with dictionary values for min, max, and avg tobs queried above
    start_end_tobs_date_values = []
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["min_temp"] = min
        start_end_tobs_date_dict["avg_temp"] = avg
        start_end_tobs_date_dict["max_temp"] = max
        start_end_tobs_date_values.append(start_end_tobs_date_dict) 
    

    return jsonify(start_end_tobs_date_values) 


if __name__ == '__main__':
    app.run(debug=True)
