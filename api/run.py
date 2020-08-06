try:
    from flask import Flask, request
    from flask_restful import Resource, Api, reqparse
    from flask import app,Flask, request
    from flask_restful import Resource, Api, reqparse
    import datetime
    import json
    import os
    import sys
    import numpy as np
    import ssl
    import elasticsearch
    from elasticsearch import Elasticsearch
    import tensorflow as tf
    import tensorflow_hub as hub
except Exception as e:
    print("Some Modules are Missing {}".format(e))


app = Flask(__name__)
api = Api(app)


# ------------------------------------------------------------
global ELK_ENDPOINT
global ELK_INDEX
global es

ELK_ENDPOINT =  "http://localhost:9200/"
ELK_INDEX    =  "final_project"

es = Elasticsearch(ELK_ENDPOINT, timeout=300)
ssl._create_default_https_context = ssl._create_unverified_context
# ------------------------------------------------------------

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
        print("IN")
        try:
            # Step 1: Create a instance of class
            helper  = ElasticSearchQuery(size=100, BucketName="MyBuckets")

            print("WHAT ")

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
            es = Elasticsearch(timeout=600, hosts=ELK_ENDPOINT)
            res = es.search(index=ELK_INDEX,
                            size=10,
                            body=query,
                            request_timeout=55)

            return {
                       "result":res
                   },200

        except Exception as e:
            print(e)
            return {"Message":"Error : {} ".format(e)},500


parser = reqparse.RequestParser()
parser.add_argument("what", type=str, required=True, help="This is Required Parameters ")
parser.add_argument("name", type=str, required=False, help="This is filter name ")
parser.add_argument("categories", type=str, required=False, help="Filter for Categories")
api.add_resource(Controller, '/compute128')

# -------- DONT TOUCH-------
class ElasticSearchQuery(object):

    def __init__(self, size=10, BucketName=None, source=[], min_score=0.5):

        """Constructor """

        self.size = size
        self.BucketName = BucketName
        self.min_score = min_score
        self.source = source
        self.baseQuery = {
            "_source":source,
            "size":self.size,
            "min_score": self.min_score,
            "query": {
                "bool": {
                    "must": [],
                    "filter": [],
                    "should": [],
                    "must_not": []
                }
            }
        }
        self.GeoBaseQuery =  {
            "_source":self.source,
            "size":self.size,
            "query": {
                "bool" : {
                    "must":{ "match_all":{}},
                    "should":[],
                    "filter": {}
                }
            }
        }
        self.aggtem = []
        self.base_higghlight = {
            "pre_tags":[
                "<em>"
            ],
            "post_tags":[
                "</em>"
            ],
            "tags_schema":"styled",
            "fields":{

            }
        }

    def match(self,field=None, value=None, boost=None, operation='should',analyzer=None):

        _ = {
            "match": {
                field: {
                    "query": value
                }
            }
        }
        if boost is None:
            self.baseQuery["query"]["bool"][operation].append(_)

        if boost is not None:
            _["match"][field]["boost"] = boost

        if analyzer is not None:
            _["match"][field]["analyzer"] = analyzer

        self.baseQuery["query"]["bool"][operation].append(_)

        return self.baseQuery

    def match_phrase(self, field=None, value=None, boost=None, operation='should',analyzer=None):
        _ = {
            "match_phrase": {
                field: {
                    "query": value
                }
            }
        }

        if boost is None:
            self.baseQuery["query"]["bool"][operation].append(_)

        if boost is not None:
            _["match_phrase"][field]["boost"] = boost

        if analyzer is not None:
            _["match_phrase"][field]["analyzer"] = analyzer

        self.baseQuery["query"]["bool"][operation].append(_)

        return self.baseQuery

    def terms(self,field=None, value=None, boost=None, operation='should'):

        _ = {"term" :{
            field : value
        }
        }
        self.baseQuery["query"]["bool"][operation].append(_)

    def add_aggreation(self, aggregate_name=None,
                       field=None,
                       type='terms',
                       sort='desc',
                       size = 10):

        _ = {
            aggregate_name:{
                type: {
                    "field": field,
                    "order" :
                        {"_count" :
                             sort
                         },
                    "size": size

                }
            }
        }
        self.aggtem.append(_)

    def complete_aggreation(self):
        _ = {
            "aggs":{

            }
        }
        for item in self.aggtem:
            for key,value in item.items():
                _["aggs"][key] = value
        self.baseQuery["aggs"] = _["aggs"]
        return self.baseQuery

    def add_geoqueries(self, radius=None, lat=None, lon=None, field=None, operation='filter'):
        radius = str(radius) + "mi"
        _ = {
            "geo_distance" : {
                "distance": radius,
                field : {
                    "lat": lat,
                    "lon": lon
                }
            }}
        self.baseQuery["query"]["bool"][operation].append(_)
        return self.baseQuery

    def wildcard(self,field=None, value=None, boost=None, operation=None):
        _ =  {
            "wildcard":{
                field:{
                    "value":value

                }
            }
        }
        if boost is None:
            self.baseQuery["query"]["bool"][operation].append(_)
            return self.baseQuery
        else:
            _["wildcard"][field]["boost"] = boost
            self.baseQuery["query"]["bool"][operation].append(_)
            return self.baseQuery

    def exists(self,field=None, operation="must"):

        _ = {
            "exists": {
                "field": field
            }
        }
        self.baseQuery["query"]["bool"][operation].append(_)
        return  self.baseQuery

    def query_string(self, default_field=None, query=None, operation="should"):
        _ = {
            "query_string":{
                "default_field": default_field,
                "query":"{}".format(query)
            }
        }
        self.baseQuery["query"]["bool"][operation].append(_)
        return self.baseQuery

    def add_geo_aggreation(self, field=None,lat=None, lon=None, aggregate_name='distance'):
        self.baseQuery.get("aggs")[aggregate_name] = {
            "geo_distance" : {
                "field" : field,
                "origin" : "{},{}".format(lat, lon),
                "unit" : "mi",
                "ranges" : [
                    { "to" : 0 },
                    { "from" : 0, "to" : 25 },
                    { "from" : 25, "to" : 50 },
                    { "from" : 50, "to" : 75 },
                    { "from" : 75, "to" : 100 },
                    { "from" : 100 }
                ]
            }}
        return self.baseQuery

    def match_phrase_prefix(self, field=None, value=None, boost=None, operation='should',analyzer=None):
        _ = {
            "match_phrase_prefix": {
                field: {
                    "query": value
                }
            }
        }

        if boost is not None:
            _["match_phrase_prefix"][field]["boost"] = boost
        if analyzer is not None:
            _["match_phrase_prefix"][field]["analyzer"] = analyzer
        self.baseQuery["query"]["bool"][operation].append(_)
        return self.baseQuery

    def autocomplete_1(self, field=None,size=25, value=None, sort='des', operation='must'):
        query = self.match_phrase_prefix(field=field,value=value, operation=operation)
        query  =self.add_aggreation(field=field, size=size, sort=sort,aggregate_name='auto_complete' )
        query = self.complete_aggreation()
        return query

class Tokens(object):

    def __init__(self, word):
        self.word = word

    def token(self):
        module_url = os.getcwd()
        #path = os.path.join(module_url, "API/Compute")
        embed = hub.KerasLayer(module_url)
        embeddings = embed([self.data])
        x = np.asarray(embeddings)
        x = x[0].tolist()
        return x
# ------------


if __name__ == '__main__':
    app.run(debug=True)
