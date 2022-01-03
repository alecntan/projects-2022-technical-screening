"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: This challenge is EXTREMELY hard and we are not expecting anyone to pass all
our tests. In fact, we are not expecting many people to even attempt this.
For complete transparency, this is worth more than the easy challenge. 
A good solution is favourable but does not guarantee a spot in Projects because
we will also consider many other criteria.
"""

################################################################################
"""
Strategy:

To convert the target course's 'requirement string' into a Boolean expression that
can be evaluated by Python's eval() function. This involved identifying potential operators and operands
from the strings given in conditions.json.

The implementation below  assumes the following:
    1. Target course exists within conditions.json (as given above)
    2. The only strings that can exist within a requirement are those given in conditions.json
    3. All possible 'requirement strings' follow the same rules as those given in conditions.json.
       That is, no new 'operations' are given (i.e "Has not completed COMPXXXX")
    4. Course Codes follow the regex [A-Z]{4}[0-9]{4}
    5. Course codes with only numbers (i.e. 4951) are COMP courses.
    6. There are no typos in the requirements 
    7. Course lists (COMP1511, COMP2521, ...) etc are only used for uoc purposes

"""

import json
import re

# Utility Functions

def parse_course_levels(expression, courses_completed):

    pattern = r"level ([0-9]) ([A-Z]{4}) courses"

    matches = re.findall(pattern, expression)
    for lvl, name in matches:
        pattern = r"{}{}[0-9]+".format(name, lvl)
        courses = courses_by_pattern(pattern, courses_completed)
        expression = expression.replace("level {} {} courses".format(lvl, name), courses)

    return expression

def courses_by_pattern(pattern, courses_completed):
    
    rel_courses = []
    for c in courses_completed:
        if re.match(pattern, c):
            rel_courses.append(c)

    expression = "0"
    if rel_courses:
        expression = " + ".join(rel_courses)

    return "( {} )".format(expression)

def convert_course_codes(expression, completed_courses):

    tokens = expression.split(' ')
    new_tokens = []
    for t in tokens:
        if re.match(r'[A-Z]{4}[0-9]{4}', t):
            if t in completed_courses:
                new_tokens.append('True')
            else:
                new_tokens.append('False')
        elif re.match(r'[0-9]{4}', t):
            new_t = 'COMP{}'.format(t)
            if new_t in completed_courses:
                new_tokens.append("True")
            else:
                new_tokens.append("False")
        else:
            new_tokens.append(t)


    return " ".join(new_tokens)

def remove_invalid_strings(expression):

    tokens = expression.split(' ')
    valid_strings = ['True', 'False', 'or', 'and', '+', '(', ')', '<=', '6*']

    valid_tokens = []
    for t in tokens:
        if t in valid_strings or re.match(r"^[0-9]+$", t):
            valid_tokens.append(t)

    return " ".join(valid_tokens)

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()

def is_unlocked(courses_list, target_course):
    """Given a list of course codes a student has taken, return true if the target_course 
    can be unlocked by them.
    
    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """
   
    ### Get Initial properties
    total_uoc = len(courses_list) * 6
    requirement_string = CONDITIONS[target_course]
    
    # Trivial Case (COMP1511)
    if requirement_string == '':
        return True

    # Add boundaries to parentheses, and comma for easier tokenisation
    requirement_string = requirement_string.replace('(', ' ( ').replace(')', ' ) ').replace(',', ' , ')

    # Remove extra white spaces for cleaner tokens (no empty strings in tokens array)
    requirement_string =  re.sub(r'\s+', ' ', requirement_string)

    # Add in "Operators"
    requirement_string = requirement_string.replace(',', '+') 
    requirement_string = requirement_string.replace('units of credit in', '<= 6*')
    requirement_string = requirement_string.replace('units of credit', "<= {}".format(total_uoc))
    requirement_string = requirement_string.replace('OR', 'or')
    requirement_string = requirement_string.replace('AND', 'and')
    # Expand Course Groups (ie. COMP courses, level x COMP courses etc)
    requirement_string = parse_course_levels(requirement_string, courses_list)
    # Add in operands (Booleans)
    requirement_string = convert_course_codes(requirement_string, courses_list)
    # Remove Unnecessary Strings ("Pre-Req" etc)
    requirement_string = remove_invalid_strings(requirement_string)

    return eval(requirement_string) 

if __name__ == "__main__":
    courses_list = input("Enter completed courses: ").split(" ")
    target_course = input("Enter target course: ")

    print(is_unlocked(courses_list, target_course))
