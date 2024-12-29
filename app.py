from flask import Flask, request, jsonify, render_template
from scraper import get_subject_codes_and_links, get_courses_for_subject, get_all_courses_with_prerequisite

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

@app.route("/all-courses-with-prerequisite", methods=["GET"])
def fetch_all_courses_with_prerequisite():
    course_name = request.args.get("name")
    course_number = request.args.get("number")

    if not course_name or not course_number:
        return jsonify({"error": "Both course name and number are required"}), 400

    try:
        courses = get_all_courses_with_prerequisite(BASE_URL, course_name, course_number)
        return jsonify({"courses": courses})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)