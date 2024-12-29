import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

def get_subject_codes_and_links(base_url: str) -> Dict[str, str]:
    response = requests.get(base_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {base_url}. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    subject_elements = soup.find_all("a", href=True)

    excluded_texts = [
        "About the University of Calgary", "Academic Regulations", "Academic Schedule", "",
        "Admissions", "Archives", "Awards and Financial Assistance", "Co-operative Education/Internship",
        "Contact Us", "Cumming School of Medicine", "Continuing Education", "Combined Degrees", "Embedded Certificates",
        "Faculty of Arts", "Faculty of Kinesiology", "Faculty of Law", "Faculty of Science", "Faculty of Nursing", 
        "Faculty of Social Work", "Faculty of Veterinary Medicine", "Faculty of Graduate Studies", "Glossary of Terms", "Haskayne School of Business",
        "Important Notice and Disclaimer", "Minor Programs", "Qatar Faculty", "School of Architecture, Planning and Landscape",
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

def get_courses_for_subject(subject_url: str) -> List[Dict]:
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

        # Get the corresponding course name by finding a related element
        course_name_span = course_number_span.find_previous("span", id=re.compile(r'ctl00_ctl00_pageContent_ctl\d{2}_ctl02_cnCourse'))
        
        if course_name_span:
            courses.append({
                "name": course_name_span.text.strip(),
                "number": course_number,
                "url": f"{subject_url}#{course_number}"
            })

    return courses

def search_prerequisites_in_subject(subject_url: str, target_course_name: str, target_course_number: str) -> List[Dict]:
    """
    Search for courses that list the target course (name and number) as a prerequisite within a subject.
    Handles cases where the name and number may appear separately and ensures association.

    Args:
        subject_url (str): The URL of the subject page to search.
        target_course_name (str): The course name (e.g., "Computer Science").
        target_course_number (str): The course number (e.g., "331").

    Returns:
        List[Dict]: Courses that list the target course as a prerequisite.
    """
    try:
        response = requests.get(subject_url)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        courses_with_prerequisite = []

        # Find all prerequisite spans
        prereq_sections = soup.find_all("span", class_="course-prereq")

        for prereq_section in prereq_sections:
            prereq_text = prereq_section.text

            # Ensure the course name and number appear together logically
            if target_course_name in prereq_text:
                # Split the prerequisite text into logical units (e.g., by "or" or "and")
                prereq_units = re.split(r'[;,]', prereq_text)  # Split by semicolon, comma, or "and"/"or"

                for unit in prereq_units:
                    # Check if both the course name and number appear in the same unit
                    if target_course_name in unit and target_course_number in unit:
                        # Find the associated course details
                        course_name_span = prereq_section.find_previous("span", id=re.compile(r'ctl00_ctl00_pageContent_ctl\d{2}_ctl02_cnCourse'))
                        course_number_span = prereq_section.find_previous("span", id=re.compile(r'ctl00_ctl00_pageContent_ctl\d{2}_ctl02_cnCode'))

                        if course_name_span and course_number_span:
                            # Extract subject code from URL
                            subject_code = subject_url.split('/')[-1].split('.')[0].upper()

                            courses_with_prerequisite.append({
                                "subject": subject_code,
                                "name": course_name_span.text.strip(),
                                "number": course_number_span.text.strip(),
                                "prereq_text": prereq_text.strip()
                            })
                        break  # Stop searching once a valid match is found

        return courses_with_prerequisite
    except Exception as e:
        print(f"Error processing {subject_url}: {str(e)}")
        return []

def get_all_courses_with_prerequisite(base_url: str, target_course_name: str, target_course_number: str) -> List[Dict]:
    """
    Search for the target course (name and number) across all subjects.

    Args:
        base_url (str): The base URL for the course calendar.
        target_course_name (str): The course name to search for (e.g., "Computer Science").
        target_course_number (str): The course number to search for (e.g., "331").

    Returns:
        List[Dict]: List of courses that have the target course as a prerequisite.
    """
    # Get all subject URLs
    subjects = get_subject_codes_and_links(f"{base_url}course-desc-main.html")
    all_courses_with_prereq = []

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Create a list of futures
        future_to_url = {
            executor.submit(search_prerequisites_in_subject, url, target_course_name, target_course_number): subject
            for subject, url in subjects.items()
        }

        # Collect results as they complete
        for future in future_to_url:
            try:
                courses = future.result()
                if courses:
                    all_courses_with_prereq.extend(courses)
            except Exception as e:
                print(f"Error processing subject: {str(e)}")

    return all_courses_with_prereq

