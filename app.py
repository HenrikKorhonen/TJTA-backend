import os

from flask import Flask, jsonify, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base

POSTGRES_USER = os.environ["PG_USER"]
POSTGRES_PW = os.environ["PG_PASS"]
POSTGRES_URL = "206.189.28.120:5432"
POSTGRES_DB = "testing"

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

#Modified
#from the official Flask tutorial github.com/pallets/flask
def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=DB_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS="FALSE"
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)  
    except OSError:
        pass

    db = SQLAlchemy(app)
    Base = automap_base()
    Base.prepare(db.engine, reflect=True)
    julkaisu = Base.classes.julkaisu
    henkilo = Base.classes.henkilo

    @app.route("/titles/<string:id>")
    @app.route("/v1/titles/<string:id>")
    def title(id):
        try:
            result = db.session.query(julkaisu).filter_by(tconst=id).first()
            
            return jsonify(tconst=result.id,
                   titletype=result.titletype,
                   primarytitle=result.primarytitle,
                   originaltitle=result.originaltitle,
                   isadult=result.isadult,
                   startyear=result.startyear,
                   endyear=result.endyear,
                   runtimeminutes=result.runtimeminutes,
                   genres=result.genres.split(","))
            
            
        except Exception as e:
            return Response(e, 500)
        

    @app.route("/names/<string:id>")
    @app.route("/v1/names/<string:id>")
    def name(id):
        try:
            result = db.session.query(henkilo).filter_by(nconst=id).first()
            return jsonify(nconst=result.id,
                   primaryname=result.primaryname,
                   birthyear=result.birthyear,
                   deathyear=result.deathyear,
                   primaryprofession=result.primaryprofession,
                   knownfortitles=result.knownfortitles.split(","))

        except Exception as e:
            return Response(e, 500)

    @app.route("/search")
    @app.route("/v1/search")
    def search():
        try:
            query = request.args.get('q')
            print(query)
            results = db.session.query(julkaisu).filter(julkaisu.primarytitle.like("%{q}%".format(q=query))).all()
            return jsonify(results=[result.tconst for result in results])

        except Exception as e:
            return Response(e, 500)
        


    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
    
