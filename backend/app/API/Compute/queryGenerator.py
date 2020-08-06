try:
    import os
    import sys
    import json
    print("Import : {} OK ".format(__file__))
except Exception as e:
    print("Some modules are missing {} ".format(e))


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

#
# def main():
#     helper = ElasticSearchQuery(size=100, BucketName="MyBuckets")
#
#     # match phrase
#     query=helper.match_phrase(field="myfeild", value="myvalue", operation='must')
#
#     # terms
#     query=helper.terms(field="myfeild", value="myvalue", operation='must')
#
#     # Feild Exists
#     query = helper.exists(field='comp feild', operation="must")
#
#     #Match
#     query=helper.match(field="MMMMM", value="myvalue", operation='must')
#
#     # Geo Queires
#     query = helper.add_geoqueries(radius="100", lat="22", lon="33")
#
#     # Aggreation
#     helper.add_aggreation(aggregate_name="FirstName", field="field1",type='terms',sort='desc', size=3)
#     helper.add_aggreation(aggregate_name="SecondName", field="field2",type='terms',sort='desc', size=3)
#     helper.add_aggreation(aggregate_name="ThirdName", field="field3",type='terms',sort='desc', size=3)
#     query = helper.complete_aggreation()
#     query = helper.query_string(default_field="DEFAULT",query="X OR  Y",operation='must')
#
#     query = helper.add_geo_aggreation(field="AAAA", lat="22", lon="43",aggregate_name="my_distance")
#
#     print(json.dumps(query, indent=3))
#
#
# def autocomplete():
#     helper = ElasticSearchQuery(size=0, BucketName="MyBuckets")
#     query  = helper.autocomplete_1(field="title",value="n", size=25,sort='desc')
#     print(json.dumps(query, indent=3))


