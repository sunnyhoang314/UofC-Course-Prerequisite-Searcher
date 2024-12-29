// script.js

// Fetch subjects and populate the dropdown
async function fetchSubjects() {
    const response = await fetch("/subject-codes");
    const data = await response.json();

    const subjectDropdown = document.getElementById("subjectDropdown");
    Object.keys(data).forEach(subject => {
        const option = document.createElement("option");
        option.value = data[subject];
        option.textContent = subject;
        subjectDropdown.appendChild(option);
    });
}

// Fetch courses when a subject is selected
async function fetchCourses() {
    const subjectUrl = document.getElementById("subjectDropdown").value;
    const response = await fetch(`/courses?url=${encodeURIComponent(subjectUrl)}`);
    const data = await response.json();

    const courseDropdown = document.getElementById("courseDropdown");
    courseDropdown.innerHTML = '<option value="" disabled selected>Select a course</option>';

    if (response.ok) {
        data.forEach(course => {
            const option = document.createElement("option");
            option.value = course.number;
            option.textContent = `${course.name} ${course.number}`;
            courseDropdown.appendChild(option);
        });
    } else {
        alert(data.error);
    }
}

// Fetch courses that list the selected course as a prerequisite across all subjects
async function fetchAllPrerequisiteForCourses() {
    const courseDropdown = document.getElementById("courseDropdown");
    const selectedOption = courseDropdown.options[courseDropdown.selectedIndex];
    
    // Extract course name and number from the dropdown text
    const courseName = selectedOption.text.split(" ").slice(0, -1).join(" "); // E.g., "Computer Science"
    const courseNumber = selectedOption.text.split(" ").pop(); // E.g., "331"

    const loadingIndicator = document.getElementById("loadingIndicator");
    const resultList = document.getElementById("prerequisiteForList");

    loadingIndicator.style.display = "block";
    resultList.innerHTML = ""; // Clear previous results

    try {
        const response = await fetch(`/all-courses-with-prerequisite?name=${encodeURIComponent(courseName)}&number=${courseNumber}`);
        const data = await response.json();

        if (response.ok && data.courses) {
            if (data.courses.length === 0) {
                resultList.innerHTML = "<li>No courses found that list this as a prerequisite.</li>";
            } else {
                data.courses.forEach(course => {
                    const listItem = document.createElement("div");
                    listItem.className = "prerequisite-item";
                    listItem.innerHTML = `
                        <strong>${course.subject} ${course.number}</strong> - ${course.name}
                        <div class="prereq-text">Prerequisites: ${course.prereq_text}</div>
                    `;
                    resultList.appendChild(listItem);
                });
            }
        } else {
            resultList.innerHTML = `<li>${data.error || "An error occurred while searching for prerequisites."}</li>`;
        }
    } catch (error) {
        resultList.innerHTML = `<li>Error: ${error.message}</li>`;
    } finally {
        loadingIndicator.style.display = "none";
    }
}

// Initialize subject dropdown on page load
window.onload = fetchSubjects;
