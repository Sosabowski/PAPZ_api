from flask import Flask, jsonify, request
import requests
from shapely.geometry import shape, mapping
import geojson

app = Flask(__name__)

PAZP_API = "https://airspace.pansa.pl/api/public/aup"

@app.route("/aup", methods=["GET"])
def get_aup():
    date = request.args.get("date")  # format YYYY-MM-DD
    if not date:
        return jsonify({"error": "Missing 'date' param"}), 400

    url = f"{PAZP_API}/{date}"
    resp = requests.get(url)

    if resp.status_code != 200:
        return jsonify({"error": "PAŻP API error"}), 500

    raw_data = resp.json()
    features = []

    for item in raw_data.get("areas", []):
        geometry = shape(item["geometry"])
        props = {
            "name": item.get("name"),
            "class": item.get("class"),
            "activity": item.get("activity"),
            "lower_limit": item.get("lower_limit"),
            "upper_limit": item.get("upper_limit"),
        }
        feature = geojson.Feature(geometry=mapping(geometry), properties=props)
        features.append(feature)

    feature_collection = geojson.FeatureCollection(features)
    return jsonify(feature_collection)

if __name__ == "__main__":
    app.run(debug=True)
