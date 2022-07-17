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
    where(measurement.date >= last_12_month_date).all()

    session.close()

    # make a dictionary
    date_prcp_dict = dict(results)

    #return dictionary as json
    return jsonify(date_prcp_dict)


@app.route("/contact")
def contact():
    email = "peleke@example.com"

    return f"Questions? Comments? Complaints? Shoot an email to {email}."


# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
