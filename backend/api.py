from flask_restful import Resource, reqparse
from flask_jwt_extended import get_jwt, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask import request, jsonify, current_app as ns, session
from backend.models import db, Account, Courses, CourseModule, Assessment, AssessmentProblem, ExamPerformance
from datetime import datetime 
from flask_caching import Cache
from backend.config import config_settings
from sqlalchemy import func
from backend.tasks import *
caching = Cache(config={'CACHE_TYPE': 'SimpleCache'})

class AccountRegisterAPI(Resource):  
    def post(self):
        info = request.get_json()
        if not info:
            return {'message': 'Missing JSON payload'}, 400
        required_fields = ['f_name', 'l_name', 'pwd', 'username', 'email', 'mobile_no', 'edu_qul', 'dob']
        
        if not all(info.get(field) for field in required_fields):
            return {'message': 'Please fill all required fields!'}, 400

        if Account.query.filter_by(username=info['username']).first():
            return {'message': 'Username already exists!'}, 409  # Conflict
        
        new_user = Account(
            username=info['username'],
            pwd=info['pwd'],
            f_name=info['f_name'],
            l_name=info['l_name'],
            edu_qul=info['edu_qul'],
            dob=datetime.strptime(info['dob'], '%Y-%m-%d').date(),
            mobile_no=info['mobile_no'],
            email=info['email'],
            role='user',
            active=True
        ) 
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'Registration successful! Please login.'}, 201 # Created

class AccountLoginAPI(Resource):
    @jwt_required(optional=True)
    def post(self):
        cur_user = get_jwt_identity()
        if cur_user :
            return {
                "msg": "Already logged in",
                "user": cur_user
            }, 200

        info = request.json
        if not info:
            return {"msg": "Missing JSON payload"}, 400

        username = info.get('username')
        pwd = info.get('password')
        print(f"Login attempt with username: {username} and {pwd}")  # Debugging line to check username
        if not username or not pwd:
            return {"msg": "Username and password are required"}, 400

        user = Account.query.filter_by(username=username).first()
        print(f"Comparing request pwd: {repr(pwd)}")
        print(f"With database pwd:   {repr(user.pwd)}")
        if user and user.pwd == pwd:
            tkn = create_access_token(identity=str(user.id),additional_claims={"name": user.username,"role": user.role})
            print(f"User {user.username} logged in successfully. on {datetime.now()}")
            return {
                "msg": "Login successful",
                "user": {
                    "id": user.id,
                    "name": user.username,
                    "role": user.role
                },
                "access_token": tkn
            }, 200
        
        return {"msg": "Invalid username or password"}, 401

jwt_blocklist = config_settings['JWT_BLOCKLIST']
class AccountLogoutAPI(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        jwt_blocklist.add(jti)
        # session.clear()
        print(f"Token {jti} added to blocklist")
        return {"msg": "You have been Logged out successfully!"}, 200
# class AccountDashboardAPI(Resource):
#     @jwt_required()
#     @caching.cached(timeout=60)
#     def get(self):
#         claims = get_jwt()
#         today = datetime.now().date()
#         assessments = Assessment.query.filter(Assessment.date_of_quiz >= today).all()
#         subjects = Courses.query.all()
#         modules = CourseModule.query.all()
#         quts = AssessmentProblem.query.all()
#         users = Account.query.all()
#         performances = ExamPerformance.query.all()
#         if claims.get('role') == 'admin':
#             return {
#                 'quizzes': [
#                     {
#                         'id': a.id,
#                         'name': a.q_name,
#                         'date': a.date_of_quiz.strftime('%Y-%m-%d'), 
#                         'time': a.time_duration.strftime('%H:%M:%S'),  
#                         'remarks': a.remarks
#                     } for a in assessments
#                 ],
#                 'subjects': [{'id': s.id, 'name': s.s_name} for s in subjects],
#                 'modules': [{'id': m.id, 'name': m.name, 'subject_id': m.subject_id} for m in modules],
#                 'quts': [
#                     {
#                         'id': q.id,
#                         'que_no': q.que_no,
#                         'statement': q.statement,
#                         'opt1': q.opt1,
#                         'opt2': q.opt2,
#                         'opt3': q.opt3,
#                         'opt4': q.opt4,
#                         'cor_opt': q.cor_opt
#                     } for q in quts
#                 ],
#                 'users': [{'id': u.id, 'username': u.username, 'role': u.role} for u in users],
#                 'scores': [
#                     {
#                         'id': p.id,
#                         'user_id': p.user_id,
#                         'quiz_id': p.quiz_id,
#                         'score': p.score,
#                         'time_of_attempt': p.time_of_attempt.strftime('%Y-%m-%d %H:%M:%S')  
#                     } for p in performances
#                 ]
#             }, 200
#         else:
#             user_id = get_jwt_identity()
#             user = Account.query.get(user_id)
#             performances = ExamPerformance.query.filter_by(user_id=user.id).all()   
        
#             return {
#                 'subjects': [{'id': s.id, 'name': s.s_name} for s in subjects],
#                 'modules': [{'id': m.id, 'name': m.name, 'subject_id': m.subject_id} for m in modules],
#                 'quizzes': [
#                     {
#                         'id': a.id,
#                         'name': a.q_name,
#                         'date': a.date_of_quiz.strftime('%Y-%m-%d'), 
#                         'time': a.time_duration.strftime('%H:%M:%S'),  
#                         'remarks': a.remarks
#                     } for a in assessments
#                 ],
#                 'quts': [
#                     {
#                         'id': q.id,
#                         'que_no': q.que_no,
#                         'statement': q.statement,
#                         'opt1': q.opt1,
#                         'opt2': q.opt2,
#                         'opt3': q.opt3,
#                         'opt4': q.opt4,
#                         'cor_opt': q.cor_opt
#                     } for q in quts
#                 ],
#                 'scores': [
#                     {
#                         'id': p.id,
#                         'user_id': p.user_id,
#                         'quiz_id': p.quiz_id,
#                         'score': p.score,
#                         'time_of_attempt': p.time_of_attempt.strftime('%Y-%m-%d %H:%M:%S')  
#                     } for p in performances
#                 ]
#             }, 200
class SubManagementAPI(Resource):
    @jwt_required()
    # @caching.cached(timeout=60)
    def get(self):
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        # Try retrieving from cache
        cached_subjects = caching.get("subjects_admin")
        if cached_subjects:
            return cached_subjects, 200
        subjects = Courses.query.all()
        data = [{
            'id': sub.id,
            'name': sub.s_name,
            'desc': sub.remarks
        } for sub in subjects]

        caching.set("subjects_admin", data, timeout=60)
        return data, 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        
        info = request.get_json()
        name = info['s_name']
        desc = info['remarks']
        print("Received data:", info)  # Debugging line to check received data
        if Courses.query.filter_by(s_name=name).first():
            return {"msg": "Subject with that name already exists"}, 400
        new_sub = Courses(s_name=name, remarks=desc)
        db.session.add(new_sub)
        db.session.commit()
        caching.delete("subjects_admin")
        return {"msg": f"Subject '{name}' added successfully!"}, 201

    
    @jwt_required()
    def put(self, sub_id):
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403

        info = request.get_json()
        subject = Courses.query.get(sub_id)
        if subject is None:
            return {"msg": "Subject not found!"}, 404
        name = info.get('s_name')
        desc = info.get('remarks')
        if name:
            if Courses.query.filter(Courses.s_name == name, Courses.id != sub_id).first(): # type: ignore
                return {"msg": "Subject with that name already exists"}, 400
            subject.s_name = name       
        if desc:
            subject.remarks = desc      
        db.session.commit()
        #Invalidate cache after DB update
        caching.delete("subjects_admin")
        return {"msg": f"Your subject '{subject.s_name}' updated successfully!"}, 200
    
    @jwt_required()
    def delete(self, sub_id):
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403

        subject = Courses.query.get(sub_id)
        if subject is not None:
            db.session.delete(subject)
            db.session.commit()
            caching.delete("subjects_admin") 
            return {"msg": f"Subject '{subject.s_name}' successfully removed!"}, 200
        else:
            return {"msg": "Subject not found!"}, 404

class ModuleMngAPI(Resource):
    @jwt_required()
    # @caching.cached(timeout=60)
    def get(self, sub_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        chapters = CourseModule.query.filter_by(subject_id=sub_id).all()
        return [{
            'id': chap.id,
            'name': chap.name,
            'description': chap.description
        } for chap in chapters], 200

    @jwt_required()
    def post(self, sub_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        info = request.get_json()
        name = info.get('name')
        desc = info.get('description')
        if not name or not desc:
            return {"msg": "Please fill all required fields!"}, 400
        if CourseModule.query.filter_by(name=name, subject_id=sub_id).first():
            return {"msg": "Chapter with that name already exists"}, 400
        new_chap = CourseModule(name=name, description=desc, subject_id=sub_id)
        db.session.add(new_chap)
        db.session.commit()
        return {"msg": f"Chapter {name} added successfully!"}, 201

    @jwt_required()
    def put(self, sub_id, chap_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        info = request.get_json()
        if not info:
            return {"msg": "Missing JSON payload"}, 400
        chap = CourseModule.query.get(chap_id)
        if chap is None:
            return {"msg": "Chapter not found!"}, 404
        name = info.get('name')
        desc = info.get('description')
        if name:
            if CourseModule.query.filter(CourseModule.name == name, CourseModule.id != chap_id, CourseModule.subject_id == sub_id).first(): # type: ignore
                return {"msg": "Chapter with that name already exists"}, 400
            chap.name = name
        if desc:
            chap.description = desc
        db.session.commit()
        return {"msg": f"Your chapter '{chap.name}' updated successfully!"}, 200

    @jwt_required()
    def delete(self, sub_id, chap_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        chapter = CourseModule.query.get(chap_id)
        if chapter is not None:
            db.session.delete(chapter)
            db.session.commit()
            return {"msg": f"Chapter '{chapter.name}' successfully deleted!"}, 200
        else:
            return {"msg": "Chapter not found!"}, 404

class AssessmentMngAPI(Resource):
    @jwt_required()
    @caching.cached(timeout=60)
    def get(self, sub_id,chap_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        exams = Assessment.query.filter_by(chapter_id=chap_id).all()
        return [{
            'id': exam.id,
            'name': exam.q_name,
            'date': exam.date_of_quiz.strftime('%Y-%m-%d'),
            'time_duration': exam.time_duration.strftime('%H:%M:%S'),
            'remarks': exam.remarks if exam.remarks else ''} for exam in exams], 200
    
    @jwt_required()
    def post(self, sub_id, chap_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        info = request.get_json()
        name = info.get('name')
        date = info.get('date')
        time = info.get('time')
        remarks = info.get('remarks', '')
        if not all([name, date, time]):
            return {"msg": "Please fill all required fields!"}, 400
        if Assessment.query.filter_by(q_name=name, chapter_id=chap_id).first():
            return {"msg": "Quiz with that name already exists"}, 400
        
        new_exam = Assessment(
            q_name=name,
            chapter_id=chap_id,
            date_of_quiz=datetime.strptime(date, '%Y-%m-%d').date(),
            time_duration=datetime.strptime(time, '%H:%M:%S').time(),
            remarks=remarks
        )
        db.session.add(new_exam)
        db.session.commit()
        return {"msg": f"Quiz '{name}' added successfully!"}, 201
    
    @jwt_required()
    def put(self, sub_id, chap_id, exam_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        info = request.get_json()
        if not info:
            return {"msg": "Missing JSON payload"}, 400
        exam = Assessment.query.get(exam_id)
        if exam is None:
            return {"msg": "Quiz not found!"}, 404
        name = info.get('name')
        date = info.get('date')
        time = info.get('time')
        remarks = info.get('remarks', '')
        if name:
            if Assessment.query.filter(Assessment.q_name == name, Assessment.id != exam_id, Assessment.chapter_id == chap_id).first(): # type: ignore
                return {"msg": f"Quiz name {name} already exists"}, 400
            exam.q_name = name       
        if date:
            exam.date_of_quiz = datetime.strptime(date, '%Y-%m-%d').date()      
        if time:
            exam.time_duration = datetime.strptime(time, '%H:%M:%S').time()      
        if remarks:
            exam.remarks = remarks      
        db.session.commit()
        return {"msg": f"Your quiz '{exam.q_name}' updated successfully!"}, 200
    
    @jwt_required()
    def delete(self, sub_id, chap_id, exam_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        exam = Assessment.query.get(exam_id) 
        if exam is not None:
            db.session.delete(exam)
            db.session.commit()
            return {"msg": f"Quiz '{exam.q_name}' successfully deleted!"}, 200
        else:
            return {"msg": "Quiz not found!"}, 404
        
class QueMngAPI(Resource):
    @jwt_required()
    # @caching.cached(timeout=60)
    def get(self, exam_id, chap_id, sub_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        quiz = Assessment.query.filter_by(id=exam_id, chapter_id=chap_id).first()
        if not quiz:
            return {"msg": "Quiz not found!"}, 404
        questions = AssessmentProblem.query.filter_by(quiz_id=exam_id).all()
        return [{
            'id': q.id,
            'que_no': q.que_no,
            'statement': q.statement,
            'opt1': q.opt1,
            'opt2': q.opt2,
            'opt3': q.opt3,
            'opt4': q.opt4,
            'cor_opt': q.cor_opt
        } for q in questions], 200
    
    @jwt_required()
    def post(self, sub_id, chap_id, exam_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403   
        if not Assessment.query.get(exam_id):
            return {"msg": "Quiz not found!"}, 404 
        info = request.get_json()
        if not info:
            return {"msg": "Missing JSON payload"}, 400
        que_no = info.get('que_no')
        statement = info.get('statement')
        opt1 = info.get('opt1')
        opt2 = info.get('opt2')
        opt3 = info.get('opt3')
        opt4 = info.get('opt4')
        cor_opt = info.get('cor_opt')
        if not all([que_no, statement, opt1, opt2, opt3, opt4, cor_opt]):
            return {"msg": "Please fill all required fields!"}, 400
        if cor_opt not in [1, 2, 3, 4]:
            return {"msg": "Correct option must be between 1 and 4"}, 400
        if AssessmentProblem.query.filter_by(quiz_id=exam_id, que_no=que_no).first():
            return {"msg": "Question with that number already exists"}, 400
        if AssessmentProblem.query.filter_by(quiz_id=exam_id, statement=statement).first():
            return {"msg": "Question with that statement already exists"}, 400
        try :
            new_que = AssessmentProblem(que_no=que_no, quiz_id=exam_id, statement=statement, opt1=opt1, opt2=opt2, opt3=opt3, opt4=opt4, cor_opt=cor_opt)
            db.session.add(new_que)
            db.session.commit()
            return {"msg": f"Your question added successfully!"}, 201
        except Exception as e:
            db.session.rollback()
            print(f"Error adding question: {e}")
            return {"msg": "An error occurred while adding the question"}, 500
    
    @jwt_required()
    def put(self, sub_id, chap_id, exam_id, que_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        info = request.get_json()
        if not info:
            return {"msg": "Missing JSON payload"}, 400
        question = AssessmentProblem.query.get(que_id)
        if question is None:
            return {"msg": "Question not found!"}, 404      
        if question.quiz_id != exam_id:
            return {"msg": "Question does not belong to this quiz"}, 400
        que_no = info.get('que_no')
        statement = info.get('statement')
        opt1 = info.get('opt1')
        opt2 = info.get('opt2')
        opt3 = info.get('opt3')
        opt4 = info.get('opt4')
        cor_opt = info.get('cor_opt')
        if que_no:
            if AssessmentProblem.query.filter(AssessmentProblem.que_no == que_no, AssessmentProblem.id!= que_id, AssessmentProblem.quiz_id == exam_id).first(): # type: ignore
                return {"msg": "Question number already exists"}, 400
            question.que_no = que_no
        if statement:
            if AssessmentProblem.query.filter(AssessmentProblem.statement == statement, AssessmentProblem.id != que_id, AssessmentProblem.quiz_id == exam_id).first(): # type: ignore
                return {"msg": "Question with that statement already exists"}, 400
            question.statement = statement
        if opt1:
            question.opt1 = opt1
        if opt2:
            question.opt2 = opt2
        if opt3:
            question.opt3 = opt3
        if opt4:
            question.opt4 = opt4
        if cor_opt:
            if cor_opt not in [1, 2, 3, 4]:
                return {"msg": "Correct option must be between 1 and 4"}, 400
            question.cor_opt = cor_opt
        db.session.commit()
        return {"msg": f"Your question updated successfully!"}, 200
    
    @jwt_required()
    def delete(self, sub_id, chap_id, exam_id, que_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        quiz = Assessment.query.filter_by(id=exam_id, chapter_id=chap_id).first()
        if not quiz:
            return {"msg": "Quiz not found!"}, 404
        question = AssessmentProblem.query.get(que_id)
        if question is None:
            return {"msg": "Question not found!"}, 404
        if question.quiz_id != exam_id:
            return {"msg": "Question does not belong to this quiz"}, 400
        try:
            question_no = question.que_no
            db.session.delete(question)
            db.session.commit()
            return {"msg": f"Question {question_no} successfully deleted!"}, 200
        except Exception as e:
            db.session.rollback()
            return {"msg": "Failed to delete question"}, 500
        
class UserMngAPI(Resource):
    @jwt_required()
    # @caching.cached(timeout=60) 
    def get(self):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        
        users = Account.query.filter(Account.role != 'admin').all()
        users_data = []
        for user in users:
            total_score = sum(score.score for score in user.scores)
            total_max_marks = sum(score.max_marks for score in user.scores)
            
            accuracy = 0
            if total_max_marks > 0:
                accuracy = round((total_score / total_max_marks) * 100, 2)

            users_data.append({
                'id': user.id,
                'username': user.username,
                'f_name': user.f_name,
                'l_name': user.l_name,
                'email': user.email,
                'active': user.active,
                'role': user.role,
                'quizzes_taken': len(user.scores),
                'accuracy': accuracy
            })
            
        return jsonify(users_data)

    @jwt_required()
    def post(self, user_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        
        target_user = Account.query.get(user_id)
        if not target_user:
            return {"msg": "User not found!"}, 404
        current_user_id = get_jwt().get('sub') 
        if str(target_user.id) == str(current_user_id):
             return {"msg": "You cannot modify your own account status."}, 403

        target_user.active = not target_user.active
        db.session.commit()
        caching.delete_memoized(self.get)

        status = "activated" if target_user.active else "deactivated"
        return {"msg": f"User '{target_user.username}' has been {status} successfully!"}, 200

class UserDashAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = Account.query.get(user_id)
        if not user:
            return {"msg": "User not found!"}, 404
        if user.role != 'user':
            return {"msg": "Access denied! Only Users can access"}, 403
        subjects = Courses.query.all()
        quizzes = Assessment.query.filter(Assessment.date_of_quiz > datetime.now().date()).all()
        return {
            'subjects': [{'id': s.id, 'name': s.s_name} for s in subjects],
            'quizzes': [
                {
                    'id': q.id,
                    'name': q.q_name,
                    'subject': q.chapter.course.s_name,
                    'chapter': q.chapter.name,
                    'date_of_quiz': q.date_of_quiz.strftime('%Y-%m-%d'),
                    'time_duration': str(q.time_duration)
                } for q in quizzes
            ]
        }

class ChapAPI_User(Resource):
    @jwt_required()
    def get(self, sub_id):
        if get_jwt().get('role') != 'user':
            return {"msg": "Access denied! Only Users can access"}, 403
        sub = Courses.query.get(sub_id)
        if not sub:
            return {"msg": "Subject not found"}, 404
        data = {
            "s_name": sub.s_name,
            "chapters": [
                {
                    "id": chap.id,
                    "name": chap.name,
                    "course": {"s_name": sub.s_name},
                    "quizzes": [{"id": quiz.id} for quiz in chap.quizzes]
                } for chap in sub.chapters
            ]
        }
        return data, 200

class QuizAPI_User(Resource):
    @jwt_required()
    def get(self, chap_id): 
        if get_jwt().get('role') != 'user':
            return {"msg": "Access denied! Only Users can access"}, 403
        chap = CourseModule.query.get(chap_id)
        if not chap:
            return {"msg": "Chapter not found"}, 404
        data = {
            "quizzes": [
                {
                    "id": quiz.id,
                    "chapter": {
                        "id": chap.id,
                        "name": chap.name,
                        "course": {
                            "s_name": chap.course.s_name
                        }
                    },
                    "q_name": quiz.q_name,
                    "questions": len(quiz.questions),
                    "time_duration": str(quiz.time_duration), 
                    "date_of_quiz": quiz.date_of_quiz.strftime('%Y-%m-%d') 
                }
                for quiz in chap.quizzes
            ]
        }
        return data, 200

class QuizStartAPI(Resource): 
    @jwt_required()
    def get(self, quiz_id):
        if get_jwt().get('role') != 'user':
            return {"msg": "Access denied! Only users can submit quizzes."}, 403
        quiz = Assessment.query.get(quiz_id)
        if not quiz:
            return {"msg": "Quiz not found"}, 404
        
        questions = AssessmentProblem.query.filter_by(quiz_id=quiz_id).all()
        return {
            "quiz": {
                "id": quiz.id,
                "q_name": quiz.q_name,
                "chapter": {
                    "id": quiz.chapter.id,
                    "name": quiz.chapter.name,
                    "course": {
                        "s_name": quiz.chapter.course.s_name
                    }
                },
                "time_duration": str(quiz.time_duration),
                "date_of_quiz": quiz.date_of_quiz.strftime('%Y-%m-%d')
            },
            "questions": [
                {
                    "id": q.id,
                    "que_no": q.que_no,
                    "statement": q.statement,
                    "opt1": q.opt1,
                    "opt2": q.opt2,
                    "opt3": q.opt3,
                    "opt4": q.opt4,
                    "cor_opt": q.cor_opt
                } for q in questions
            ]
        }, 200
    @jwt_required()
    def post(self, quiz_id):
        user_id = get_jwt_identity()
        if get_jwt().get('role') != 'user':
            return {"msg": "Access denied! Only users can submit quizzes."}, 403
        quiz = Assessment.query.get(quiz_id)
        if not quiz:
            return {"msg": "Quiz not found"}, 404
        submitted_data = request.get_json()
        if not submitted_data or 'answers' not in submitted_data:
            return {"msg": "Missing answers in request payload."}, 400
        
        user_answers = submitted_data.get('answers')
        score = 0
        total_questions = len(quiz.questions)
        for question in quiz.questions:
            question_id_str = str(question.id)
            user_choice = user_answers.get(question_id_str)
            correct_answer_str = str(question.cor_opt)
            if user_choice == correct_answer_str:
                score += 1
        new_performance_record = ExamPerformance(
            score=score,
            quiz_id=quiz_id,
            user_id=user_id,
            max_marks=total_questions
        )
        db.session.add(new_performance_record)
        db.session.commit()
        return {
            "msg": "Quiz submitted successfully!",
            "score": score,
            "max_marks": total_questions
        }, 200

class ScoreHistoryAPI(Resource):
    @jwt_required()
    def get(self, user_id):
        if get_jwt().get('role') != 'user':
            return {"msg": "Access denied! Only users can view their score history."}, 403
        user = Account.query.get(user_id)
        if not user:
            return {"msg": "User not found"}, 404
        
        scores = ExamPerformance.query.filter_by(user_id=user.id).order_by(ExamPerformance.time_of_attempt.desc()).all()
        if not scores:
            return {"msg": "No scores found"}, 404
        
        return [{
                'subject': score.quiz.chapter.course.s_name,
                'chapter': score.quiz.chapter.name,
                'quiz_name': score.quiz.q_name,
                'score': score.score,
                'date_of_attempt': score.time_of_attempt.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': str(score.quiz.time_duration)
            } for score in scores], 200

class AdminStatisticsAPI(Resource):
    @jwt_required()
    def get(self):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Admins only!"}, 403

        # Quiz Attempts by Subject (for Pie Chart)
        attempts_by_subject_query = db.session.query(
            Courses.s_name,
            func.count(ExamPerformance.id)
        ).join(CourseModule, Courses.id == CourseModule.subject_id)\
         .join(Assessment, CourseModule.id == Assessment.chapter_id)\
         .join(ExamPerformance, Assessment.id == ExamPerformance.quiz_id)\
         .group_by(Courses.s_name).all()

        attempts_by_subject = {subject: count for subject, count in attempts_by_subject_query}

        # Average Score by Quiz (for Bar Chart)
        avg_score_by_quiz_query = db.session.query(
            Assessment.q_name,
            func.avg(ExamPerformance.score * 100.0 / ExamPerformance.max_marks)
        ).join(ExamPerformance, Assessment.id == ExamPerformance.quiz_id)\
         .group_by(Assessment.q_name).all()

        avg_score_by_quiz = {name: round(avg, 2) for name, avg in avg_score_by_quiz_query}

        # Total Attempts per Quiz (for Bar Chart)
        attempts_per_quiz_query = db.session.query(
            Assessment.q_name,
            func.count(ExamPerformance.id)
        ).join(ExamPerformance, Assessment.id == ExamPerformance.quiz_id)\
         .group_by(Assessment.q_name).all()

        attempts_per_quiz = {name: count for name, count in attempts_per_quiz_query}

        # Average Score by Subject (for Bar Chart)
        avg_score_by_subject_query = db.session.query(
            Courses.s_name,
            func.avg(ExamPerformance.score * 100.0 / ExamPerformance.max_marks)
        ).join(CourseModule, Courses.id == CourseModule.subject_id)\
         .join(Assessment, CourseModule.id == Assessment.chapter_id)\
         .join(ExamPerformance, Assessment.id == ExamPerformance.quiz_id)\
         .group_by(Courses.s_name).all()
        
        avg_score_by_subject = {subject: round(avg, 2) for subject, avg in avg_score_by_subject_query}

        return {
            "attempts_by_subject": attempts_by_subject,
            "avg_score_by_quiz": avg_score_by_quiz,
            "attempts_per_quiz": attempts_per_quiz,
            "avg_score_by_subject": avg_score_by_subject
        }

class UserStatisticsAPI(Resource): 
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = db.session.get(Account, user_id)
        if not user:
            return {"msg": "User not found"}, 404
        # --- Chart 3 Data: Score in Each Attempted Quiz ---
        # Filter out scores that are None OR zero
        my_quiz_scores = []
        for score in user.scores:
            if score.score is not None and score.score > 0: 
                total_marks = len(score.quiz.questions) 
                percentage_score = 0
                if total_marks > 0:
                    percentage_score = round((score.score / total_marks) * 100, 2)
                
                my_quiz_scores.append({"name": score.quiz.q_name, "score": percentage_score})

        subject_scores = {}
        for score in user.scores:
            if score.score is None:
                continue
            total_marks = len(score.quiz.questions)
            percentage_score = 0
            if total_marks > 0:
                percentage_score = round((score.score / total_marks) * 100, 2) 

            subject = score.quiz.chapter.course.s_name
            if subject not in subject_scores:
                subject_scores[subject] = []
            
            subject_scores[subject].append(percentage_score) 
        my_avg_score_by_subject = {
            subject: round(sum(scores) / len(scores), 2)
            for subject, scores in subject_scores.items() if scores}
        my_score_comparison = {
            subject: {
                "average": round(sum(scores) / len(scores), 2),
                "highest": max(scores)
            }
            for subject, scores in subject_scores.items() if scores
        }
        my_attempt_distribution = {
            subject: len(scores)
            for subject, scores in subject_scores.items()
        }
        return {
            "my_quiz_scores": my_quiz_scores,
            "my_avg_score_by_subject": my_avg_score_by_subject,
            "my_score_comparison": my_score_comparison,
            "my_attempt_distribution": my_attempt_distribution
        }
    
class AdminUserExportAPI(Resource):
    @jwt_required()
    def post(self):
        admin_id = get_jwt_identity()
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        task = export_user_data_by_admin.delay(admin_id)
        return {"message": "User export process has been started.", "task_id": task.id}, 202

class TaskStatusAPI(Resource):
    @jwt_required()
    def get(self, task_id):
        task = export_user_data_by_admin.AsyncResult(task_id)  
        response = {
            'state': task.state,
            'info': task.info, 
        }
        return response, 200
    
class SearchAPI(Resource):
    @jwt_required()
    def get(self):
        # Use reqparse to safely get the search query from URL parameters 
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, required=True, help='Search query cannot be blank', location='args')
        args = parser.parse_args()
        search_query = args['q']
        user_role = get_jwt().get('role')
        results = {
            "users": [],
            "subjects": [],
            "chapters": [],
            "quizzes": []
        }
        subjects = Courses.query.filter(Courses.s_name.ilike(f'%{search_query}%')).all()
        results["subjects"] = [{'id': s.id, 'name': s.s_name} for s in subjects]
        chapters = CourseModule.query.filter(CourseModule.name.ilike(f'%{search_query}%')).all()
        results["chapters"] = [{'id': c.id, 'name': c.name, 'subject_name': c.course.s_name} for c in chapters]
        # Query quizzes
        quizzes = Assessment.query.filter(Assessment.q_name.ilike(f'%{search_query}%')).all()
        results["quizzes"] = [{'id': q.id, 'name': q.q_name, 'chapter_name': q.chapter.name} for q in quizzes]
        # --- Admin-only results ---
        if user_role == 'admin':
            users = Account.query.filter(Account.username.ilike(f'%{search_query}%'), Account.role == 'user').all()
            results["users"] = [{'id': u.id, 'username': u.username, 'full_name': f'{u.f_name} {u.l_name}'} for u in users]
        return results, 200