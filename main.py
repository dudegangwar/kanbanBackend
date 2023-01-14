from flask import Flask
import os
from application.config import LocalDevelopmentConfig
from application.database import db
from application import workers
from flask_session import Session
from flask_restful import Resource, Api
from application import config
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_cors import CORS
from datetime import timedelta
# from flask_caching import Cache


app = None
api = None
celery = None
CORS(api)
# cache = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    jwt = JWTManager(app)
    # app.config["SESSION_PERMANENT"] = False
    # app.config["SESSION_TYPE"] = "filesystem"   
    app.config["SECRET_KEY"] = "anuj"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    Session(app)
    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently no production config is setup.")
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)
    
    db.init_app(app)
    api = Api(app)
    app.app_context().push()

    # Create Celery
    celery = workers.celery
    # Update with configuration
    celery.conf.update(
        broker_url = app.config["CELERY_BROKER_URL"],
        result_backend = app.config["CELERY_RESULT_BACKEND"]
    )

    celery.Task = workers.ContextTask
    app.app_context().push()
    # cache = Cache(app)
    # app.app_context().push()

    return app, api, celery


app, api, celery = create_app()
CORS(app, support_credentials=True)

# from application.controllers import *
# from application.sendemail import *

# from application.email import *
# api.(UserAPI, "/api/user","api/user/<string:username>")
from application.api import * 
api.add_resource(UserAPI, "/api/user","/api/user/<string:id>")
api.add_resource(CreateUserAPI, '/api/create-user')
api.add_resource(ListAPI, "/api/getlist", "/api/getlist/<int:id>")
api.add_resource(TaskAPI, "/api/gettask/", "/api/gettask/<int:id>")
api.add_resource(StartWorker,"/api/start/<string:id>")
api.add_resource(DownloadList,'/api/export/list/<string:id>')
api.add_resource(DownloadTask,"/api/export/task/<string:id>")
api.add_resource(DownloadData, "/api/export/data/<string:id>")
from application.sendemail import *


# app.add_resource
if __name__ == '__main__':
    monthly_run()
    # mail_run()
    app.debug = True
    app.run(port=8080)
    
