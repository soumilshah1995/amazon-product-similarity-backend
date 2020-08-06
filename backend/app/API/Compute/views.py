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
global es

ELK_ENDPOINT =  os.getenv("ELK_ENDPOINT","http://localhost:9200/")
ELK_INDEX    =  os.getenv("ELK_INDEX","final_project")
es = Elasticsearch(ELK_INDEX, timeout=300)
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
        self.name =  parser.parse_args().get('name', None)
        self.categories = parser.parse_args().get('categories', None)

    def get(self):
        """
        Return the JSON Response fROM ELK
        :return:
        """

        try:
            # Step 1: Create a instance of class
            helper  = ElasticSearchQuery(size=100, BucketName="MyBuckets")

            if self.what is not None:
                if len(self.what) >= 2:
                    query = helper.match(field="name", value=self.what, operation='must')

            if self.name is not None:
                if len(self.name) >= 2:
                    query = helper.match_phrase(field="name", value=self.name, operation='filter')

            if self.categories is not None:
                if len(self.categories) >= 2:
                    query = helper.match_phrase(field="categories", value=self.categories, operation='filter')

            # Aggreation Query in ELK
            helper.add_aggreation(aggregate_name="Name", field="name.keyword",type='terms',sort='desc', size=5)
            helper.add_aggreation(aggregate_name="PrimaryCategories", field="primaryCategories.keyword",type='terms',sort='desc', size=5)
            helper.add_aggreation(aggregate_name="Categories", field="categories.keyword",type='terms',sort='desc', size=5)

            query = helper.complete_aggreation()
            res = es.search(index=ELK_INDEX,
                            size=10,
                            body=query,
                            request_timeout=55)

            return {
                "result":res
            },200

        except Exception as e:
            return {"Message":"Error : {} ".format(e)},500


parser = reqparse.RequestParser()
parser.add_argument("what", type=str, required=True, help="This is Required Parameters ")
parser.add_argument("name", type=str, required=False, help="This is filter name ")
parser.add_argument("categories", type=str, required=False, help="Filter for Categories ")
