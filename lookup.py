"""
Compulsory Task

Run SQLite and use .read create_database.sql to create a database called
HyperionDev.db.

Follow these steps by using lookup.py as a template:

    ● Create a program that allows a user to easily be able to make certain queries
      in the database. When printing, only certain fields should show on console.

    ● In addition, after each query, the user should be given the option to either
      save the resulting query in XML or JSON form. The user should also be given
      the option to choose their filename.
        ○ When saving to XML or JSON, all fields in the specified table should
          be included in the file.

    ● The user should be able to

        ○ View all subjects being taken by a specified student (search by
          student_id).
            ■ On console, the subject name should only be shown

        ○ Look up an address given a first name and a surname.
            ■ Only the street name and city should be shown on the console.

        ○ List all reviews given to a student (search by student_id).
            ■ The completeness, efficiency, style and documentation scores
              should be displayed on console, along with the review text.

        ○ List all courses being given by a specific teacher (search by
          teacher_id).
            ■ Just the course name should be displayed on the console.

        ○ List all students who haven’t completed their course.
            ■ The student number, first and last names, email addresses and
              course names should be shown on the console.

        ○ List all students who have completed their course and achieved a
          mark of 30 or below.
            ■ The student number, first and last names, email addresses and
              course names should be shown on the console. Their marks
              should also be displayed
"""
# importing all necessary modules to run the scripts
import sqlite3
import json
import xml.etree.ElementTree as ET

# try/except created to catch errors when starting the program
try:
    conn = sqlite3.connect("HyperionDev.db")
    with open("create_database.sql", "r") as sql_file:
        conn.executescript(sql_file.read())  # reading the sql script

except sqlite3.Error:
    print("Please store your database as HyperionDev.db")
    quit()

cur = conn.cursor()  # to create SQL queries in the program


# storing the data in a json file
# I got steer from the previous Task: Data Sources, on how to execute this
def store_data_as_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, sort_keys=True, indent=4)


# storing the data in a xml file
# I got steer from the following URLs:
# https://www.tutorialspoint.com/create-xml-documents-using-python
#
def store_data_as_xml(data, filename):
    root = ET.Element('root')
    results = ET.SubElement(root, 'results')
    results.text = str(data)  # casting data type to string as data is a list type
    tree = ET.ElementTree(root)
    tree.write(filename)


# calling the function to store the data in either xml or json files
def offer_to_store(data):
    while True:
        print("\nWould you like to store this result?")
        choice = input("Y/[N]? : ").strip().lower()

        if choice == "y":
            filename = input("Specify filename. Must end in .xml or .json: ")
            ext = filename.split(".")[-1]
            if ext == 'xml':
                store_data_as_xml(data, filename)
            elif ext == 'json':
                store_data_as_json(data, filename)
            else:
                print("Invalid file extension. Please use .xml or .json")

        elif choice == 'n':
            break

        else:
            print("Invalid choice")


# menu selection option
usage = '''
-------------------------------------------------------------------------------------------------------
What would you like to do?

d                          - demo
vs <student_id>            - view subjects taken by a student
la <firstname> <surname>   - lookup address for a given firstname and surname
lr <student_id>            - list reviews for a given student_id
lc <teacher_id>            - list all courses taken by teacher_id
lnc                        - list all students who haven't completed their course
lf                         - list all students who have completed their course and achieved 30 or below
e                          - exit this program

Type your option here : '''

print("\n                                 Welcome to the data querying app!")

while True:
    # Get input from user
    user_input = input(usage)
    print()

    # Parse user input into command and args
    command = user_input

    if command == 'd':  # demo - a nice bit of code from me to you - this prints all student names and surnames :)
        # NB! The demo command is not my code, it is part of the template. I have left the above comment
        # as a reference point from the person who wrote this template
        data = cur.execute("SELECT * FROM Student")
        for _, firstname, surname, _, _ in data:
            print(f"{firstname} {surname}")

    elif command == 'vs':  # view subjects by student_id
        student_id = input('Enter the student_id  : ')
        cur.execute("""
            SELECT course_name AS Subjects
            FROM Course AS c
            INNER JOIN StudentCourse AS s
            ON c.course_code = s.course_code
            WHERE s.student_id = ?""", (student_id,))
        data = cur.fetchall()
        if data:
            print(f"""
Subjects listed for student_id: {student_id}
---------------------------------------------""")
            for subject in data:
                print(subject[0])
        else:
            print(f"\nNo subjects found for given student_id: {student_id}")

        offer_to_store(data)

    elif command == 'la':  # list address by name and surname
        # for the UNION keyword I got reference from W3Schools
        # as I was getting an ambiguous column name error in sql for the first_name attribute
        # I had to create the same SQL query for both student and teacher tables
        # and combine the two to avoid the Ambiguous Column Name Error I was getting
        firstname = input('Enter the firstname   : ')
        surname = input('Enter the surname     : ')
        cur.execute("""
            SELECT a.street, a.city
            FROM Address a
            JOIN Student s ON s.address_id = a.address_id
            WHERE s.first_name = @first_name AND s.last_name = @last_name
            UNION
            SELECT a.street, a.city
            FROM Address a
            JOIN Teacher t ON t.address_id = a.address_id
            WHERE t.first_name = @first_name AND t.last_name = @last_name;
        """, (firstname, surname))
        data = cur.fetchone()
        if data:
            print(f"""
Address listed for: {firstname} {surname}
---------------------------------------------""")
            print(f"{data[0]} {data[1]}")
        else:  # if the name and surname is not in the database
            print(f"\nNo address found for given name and surname: {firstname} {surname}")

        offer_to_store(data)

    elif command == 'lr':  # list reviews by student_id
        student_id = input('Enter the student_id  : ')
        cur.execute("""
            SELECT completeness, efficiency, style, documentation, review_text
            FROM Review
            WHERE student_id = ?
        """, (student_id,))
        data = cur.fetchall()
        if data:
            print(f"""
Reviews posted for student_id: {student_id}
---------------------------------------------""")
            for review in data:
                print(f"Completeness Score  : {review[0]}")
                print(f"Efficiency Score    : {review[1]}")
                print(f"Style Score         : {review[2]}")
                print(f"Documentation Score : {review[3]}")
                print(f"Review Text         : {review[4]}")
                print("-----------------------------------")
        else:
            print(f"\nNo reviews found for given student_id: {student_id}")

        offer_to_store(data)

    elif command == 'lc':  # list courses by teacher_id
        teacher_id = input('Enter the teacher_id  : ')
        cur.execute("""
            SELECT course_name
            FROM Course
            WHERE teacher_id = ?
        """, (teacher_id,))
        data = cur.fetchall()
        if data:
            print(f"""
List of courses by teacher_id: {teacher_id}
---------------------------------------------""")
            for course in data:
                print(course[0])
        else:
            print(f"\nNo courses found for given teacher_id: {teacher_id}")

        offer_to_store(data)

    elif command == 'lnc':  # list all students who haven't completed their course
        cur.execute("""
        SELECT Student.student_id, Student.first_name, Student.last_name, 
        Student.email, Course.course_name
        FROM Student
        INNER JOIN StudentCourse ON Student.student_id = StudentCourse.student_id
        INNER JOIN Course ON StudentCourse.course_code = Course.course_code
        WHERE StudentCourse.is_complete = 0;""")

        data = cur.fetchall()
        if data:
            for student in data:
                print(f"Student Number  : {student[0]}")
                print(f"First Name      : {student[1]}")
                print(f"Surname         : {student[2]}")
                print(f"Email           : {student[3]}")
                print(f"Course Name     : {student[4]}")
                print("---------------------------------")

        else:
            print("\nNo incomplete students found")

        offer_to_store(data)

    elif command == 'lf':  # list all students who have completed their course and got a mark <= 30
        cur.execute("""
        SELECT Student.student_id, Student.first_name, Student.last_name, Student.email, 
        Course.course_name, StudentCourse.mark
        FROM Student
        INNER JOIN StudentCourse ON Student.student_id = StudentCourse.student_id
        INNER JOIN Course ON StudentCourse.course_code = Course.course_code
        WHERE StudentCourse.is_complete = 1 AND StudentCourse.mark <= 30
        """)
        data = cur.fetchall()
        if data:
            for student in data:
                print(f"Student Number  : {student[0]}")
                print(f"First Name      : {student[1]}")
                print(f"Surname         : {student[2]}")
                print(f"Email           : {student[3]}")
                print(f"Course Name     : {student[4]}")
                print(f"Mark            : {student[5]}")
                print("---------------------------------")

        else:  # if the data changes for the students to all pass
            print("\nNo failed students found")

        offer_to_store(data)

    elif command == 'e':  # exit program
        print('''Programme exited successfully!
-------------------------------------------------------------------------------------------------------''')
        break

    else:  # invalid entry
        print(f"\nIncorrect command: '{command}'")

conn.commit()  # committing all changes
conn.close()  # closing the database connection

# Where I struggled to implement from the sql queries. So, I referenced back to these URLs:
# https://www.w3schools.com/sql/default.asp
# https://www.youtube.com/watch?v=byHcYRpMgI4&t=4173s&ab_channel=freeCodeCamp.org

# I got the coding reference to read the sql file from the following URL
# https://www.youtube.com/watch?v=xkKvJVs3DR8&ab_channel=SeanMacKenzieDataEngineering

# XML reference:
# https://www.tutorialspoint.com/create-xml-documents-using-python

# 17/08/2023 - Thank you, Lucille for the mentor session, advise and detailed feedback,
# I appreciate all your help muchness :)

# Hi Kenneth Mlimi,
# There seems to be a misunderstanding based on your feedback.
# I have now copied my code in the lookup.py template for ease of reference.
# I hope this now satisfies the requirements you need for grading.
# Thank you, Farinaaz :)
