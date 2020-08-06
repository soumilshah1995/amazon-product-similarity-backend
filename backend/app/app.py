
# from dotenv import load_dotenv
# load_dotenv()

try:
    from API import (app,api,Controller)
except Exception as e:
    print("Modules are Missing : {} ".format(e))


api.add_resource(Controller, '/compute128')


if __name__ == '__main__':
    app.run(debug=True)
