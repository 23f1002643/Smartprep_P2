import sys
import os
from datetime import datetime, time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import ns as app
from models import db, Account, Courses, CourseModule, Assessment, AssessmentProblem

def seed_data():
    with app.app_context():
        print("🚀 Seeding data...")

        # Wipe existing DB (if any)
        db.drop_all()
        db.create_all()

        # ✅ Users (admin is created in app.py)
        for i in range(1, 11):
            user = Account(
                username=f"user{i}",
                f_name=f"First{i}",
                l_name=f"Last{i}",
                pwd="pass1234",
                edu_qul="Graduate",
                mobile_no=f"99900000{i}",
                dob=datetime.strptime("2000-01-01", "%Y-%m-%d").date(),
                email=f"user{i}@test.com",
                role="user",
                active=True
            )
            db.session.add(user)

        # ✅ Subjects and Chapters
        subjects = [
            {"s_name": "Math", "remarks": "Basic Math concepts"},
            {"s_name": "Science", "remarks": "Science fundamentals"},
            {"s_name": "English", "remarks": "Grammar and Vocabulary"},
            {"s_name": "History", "remarks": "World History"},
            {"s_name": "Geography", "remarks": "Maps and Continents"},
            {"s_name": "Computer", "remarks": "Basics of computing"}
        ]

        chapters_per_subject = [
            ["Algebra", "Geometry", "Calculus", "Statistics"],
            ["Physics", "Chemistry", "Biology", "Astronomy"],
            ["Nouns", "Verbs", "Adjectives", "Adverbs"],
            ["Ancient", "Medieval", "Modern", "World Wars"],
            ["Continents", "Countries", "Climates", "Oceans"],
            ["Hardware", "Software", "Networks", "Security"]
        ]

        quiz_names = ["Quiz A", "Quiz B"]

        sample_questions = [
            {
                "statement": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct": 2
            },
            {
                "statement": "What color is the sky?",
                "options": ["Blue", "Green", "Red", "Yellow"],
                "correct": 1
            },
            {
                "statement": "Sun rises in the?",
                "options": ["North", "South", "East", "West"],
                "correct": 3
            },
            {
                "statement": "How many legs a dog has?",
                "options": ["2", "3", "4", "5"],
                "correct": 3
            },
            {
                "statement": "Water freezes at?",
                "options": ["0C", "50C", "100C", "25C"],
                "correct": 1
            }
        ]

        for s_index, subject in enumerate(subjects):
            course = Courses(s_name=subject["s_name"], remarks=subject["remarks"])
            db.session.add(course)
            db.session.flush()  # Get subject ID

            for chap_name in chapters_per_subject[s_index]:
                chapter = CourseModule(
                    subject_id=course.id,
                    name=chap_name,
                    description=f"Chapter about {chap_name}"
                )
                db.session.add(chapter)
                db.session.flush()

                for quiz_name in quiz_names:
                    quiz = Assessment(
                        q_name=quiz_name,
                        chapter_id=chapter.id,
                        date_of_quiz=datetime.today().date(),
                        time_duration=time(0, 30),
                        remarks="Simple quiz"
                    )
                    db.session.add(quiz)
                    db.session.flush()

                    for i, q in enumerate(sample_questions):
                        question = AssessmentProblem(
                            que_no=i + 1,
                            quiz_id=quiz.id,
                            statement=q["statement"],
                            opt1=q["options"][0],
                            opt2=q["options"][1],
                            opt3=q["options"][2],
                            opt4=q["options"][3],
                            cor_opt=q["correct"]
                        )
                        db.session.add(question)

        db.session.commit()
        print("✅ Data seeded successfully!")

if __name__ == "__main__":
    seed_data()
