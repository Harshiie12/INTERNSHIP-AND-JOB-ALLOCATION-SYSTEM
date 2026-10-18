from flask import Flask, request
from database import get_db_connection
app=Flask(__name__)









# ================= HOME =================

@app.route("/")
def home():
    return "Internship and Job Allocation System is Running!"


# ================= STUDENTS =================

@app.route("/students")
def students():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Student")
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return str(data)


@app.route("/api/students", methods=["GET"])
def get_students():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()

    cursor.close()
    db.close()

    return {"students": students}


@app.route("/api/students", methods=["POST"])
def add_student():

    data = request.get_json()

    if data["cgpa"] < 0 or data["cgpa"] > 10:
        return {
            "message": "CGPA must be between 0 and 10"
        }, 400

    db = get_db_connection()
    cursor = db.cursor()

    sql = """
    INSERT INTO Student
    (name, email, qualification, cgpa, skills, preferred_type)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        data["name"],
        data["email"],
        data["qualification"],
        data["cgpa"],
        data["skills"],
        data["preferred_type"]
    )

    cursor.execute(sql, values)
    db.commit()

    cursor.close()
    db.close()

    return {
        "message": "Student added successfully!"
    }


# ================= OPPORTUNITIES =================

@app.route("/api/opportunities", methods=["GET"])
def get_opportunities():

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Opportunity")
    opportunities = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        "opportunities": opportunities
    }


@app.route("/api/opportunities", methods=["POST"])
def add_opportunity():

    data = request.get_json()

    db = get_db_connection()
    cursor = db.cursor()

    sql = """
    INSERT INTO Opportunity
    (company_name, opportunity_title, opportunity_type,
     required_skills, minimum_cgpa, location)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        data["company_name"],
        data["opportunity_title"],
        data["opportunity_type"],
        data["required_skills"],
        data["minimum_cgpa"],
        data["location"]
    )

    cursor.execute(sql, values)
    db.commit()

    cursor.close()
    db.close()

    return {
        "message": "Opportunity added successfully!"
    }


# ================= APPLICATIONS =================

@app.route("/api/applications", methods=["GET"])
def get_applications():

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Application")
    applications = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        "applications": applications
    }


@app.route("/api/applications", methods=["POST"])
def add_application():

    data = request.get_json()

    db = get_db_connection()
    cursor = db.cursor()

    sql = """
    INSERT INTO Application
    (student_id, opportunity_id, application_date, status)
    VALUES (%s, %s, %s, %s)
    """

    values = (
        data["student_id"],
        data["opportunity_id"],
        data["application_date"],
        data["status"]
    )

    cursor.execute(sql, values)
    db.commit()

    cursor.close()
    db.close()

    return {
        "message": "Application added successfully!"
    }


# ================= ALLOCATIONS =================

@app.route("/api/allocations", methods=["GET"])
def get_allocations():

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Allocation")
    allocations = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        "allocations": allocations
    }


@app.route("/api/allocations", methods=["POST"])
def add_allocation():

    data = request.get_json()

    db = get_db_connection()
    cursor = db.cursor()

    sql = """
    INSERT INTO Allocation
    (student_id, opportunity_id, allocation_date, status)
    VALUES (%s, %s, %s, %s)
    """

    values = (
        data["student_id"],
        data["opportunity_id"],
        data["allocation_date"],
        data["status"]
    )

    cursor.execute(sql, values)
    db.commit()

    cursor.close()
    db.close()

    return {
        "message": "Allocation added successfully!"
    }


# ================= MATCHING =================

@app.route("/api/match/<int:student_id>", methods=["GET"])
def match_opportunities(student_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get student
    cursor.execute(
        """
        SELECT *
        FROM Student
        WHERE student_id = %s
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if not student:
        cursor.close()
        db.close()

        return {
            "message": "Student not found"
        }, 404

    # Get opportunities
    # required_skills is renamed temporarily to skills
    cursor.execute(
        """
        SELECT
            opportunity_id,
            company_name,
            opportunity_title,
            opportunity_type,
            required_skills AS skills,
            minimum_cgpa,
            location
        FROM Opportunity
        """
    )

    opportunities = cursor.fetchall()

    matched = []

    # Check every opportunity
    for opportunity in opportunities:

        # CGPA matching
        cgpa_match = (
            float(student["cgpa"])
            >= float(opportunity["minimum_cgpa"])
        )

        # Skills matching
        skills_match = (
            opportunity["skills"].lower()
            in student["skills"].lower()
        )

        # Opportunity type matching
        type_match = (
            student["preferred_type"].lower()
            == opportunity["opportunity_type"].lower()
        )

        # If all conditions match
        if cgpa_match and skills_match and type_match:
            matched.append(opportunity)

    cursor.close()
    db.close()

    return {
        "student": student,
        "matched_opportunities": matched
    }
# Matching API
@app.route("/api/match/<int:student_id>", methods=["GET"])
def match_student(student_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM Student WHERE student_id = %s",
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:
        cursor.close()
        db.close()
        return {"message": "Student not found"}, 404

    cursor.execute("SELECT * FROM Opportunity")
    opportunities = cursor.fetchall()

    matches = []

    for opportunity in opportunities:

        # Check CGPA
        cgpa_match = student["cgpa"] >= opportunity["minimum_cgpa"]

        # Check skill
        student_skills = str(student["skills"]).lower()
        required_skill = str(opportunity["required_skill"]).lower()

        skill_match = required_skill in student_skills

        # Check opportunity type
        type_match = (
            str(student["preferred_type"]).lower()
            == str(opportunity["opportunity_type"]).lower()
        )

        # If all conditions match
        if cgpa_match and skill_match and type_match:
            matches.append({
                "opportunity_id": opportunity["opportunity_id"],
                "company_name": opportunity["company_name"],
                "opportunity_name": opportunity["opportunity_name"],
                "opportunity_type": opportunity["opportunity_type"],
                "required_skill": opportunity["required_skill"],
                "minimum_cgpa": opportunity["minimum_cgpa"],
                "location": opportunity["location"],
                "match": "MATCHED"
            })

    cursor.close()
    db.close()

    return {
        "student_id": student_id,
        "student_name": student["name"],
        "matches": matches
    }


if __name__ == "__main__":
    app.run(debug=True)
    


# ================= RUN APPLICATION =================

if __name__ == "__main__":
    app.run(debug=True)