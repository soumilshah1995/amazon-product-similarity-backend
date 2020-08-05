try:
    from flask import app,Flask, request
    from flask_restful import Resource, Api, reqparse
    import datetime
    import json
    import os
    import sys
    import tensorflow as tf
    import tensorflow_hub as hub
    import numpy as np
    import ssl
except Exception as e:
    pass

app = Flask(__name__)
api = Api(app)

sys.path.append("Compute")
sys.path.append("API")
ssl._create_default_https_context = ssl._create_unverified_context


class Compute(Resource):

    def __init__(self):
        self.data = parser.parse_args().get('data', None)

    def get(self):
        module_url = os.getcwd()
        path = os.path.join(module_url, "API/Compute")
        embed = hub.KerasLayer(path)
        embeddings = embed([self.data])
        x = np.asarray(embeddings)
        x = x[0].tolist()
        return {"vector": x}


parser = reqparse.RequestParser()
parser.add_argument("data", type=str, required=True, help="This is Required Parameters ")


