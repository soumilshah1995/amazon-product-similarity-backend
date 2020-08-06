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
    from API.Compute.queryGenerator import ElasticSearchQuery
    import elasticsearch
    from elasticsearch import Elasticsearch

except Exception as e:
    print("Error : {} ".format(e))


# ------------------------------------------------------------
global ELK_ENDPOINT
global ELK_INDEX

ELK_ENDPOINT =  os.getenv("ELK_ENDPOINT","http://localhost:9200/")
ELK_INDEX  =os.getenv("ELK_INDEX","final_project")

# ------------------------------------------------------------


app = Flask(__name__)
api = Api(app)

sys.path.append("Compute")
sys.path.append("API")
ssl._create_default_https_context = ssl._create_unverified_context


class Tokens(object):

    def __init__(self, word):
        self.word = word

    def token(self):
        module_url = os.getcwd()
        path = os.path.join(module_url, "API/Compute")
        embed = hub.KerasLayer(path)
        embeddings = embed([self.data])
        x = np.asarray(embeddings)
        x = x[0].tolist()
        return x


class Controller(Resource):

    def __init__(self):
        self.what = parser.parse_args().get('what', None)

    def get(self):
        """
        Return the JSON Response fROM ELK
        :return:
        """
        # Step 1: Create a instance of class
        helper  = ElasticSearchQuery(size=100, BucketName="MyBuckets")
        query   = helper.match(field="XXXXXXXXXXX", value="XXXXXX", operation='must')

        # Aggreation Query in ELK
        helper.add_aggreation(aggregate_name="FirstName", field="XXXXX",type='terms',sort='desc', size=3)
        helper.add_aggreation(aggregate_name="SecondName", field="XXXXX",type='terms',sort='desc', size=3)
        query = helper.complete_aggreation()
        return query

parser = reqparse.RequestParser()
parser.add_argument("what", type=str, required=True, help="This is Required Parameters ")


