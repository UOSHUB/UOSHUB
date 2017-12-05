from lxml.etree import fromstring as __parse_xml


# Scrapes possible values of ["Campus", "College", "Department"] from offered courses report
def values_of(courses, *params):
    # For each supported value, create an empty dictionary in values for later use
    values = {param: {} for param in params if param in ["Campus", "College", "Department"]}
    # Loop through courses to get the required values
    for course in __parse_xml(courses).find("LIST_G_SSBSECT_TERM_CODE"):
        # If campus values are required
        if "Campus" in values:
            # Add course's campus to values as {"campus name": "campus abbreviation"}
            values["Campus"].update({course.find("CAMPUS_DESC").text: course.find("SSBSECT_CAMP_CODE").text})
        # If college values are required
        if "College" in values:
            # Add course's college to values as {"college name": "college number"}
            values["College"].update({course.find("COLLEGE_NAME").text: course.find("SCBCRSE_COLL_CODE").text})
        # If department values are required
        if "Department" in values:
            # Add course's department to values as {"department name": "department initials"}
            values["Department"].update({course.find("DEPT_NAME").text: course.find("SCBCRSE_DEPT_CODE").text})
    return values


# Scrapes possible values of "Majors" from students' schedule
def values_of_majors(schedules):
    return {
        # Add student's major from his schedule as {"major name": "major initials"}
        schedule.find("CF_MAJR_DESC").text: schedule.find("SGBSTDN_MAJR_CODE_1").text
        # Loop through each schedule from schedules report
        for schedule in __parse_xml(schedules).find("LIST_G_STVCOLL_DESC")
    }