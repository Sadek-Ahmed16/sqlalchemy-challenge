# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

print(Base.classes.keys())

# Create our session (link) from Python to the DB

# session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
    

#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    """Listing all available API routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;   -   ENTER START DATE WHERE '&lt;start&gt'<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;   -   ENTER START DATE WHERE '&lt;start&gt' AND END DATE WHERE '&lt;end&gt'"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returning qurery results from precipitation analysis"""

    session = Session(engine)

    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).order_by(measurement.date).all()

    session.close()


    prcp_dict = {date: prcp for date, prcp in results}
    
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Returning a JSON list of stations from the dataset"""

    session = Session(engine)

    results = session.query(station.station).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year for most active station"""

    session = Session(engine)

    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_stations = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_station_id = most_active_stations[0][0]
    results = session.query(measurement.date, measurement.tobs).filter(measurement.date >= one_year_ago).\
        filter(measurement.station == most_active_station_id).all()

    session.close()

    tobs_dict = {date: tobs for date, tobs in results}

    return jsonify(tobs_dict)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def tobs_analysis(start, end=None):
    """Returning a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""

    session = Session(engine)

    if end:
        results = session.query(func.min(measurement.tobs).label('TMIN'), func.avg(measurement.tobs).label('TAVG'), \
            func.max(measurement.tobs).label('TMAX')).filter(measurement.date.between(start, end)).all()
    else:
        results = session.query(func.min(measurement.tobs).label('TMIN'), func.avg(measurement.tobs).label('TAVG'), \
            func.max(measurement.tobs).label('TMAX')).filter(measurement.date >= start).all()

    session.close()

    if results:
        analysis_dict = {
            'TMIN': results[0].TMIN,
            'TAVG': results[0].TAVG,
            'TMAX': results[0].TMAX
        }

        return jsonify(analysis_dict)

if __name__ == '__main__':
    app.run(debug=True)



