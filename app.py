from flask import Flask, request, jsonify, render_template
from scraper import get_subject_codes_and_links, get_courses_for_subject

app = Flask(__name__)

BASE_URL = "https://www.ucalgary.ca/pubs/calendar/archives/2020/"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/subject-codes", methods=["GET"])
def fetch_subject_codes():
    try:
        subject_codes = get_subject_codes_and_links(f"{BASE_URL}course-desc-main.html")
        return jsonify(subject_codes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/courses", methods=["GET"])
def fetch_courses():
    subject_url = request.args.get("url")
    if not subject_url:
        return jsonify({"error": "No subject URL provided"}), 400

    try:
        courses = get_courses_for_subject(subject_url)
        return jsonify(courses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
