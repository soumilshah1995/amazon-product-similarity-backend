try:
    from flask import Flask
    from flask_restful import Resource, Api
    import json
    from flask import request
    import datetime
except Exception as e:
    print("Error : {} ".format(e))



app = Flask(__name__)
api = Api(app)


class Controller(Resource):
    def get(self):
        return json.dumps({"Messagesssssss ":"ok "})


api.add_resource(Controller, '/')


if __name__ == '__main__':
    app.run(host="0.0.0.0")