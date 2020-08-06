
__Author__ = 'Soumil Nitin Shah '
__Version__ = '2.0.0'
__Email__ = "s.shah@jobtarget.com"


try:
    from flask import Flask, request
    from flask_restful import Resource, Api, reqparse
    from API.Compute.views import Controller

except Exception as e:
    print("Some Modules are Missing {}".format(e))


app = Flask(__name__)
api = Api(app)



