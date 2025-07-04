from flask import Flask, jsonify, request
import requests
from shapely.geometry import shape, mapping
import geojson
import os

app = Flask(__name__)

PAZP_API = "https://airspace.pansa.pl/api/public/aup"

@app.route("/aup", methods=["GET"])
def get_aup():
    date = request.args.get("date")  # może być None

    if date:
        url = f"{PAZP_API}/{date}"
    else:
        url = PAZP_API  # bez daty – API zwraca dane na dziś

    resp = requests.get(url)

    if resp.status_code != 200:
        return jsonify({
            "error": "PAŻP API error",
            "status": resp.status_code,
            "url": url
        }), 500

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

    return jsonify(geojson.FeatureCollection(features))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # domyślnie 5000, ale Render poda PORT
    app.run(host="0.0.0.0", port=port)
