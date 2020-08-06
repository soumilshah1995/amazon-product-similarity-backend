try:
    from API import (app,api,Compute,Controller)
except Exception as e:
    print("Modules are Missing : {} ".format(e))


api.add_resource(Controller, '/compute128')


if __name__ == '__main__':
    app.run(debug=True)
