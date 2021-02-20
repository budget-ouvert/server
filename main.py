from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from api import NodeHistory, FileHandler

app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(
    NodeHistory, "/node_history/<string:source>/<int:year>/<string:node_id>"
)
api.add_resource(FileHandler, "/hierarchy/<string:source>/<int:year>")


if __name__ == "__main__":
    app.run(debug=True)
