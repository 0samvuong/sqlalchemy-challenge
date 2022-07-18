import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



# 3. Define static routes
@app.route("/")
def index():
    return (
        f"Hello, here are a list of routes: <br/>"
        f"/api/v1.0/precipitation <br/>" 
        f"/api/v1.0/stations<br/>" 
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

   
    # precipitation query - well the queries to get the last date / 12 months date

    last_date_query = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date_query[0], '%Y-%m-%d').date()
    last_12_month_date = last_date - dt.timedelta(days=365)
    
    #resulting query
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= last_12_month_date).all()

    session.close()

    # make a dictionary
    date_prcp_dict = dict(results)

    #return dictionary as json
    return jsonify(date_prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    # i worked on the tobs app first, then simply amended that query to only return the list of names
    session = Session(engine)
    active_stations = session.query(station.name).\
    filter(station.station == measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).all()
    session.close()

    temp_list = []

    for x in active_stations:
        temp_dict = {}
        temp_dict["name"] = x.name
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # need the label agg functions to ref it later
    active_stations = session.query(func.count(measurement.station).label('count'), measurement.station, station.name).\
    filter(station.station == measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).all()
    session.close()

    temp_list = []

    for x in active_stations:
        temp_dict = {}
        temp_dict["count"] = x.count
        temp_dict["station id"] = x.station
        temp_dict["name"] = x.name
        temp_list.append(temp_dict)
    

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(engine)
    results = session.query(func.min(measurement.tobs).label('min'),func.max(measurement.tobs).label('max'), func.avg(measurement.tobs).label('mean')).\
       filter(measurement.date >= start).all()
    session.close() 

    temp_list = []

    for x in results:
        temp_dict = {}
        temp_dict["min"] = x.min
        temp_dict["max"] = x.max
        temp_dict["mean"] = x.mean
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    
    #honestly im not sure if this works, sometimes i get a result and sometimes i dont...
    session = Session(engine)
    results2 = session.query(func.min(measurement.tobs).label('min'),func.max(measurement.tobs).label('max'), func.avg(measurement.tobs).label('mean')).\
       filter(measurement.date >= start).\
       filter(measurement.date <= end).all()
    session.close() 

    temp_list2 = []

    for x in results2:
        temp_dict2 = {}
        temp_dict2["min"] = x.min
        temp_dict2["max"] = x.max
        temp_dict2["mean"] = x.mean
        temp_list2.append(temp_dict2)
    
    return jsonify(temp_list2) 

# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
