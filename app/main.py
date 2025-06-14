# app/main.py
from flask import Flask, request, jsonify, render_template
from recommender import recommend_jobs
import json

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        raw_data = request.get_data(as_text=True)
        data = json.loads(raw_data)
        query = data.get("query", "").strip()
        if not query:
            return jsonify({"error": "Missing 'query' field"}), 400

        results = recommend_jobs(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
