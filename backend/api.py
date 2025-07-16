from flask_restful import Resource
from flask_jwt_extended import get_jwt, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask import request, jsonify, current_app as ns, session
from backend.models import db, Account, Courses, CourseModule, Assessment, AssessmentProblem, ExamPerformance
from datetime import datetime 
from flask_caching import Cache
from backend.config import config_settings

caching = Cache()

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
        print(f"User = {user}")  # Debugging line to check user retrieval
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
class AccountDashboardAPI(Resource):
    @jwt_required()
    @caching.cached(timeout=60)
    def get(self):
        claims = get_jwt()
        today = datetime.now().date()
        assessments = Assessment.query.filter(Assessment.date_of_quiz >= today).all()
        subjects = Courses.query.all()
        modules = CourseModule.query.all()
        quts = AssessmentProblem.query.all()
        users = Account.query.all()
        performances = ExamPerformance.query.all()
        if claims.get('role') == 'admin':
            return {
                'quizzes': [
                    {
                        'id': a.id,
                        'name': a.q_name,
                        'date': a.date_of_quiz.strftime('%Y-%m-%d'), 
                        'time': a.time_duration.strftime('%H:%M:%S'),  
                        'remarks': a.remarks
                    } for a in assessments
                ],
                'subjects': [{'id': s.id, 'name': s.s_name} for s in subjects],
                'modules': [{'id': m.id, 'name': m.name, 'subject_id': m.subject_id} for m in modules],
                'quts': [
                    {
                        'id': q.id,
                        'que_no': q.que_no,
                        'statement': q.statement,
                        'opt1': q.opt1,
                        'opt2': q.opt2,
                        'opt3': q.opt3,
                        'opt4': q.opt4,
                        'cor_opt': q.cor_opt
                    } for q in quts
                ],
                'users': [{'id': u.id, 'username': u.username, 'role': u.role} for u in users],
                'scores': [
                    {
                        'id': p.id,
                        'user_id': p.user_id,
                        'quiz_id': p.quiz_id,
                        'score': p.score,
                        'time_of_attempt': p.time_of_attempt.strftime('%Y-%m-%d %H:%M:%S')  
                    } for p in performances
                ]
            }, 200
        else:
            user_id = get_jwt_identity()
            user = Account.query.get(user_id)
            performances = ExamPerformance.query.filter_by(user_id=user.id).all()   
        
            return {
                'subjects': [{'id': s.id, 'name': s.s_name} for s in subjects],
                'modules': [{'id': m.id, 'name': m.name, 'subject_id': m.subject_id} for m in modules],
                'quizzes': [
                    {
                        'id': a.id,
                        'name': a.q_name,
                        'date': a.date_of_quiz.strftime('%Y-%m-%d'), 
                        'time': a.time_duration.strftime('%H:%M:%S'),  
                        'remarks': a.remarks
                    } for a in assessments
                ],
                'quts': [
                    {
                        'id': q.id,
                        'que_no': q.que_no,
                        'statement': q.statement,
                        'opt1': q.opt1,
                        'opt2': q.opt2,
                        'opt3': q.opt3,
                        'opt4': q.opt4,
                        'cor_opt': q.cor_opt
                    } for q in quts
                ],
                'scores': [
                    {
                        'id': p.id,
                        'user_id': p.user_id,
                        'quiz_id': p.quiz_id,
                        'score': p.score,
                        'time_of_attempt': p.time_of_attempt.strftime('%Y-%m-%d %H:%M:%S')  
                    } for p in performances
                ]
            }, 200
class SubManagementAPI(Resource):
    @jwt_required()
    # @caching.cached(timeout=60)
    def get(self):
        user_id = get_jwt_identity()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403

        subjects = Courses.query.all()
        return [{
            'id': sub.id,
            'name': sub.s_name,
            'desc': sub.remarks
        } for sub in subjects], 200

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
        caching.delete_memoized(SubManagementAPI.get)
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
        caching.delete_memoized(SubManagementAPI.get)
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
            caching.delete_memoized(SubManagementAPI.get)
            return {"msg": f"Subject '{subject.s_name}' successfully removed!"}, 200
        else:
            return {"msg": "Subject not found!"}, 404

class ModuleMngAPI(Resource):
    @jwt_required()
    @caching.cached(timeout=60)
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
    def get(self, chap_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        exams = Assessment.query.filter_by(chapter_id=chap_id).all()
        return [{
            'id': exam.id,
            'name': exam.q_name,
            'date': exam.date_of_quiz,
            'time': exam.time_duration,
            'remarks': exam.remarks
        } for exam in exams], 200
    
    @jwt_required()
    def post(self, chap_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        info = request.get_json()
        name = info.get('name')
        date = info.get('date')
        time = info.get('time')
        remarks = info.get('remarks', '')
        if not name or not date or not time:
            return {"msg": "Please fill all required fields!"}, 400
        if Assessment.query.filter_by(q_name=name, chapter_id=chap_id).first():
            return {"msg": "Quiz with that name already exists"}, 400
        new_exam = Assessment(q_name=name, chapter_id=chap_id, date_of_quiz=datetime.strptime(date, '%Y-%m-%d').date(), time_duration=datetime.strptime(time, '%H:%M:%S').time(), remarks=remarks)
        db.session.add(new_exam)
        db.session.commit()
        return {"msg": f"Quiz '{name}' added successfully!"}, 201
    
    @jwt_required()
    def put(self, chap_id, exam_id):
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
    def delete(self, chap_id, exam_id):
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
    @caching.cached(timeout=60)
    def get(self, exam_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        if not Assessment.query.get(exam_id):
            return {"msg": "Quiz not found!"}, 404
        questions = AssessmentProblem.query.filter_by(quiz_id=exam_id).all()
        return jsonify([{
            'id': q.id,
            'que_no': q.que_no,
            'statement': q.statement,
            'opt1': q.opt1,
            'opt2': q.opt2,
            'opt3': q.opt3,
            'opt4': q.opt4,
            'cor_opt': q.cor_opt
        } for q in questions]), 200
    
    @jwt_required()
    def post(self, exam_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403   
        if not Assessment.query.get(exam_id):
            return {"msg": "Quiz not found!"}, 404 
        info = request.get_json()
        que_no = info.get('que_no')
        statement = info.get('statement')
        opt1 = info.get('opt1')
        opt2 = info.get('opt2')
        opt3 = info.get('opt3')
        opt4 = info.get('opt4')
        cor_opt = info.get('cor_opt')
        if not all([que_no, statement, opt1, opt2, opt3, opt4, cor_opt]):
            return {"msg": "Please fill all required fields!"}, 400
        if AssessmentProblem.query.filter_by(quiz_id=exam_id, que_no=que_no).first():
            return {"msg": "Question with that number already exists"}, 400
        if AssessmentProblem.query.filter_by(quiz_id=exam_id, statement=statement).first():
            return {"msg": "Question with that statement already exists"}, 400
        new_que = AssessmentProblem(que_no=que_no, quiz_id=exam_id, statement=statement, opt1=opt1, opt2=opt2, opt3=opt3, opt4=opt4, cor_opt=cor_opt)
        db.session.add(new_que)
        db.session.commit()
        return {"msg": f"Your question added successfully!"}, 201
    
    @jwt_required()
    def put(self, exam_id, que_id):
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
    def delete(self, exam_id, que_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        question = AssessmentProblem.query.get(que_id)
        if question is None:
            return {"msg": "Question not found!"}, 404
        if question.quiz_id != exam_id:
            return {"msg": "Question does not belong to this quiz"}, 400
        db.session.delete(question)
        db.session.commit()
        return {"msg": f"Question {question.que_no} successfully deleted!"}, 200
        
class UserMngAPI(Resource):
    @jwt_required()
    @caching.cached(timeout=60)
    def get(self):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        users = Account.query.all()
        return jsonify([{
            'id': user.id,
            'username': user.username,
            'active': user.active,
            'role': user.role
        } for user in users]), 200

    @jwt_required()
    def post(self, user_id):
        if get_jwt().get('role') != 'admin':
            return {"msg": "Access denied! Only admin can access"}, 403
        target_user = Account.query.get(user_id)
        if not target_user:
            return {"msg": "User not found!"}, 404
        if target_user.id == user['user']['id']:
            return {"msg": "You cannot modify your own account status"}, 403
        target_user.active = not target_user.active
        db.session.commit()
        status = "activated" if target_user.active else "deactivated"
        return {"msg": f"User {target_user.username} has been {status} successfully!"}, 200

