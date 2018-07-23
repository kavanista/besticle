from flask import Flask
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello world"

URL="https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid={}&format=json"

def format_output(js):
    #import pdb; pdb.set_trace()
    result = ""
    for bus in js["results"]:
        bus_route = bus["route"]
        arrival_time = bus["arrivaldatetime"]
        result += bus_route + " " + arrival_time + "<br>"
    return result

@app.route('/bus/<stopid>')
def bus_get(stopid):
    resp = requests.get(URL.format(stopid))
    if resp.status_code == 200:
        js = json.loads(resp.content)
        if js["errorcode"] == "0":
            #return json.dumps(js)
            return format_output(js)
        else:
            return "API endpoint is down: Code {}".format(js["errorcode"]) 
    return "Cannot access API endpoint"

if __name__ == '__main__':
    app.run(debug=True)
