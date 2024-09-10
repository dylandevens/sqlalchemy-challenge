
# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta
from sqlalchemy import inspect

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station



#################################################
# Flask Setup
#################################################
# from 10.4

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to my 'Surf's Up' Homepage!<br/>"
    
    f"Available Routes: <br/>"
    f"/api/v1.0/about<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/(start)<br/>"
    f"/api/v1.0/(start)/(end)<br/>"
    )










@app.route("/api/v1.0/about")
def about():
    print("Server received request for 'About' page...")
    return """Welcome to my 'About' page!
    
    This is my first flask application. please take a tour, and if you feel up to it,
    plan your own Hawaiian Suf-cation"""
    

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data."""
    session = Session(engine)
    
    #Select for last 12 months
    most_recent = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    year_ago = datetime.date(most_recent) - datetime.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores for last 12 months
    results = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= year_ago).all()
    
    session.close()
    
    #to dictionary
    prcp_dictionary = {date: prcp for date, prcp in results}
    
    return jsonify(prcp_dictionary)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    session = Session(engine)
    results = session.query(Stations).all()
    session.close()
    
    #to dictionary
    stations_dict = {}
    for station in results:
        stations_dict[station.station] = {
            "name": station.name,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "elevation": station.elevation
        }
    
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the last 12 months of temperature data from the most_active station."""
    session = Session(engine)
    
    # Using the most active station id
    most_active = session.query(Measurements.station).group_by(Measurements.station).order_by(func.count(Measurements.station).desc()).first()[0]


    #Select for last 12 months
#     most_recent = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
    most_recent = session.query(func.max(Measurements.date)).first()[0]
#     most_recent = datetime.strptime(most_recent, "%Y-%m-%d")
    # Calculate the date one year from the last date in data set.
    year_ago = datetime.strptime(most_recent, "%Y-%m-%d") - timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores for last 12 months
    results = session.query(Measurements.date, Measurements.tobs).filter(Measurements.station == most_active).filter(Measurements.date >= year_ago.strftime("%Y-%m-%d")).all()

    
    session.close()

    
#     to_dictionary
    temp_dict = {date: temp for date, temp in results}
    header = f"Date:    Temp:    for station id {most_active}\n"                                                                                         
#     return header + jsonify(temp_dict)
    return jsonify(temp_dict)
                                                                                     
                                                                                                      
                                                                                          
@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return min, max, and avg temp for only a start date"""
    session = Session(engine)
    
    start = start.strip('()')
#     start_date = start.strftime("%Y-%m-%d")
    
    with_start = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).filter(Measurements.date >= start).all()
    
    session.close()
    
    
    if with_start:
        min_temp, avg_temp, max_temp = with_start[0]
        start_summary = {
            "start_date": start,
            "TMIN": min_temp,
            "TAVG": avg_temp,
            "TMAX": max_temp
        }

    
    return jsonify(start_summary)
               
                               
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start,end):
    """Return min, max, and avg temp for a start AND end date"""
    session = Session(engine)

    start = start.strip('()')
    end = end.strip('()')
    
    with_start_and_end = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    
    session.close()
    
    
    if with_start_and_end:
        min_temp, avg_temp, max_temp = with_start_and_end[0]
        end_summary = {
            "start_date": start,
            "end_date": end,
            "TMIN": min_temp,
            "TAVG": avg_temp,
            "TMAX": max_temp
        }
    

    
    return jsonify(end_summary)    
                                   
                                
if __name__ == "__main__":
    app.run(debug = True)
    
