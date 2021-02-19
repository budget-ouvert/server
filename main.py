from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from api import NodeHistory, FileHandler


def create_app():
    app = Flask(__name__)
    CORS(app)
    api = Api(app)

    api.add_resource(
        NodeHistory, "/node_history/<string:source>/<int:year>/<string:node_id>"
    )
    api.add_resource(FileHandler, "/hierarchy/<string:source>/<int:year>")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
