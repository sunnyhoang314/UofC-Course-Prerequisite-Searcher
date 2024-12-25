import requests
from bs4 import BeautifulSoup

def get_subject_codes_and_links(base_url):
    response = requests.get(base_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {base_url}. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")

    # Find all <a> tags
    subject_elements = soup.find_all("a", href=True)

    # Filter out unwanted entries
    excluded_texts = [
        "About the University of Calgary",
        "Academic Regulations",
        "Academic Schedule",
        "",
        "Admissions", 
        "Archives",
        "Awards and Financial Assistance",
        "Co-operative Education/Internship",
        "Contact Us",
        "Cumming School of Medicine",
        "Continuing Education"
    ]
    subjects = {}

    for element in subject_elements:
        href = element["href"]
        text = element.text.strip()
        if href.endswith(".html") and "course" not in href and text not in excluded_texts:
            subjects[text] = base_url.rsplit("/", 1)[0] + "/" + href

    return subjects


def get_courses_for_subject(subject_url):
    response = requests.get(subject_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {subject_url}. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")

    # Example selectors for course names and numbers
    course_name_elements = soup.find_all("span", id="ctl00_ctl00_pageContent_ctl05_ctl02_cnCourse")
    course_number_elements = soup.find_all("span", id="ctl00_ctl00_pageContent_ctl05_ctl02_cnCode")

    courses = [
        {
            "name": name.text.strip(),
            "number": number.text.strip(),
            "url": f"{subject_url}#{number.text.strip()}"  # Construct full course URL
        }
        for name, number in zip(course_name_elements, course_number_elements)
    ]

    return courses
