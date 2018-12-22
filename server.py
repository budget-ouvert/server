from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from api.plf import NodeHistory


app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(NodeHistory, '/node_history/<int:year>/<string:node_id>')

if __name__ == '__main__':
    app.run(debug=True)
