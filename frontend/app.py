try:
    from flask import Flask
    from flask import request,redirect,render_template,session
    import requests
    import base64
    import requests
except Exception as e:
    print('Error : {} '.format(e))

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template("home.html")


@app.route('/search', methods=["GET", "POST"])
def search():

    what = request.form.get("what")
    print("WHAT : {} ".format(what))
    url = "http://localhost:5000/search?what="+what
    r = requests.get(url)
    r = r.json()
    return r



@app.route('/pipe', methods=["GET", "POST"])
def pipe():
    data = request.form.get("data")
    payload = {}
    headers= {}
    url = "http://localhost:5000/autocomplete?what="+str(data)
    response = requests.request("GET", url, headers=headers, data = payload)
    return response.json()



if __name__ == "__main__":
    app.run(debug=True, port=4000)