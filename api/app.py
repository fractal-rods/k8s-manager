import os

from flask import Flask

from flask_app.controllers.v1 import blueprint


def create_app(test_config=None):
    # create and configure the app
    UPLOAD_DIRECTORY = os.curdir + "/uploads"
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    app = Flask(__name__)

    # register the blueprints
    # The blueprints define API routes for request handling.
    app.register_blueprint(blueprint)

    app.config["UPLOAD_DIRECTORY"] = UPLOAD_DIRECTORY

    return app


app = create_app()

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5001))
    HOST = os.environ.get("HOST", "localhost")

    if not (HOST):
        raise Exception("No host defined")
    if not (PORT):
        raise Exception("No port defined")

    app.run(host=HOST, port=PORT, debug=False)
