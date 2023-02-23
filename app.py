import numpy as np

import sqlalchemy
import datetime as dt
import pandas as pd
from datetime import date, timedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func



from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into to a new model
base = automap_base()

# Reflect the tables 
base.prepare(engine, reflect=True)

# Save references 
Measurement = base.classes.measurement
Stations = base.classes.station

# Flask Set up
app = Flask(__name__)


# Flask Routes 
@app.route("/")
def home():
    """List all available routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query dates and precipitaion
    results = session.query(Measurement.date, Measurement.prcp).all()

    # create a dictionary using 'date' as the key and 'prcp' as the value
    all_prcp = []

    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    Session.close()

# return the list of all dates and prcp
    return jsonify(all_prcp)

# 2) Stations Route
@app.route("/api/v1.0/stations")
def stations():
    
    # Query all distinct stations
    session = Session(engine)
    results = session.query(Measurement.station).distinct().all()

    session.close()

     # Store results as a list
    stations_list = list(np.ravel(results))

    # Return a list of all distinct stations
    return jsonify(stations_list)

# 3) Tobs Routes
@app.route("/api/v1.0/tobs")
def tobs():
    # Query
    session = Session(engine)
     #Query the dates and temperature observations of the most active station
    Result =  session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').filter(Stations.station == Measurement.station).filter(Stations.name == 'WAIHEE 837.5, HI US').all()
    
    session.close()

    #Return a JSON list of temperature observations (TOBS)
    tobs_list = []
    for date, tobs in Result:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs 
        tobs_list.append(tobs_dict)

    #Return a JSON list of tobs from the dataset
    return jsonify(tobs_list)
    
@app.route("/api/v1.0/<start>")
def StartDate(start_date_only):   
# Create our session (link) from Python to the DB
    session = Session(engine)

    Results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date_only).group_by(Measurement.date).all()

    session.close()

    #Return JSON list of max, min, avg tobs
    start_list = []
    for date,tmin,tmax,tavg in Results:
        start_dict = {}
        start_dict['Date'] = date
        start_dict['TMIN'] = tmin
        start_dict['TMAX'] = tmax
        start_dict['TAVG'] = tavg
        start_list.append(start_dict)

    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def StartDateEndDate(start_date,end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    Resultss = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date<=end_date).group_by(Measurement.date).all()

    session.close()

    #Return JSON list of max, min, avg tobs
    startend_list = []
    for date,Tmin,Tmax,Tavg in Resultss:
        startend_dict = {}
        startend_dict['Date'] = date
        startend_dict['TMIN'] = Tmin
        startend_dict['TMAX'] = Tmax
        startend_dict['TAVG'] = Tavg
        startend_list.append(startend_dict)

    return jsonify(startend_list)    


if __name__ =='_main_': 
    app.run(debug=True)