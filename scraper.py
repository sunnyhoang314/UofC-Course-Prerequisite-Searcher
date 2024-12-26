import requests
from bs4 import BeautifulSoup
import re

def get_subject_codes_and_links(base_url):
    response = requests.get(base_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {base_url}. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    subject_elements = soup.find_all("a", href=True)

    excluded_texts = [
        "About the University of Calgary", "Academic Regulations", "Academic Schedule", "",
        "Admissions", "Archives", "Awards and Financial Assistance", "Co-operative Education/Internship",
        "Contact Us", "Cumming School of Medicine", "Continuing Education", "Combined Degrees", "Embedded Certificates",
        "Faculty of Arts, Faculty of Kinesiology", "Faculty of Law", "Faculty of Science", "Faculty of Nursing", 
        "Faculty of Social Work", "Faculty of Veterinary Medicine", "Glossary of Terms", "Haskayne School of Business",
        "Importtant Notice and Disclaimer", "Minor Programs", "Qatar Faculty", "School of Architecture, Planning and Landscape",
        "Schulich School of Engineering", "Student and Campus Services", "Summary of Changes for 2020/21 Calendar", 
        "Tuition and General Fees", "Types of Credentials and Sub-Degree Nomenclature", "Undergraduate Degrees with a Major", 
        "University of Calgary Calendar 2020-2021", "Welcome", "Werklund School of Education", "Who's Who"
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
    
    # Find all span tags that have an id matching the pattern for course numbers
    course_number_elements = soup.find_all("span", id=re.compile(r'ctl00_ctl00_pageContent_ctl\d{2}_ctl02_cnCode'))

    courses = []

    # Loop through each course number element and retrieve the course number
    for course_number_span in course_number_elements:
        course_number = course_number_span.text.strip()

        # Get the corresponding course name by finding a related element (adjust as necessary)
        course_name_span = course_number_span.find_previous("span", id=re.compile(r'ctl00_ctl00_pageContent_ctl\d{2}_ctl02_cnCourse'))
        
        if course_name_span:
            courses.append({
                "name": course_name_span.text.strip(),
                "number": course_number,
                "url": f"{subject_url}#{course_number}"
            })

    return courses
