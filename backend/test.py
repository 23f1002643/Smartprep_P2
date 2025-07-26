# import sys
# import os
# from datetime import datetime, time

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from app import ns as app
# from backend.models import db, Account, Courses, CourseModule, Assessment, AssessmentProblem
# def add_sample_data():
#     with app.app_context():
#         if Courses.query.filter_by(s_name="Math").first():
#             print("✅ Sample data already exists. No new data was added.")
#             return

#         print("🚀 Seeding new sample data into the database...")

#         for i in range(1, 11):
#             user = Account(
#                 username=f"user{i}", f_name=f"First{i}", l_name=f"Last{i}", pwd="pass1234",
#                 edu_qul="Graduate", mobile_no=f"99900000{i:02d}", dob=datetime.strptime("2000-01-01", "%Y-%m-%d").date(),
#                 email=f"user{i}@test.com", role="user", active=True
#             )
#             db.session.add(user)

#         seed_data_structure = [
#             {
#                 "subject": {"s_name": "Math", "remarks": "Basic Math concepts"},
#                 "chapters": ["Algebra", "Geometry"]
#             },
#             {
#                 "subject": {"s_name": "Science", "remarks": "Science fundamentals"},
#                 "chapters": ["Physics", "Chemistry"]
#             }
#         ]
        
#         unique_questions_by_chapter = {
#             "Algebra": [
#                 {"statement": "What is x in 2x + 3 = 7?", "options": ["1", "2", "3", "4"], "correct": 2},
#                 {"statement": "Solve: x² = 49", "options": ["5", "6", "7", "8"], "correct": 3},
#                 {"statement": "Which is a linear equation?", "options": ["x² + 1", "2x + 3", "x³ - x", "x² + x + 1"], "correct": 2},
#                 {"statement": "Factor of x² - 9?", "options": ["(x+3)(x-3)", "(x-3)(x-3)", "(x+3)(x+3)", "None"], "correct": 1},
#                 {"statement": "Degree of x² + 5x + 6?", "options": ["1", "2", "3", "0"], "correct": 2},
#                 {"statement": "What is 2(x + 3)?", "options": ["2x + 6", "x + 6", "2x + 3", "x + 3"], "correct": 1},
#                 {"statement": "x - 4 = 0, x is?", "options": ["4", "-4", "0", "1"], "correct": 1},
#                 {"statement": "Which is a polynomial?", "options": ["x", "x/2", "√x", "log x"], "correct": 1},
#                 {"statement": "Solve: 5x = 20", "options": ["5", "4", "3", "2"], "correct": 2},
#                 {"statement": "x² + 2x + 1 = ?", "options": ["(x+1)²", "(x-1)²", "x²", "x² + 1"], "correct": 1}
#             ],
#             "Geometry": [
#                 {"statement": "Sum of angles in triangle?", "options": ["90°", "180°", "360°", "270°"], "correct": 2},
#                 {"statement": "A square has how many sides?", "options": ["3", "4", "5", "6"], "correct": 2},
#                 {"statement": "Right angle = ?", "options": ["45°", "90°", "180°", "60°"], "correct": 2},
#                 {"statement": "Diagonal of square divides it into?", "options": ["Two squares", "Two triangles", "Four triangles", "None"], "correct": 2},
#                 {"statement": "Area of rectangle formula?", "options": ["l + b", "2l + 2b", "l × b", "l ÷ b"], "correct": 3},
#                 {"statement": "Circle's boundary is called?", "options": ["Radius", "Diameter", "Circumference", "Arc"], "correct": 3},
#                 {"statement": "Diameter is ___ times radius?", "options": ["1", "2", "3", "4"], "correct": 2},
#                 {"statement": "360° angle is a?", "options": ["Straight angle", "Reflex angle", "Full rotation", "Acute angle"], "correct": 3},
#                 {"statement": "Isosceles triangle has?", "options": ["3 equal sides", "2 equal sides", "All different", "None"], "correct": 2},
#                 {"statement": "Line connecting center to circle?", "options": ["Radius", "Chord", "Tangent", "Arc"], "correct": 1}
#             ],
#             "Physics": [
#                 {"statement": "Unit of Force?", "options": ["Joule", "Pascal", "Newton", "Watt"], "correct": 3},
#                 {"statement": "Gravity on Earth?", "options": ["8.9", "9.8", "10.5", "12"], "correct": 2},
#                 {"statement": "Speed = ?", "options": ["Distance × Time", "Distance / Time", "Time / Distance", "None"], "correct": 2},
#                 {"statement": "Light travels in?", "options": ["Curved path", "Straight line", "Zigzag", "All"], "correct": 2},
#                 {"statement": "Sound needs?", "options": ["Vacuum", "Medium", "No medium", "Space"], "correct": 2},
#                 {"statement": "Energy stored in food?", "options": ["Potential", "Thermal", "Chemical", "Mechanical"], "correct": 3},
#                 {"statement": "SI unit of power?", "options": ["Watt", "Joule", "Newton", "Ampere"], "correct": 1},
#                 {"statement": "Heat transfer by fluid?", "options": ["Conduction", "Radiation", "Convection", "Fusion"], "correct": 3},
#                 {"statement": "Magnet attracts?", "options": ["Wood", "Plastic", "Iron", "Rubber"], "correct": 3},
#                 {"statement": "Force causes?", "options": ["Rest", "Motion", "Both", "None"], "correct": 3}
#             ],
#             "Chemistry": [
#                 {"statement": "Water formula?", "options": ["H2O", "CO2", "O2", "CH4"], "correct": 1},
#                 {"statement": "Atomic number of oxygen?", "options": ["6", "7", "8", "9"], "correct": 3},
#                 {"statement": "NaCl is?", "options": ["Baking soda", "Salt", "Sugar", "Lime"], "correct": 2},
#                 {"statement": "Gas used in soft drinks?", "options": ["O2", "CO2", "H2", "N2"], "correct": 2},
#                 {"statement": "Acids taste?", "options": ["Sweet", "Salty", "Sour", "Bitter"], "correct": 3},
#                 {"statement": "Litmus turns red in?", "options": ["Base", "Acid", "Neutral", "Water"], "correct": 2},
#                 {"statement": "Common base?", "options": ["HCl", "NaOH", "CO2", "H2O"], "correct": 2},
#                 {"statement": "Periodic table creator?", "options": ["Newton", "Mendeleev", "Einstein", "Bohr"], "correct": 2},
#                 {"statement": "Atoms combine to form?", "options": ["Compounds", "Mixtures", "Solutions", "Alloys"], "correct": 1},
#                 {"statement": "Most reactive metal?", "options": ["Iron", "Sodium", "Gold", "Copper"], "correct": 2}
#             ]
#         }
#         quiz_names = ["Quiz A", "Quiz B"]

#         for item in seed_data_structure:
#             subject_data = item["subject"]
#             course = Courses(s_name=subject_data["s_name"], remarks=subject_data["remarks"])
#             db.session.add(course)
#             db.session.flush()

#             for chap_name in item["chapters"]:
#                 chapter = CourseModule(
#                     subject_id=course.id, name=chap_name,
#                     description=f"Chapter about {chap_name}"
#                 )
#                 db.session.add(chapter)
#                 db.session.flush()

#                 chapter_questions = unique_questions_by_chapter.get(chap_name, [])

#                 for q_index, quiz_name in enumerate(quiz_names):
#                     quiz = Assessment(
#                         q_name=f"{chap_name} - {quiz_name}", chapter_id=chapter.id,
#                         date_of_quiz=datetime.today().date(), time_duration=time(0, 30),
#                         remarks="Auto-generated quiz"
#                     )
#                     db.session.add(quiz)
#                     db.session.flush()

#                     start_index = q_index * 5
#                     selected_questions = chapter_questions[start_index:start_index + 5]

#                     for i, q in enumerate(selected_questions):
#                         question = AssessmentProblem(
#                             que_no=i + 1, quiz_id=quiz.id, statement=q["statement"],
#                             opt1=q["options"][0], opt2=q["options"][1],
#                             opt3=q["options"][2], opt4=q["options"][3],
#                             cor_opt=q["correct"]
#                         )
#                         db.session.add(question)

#         db.session.commit()
#         print("✅ New data has been successfully added to the database!")

# if __name__ == "__main__":
#     add_sample_data()