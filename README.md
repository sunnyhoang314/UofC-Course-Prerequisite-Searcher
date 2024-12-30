# UofC Course Prerequisite Searcher

This tool allows students at the University of Calgary to easily find courses that require a specific course as a prerequisite. It scrapes the UofC course catalog to gather prerequisite data and presents it in a user-friendly interface.

## Features

- Web scrapes the UofC course catalog for prerequisite information.
- Displays courses that require a given course as a prerequisite.
- Provides a simple search interface for easy use.

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/sunnyhoang314/UofC-Course-Prerequisite-Searcher.git
    ```

2. Navigate to the project directory:
    ```bash
    cd UofC-Course-Prerequisite-Searcher
    ```

3. Install the necessary dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the scraper:
    ```bash
    python scraper.py
    ```

2. Start the web interface:
    ```bash
    python app.py
    ```

3. Open your browser and go to `http://localhost:5000` to access the course prerequisite search.

## TODO

1. Update to the most recent academic calendar regulations (2024 - 2025).
2. Indicate whether or not this course is required for your major.
