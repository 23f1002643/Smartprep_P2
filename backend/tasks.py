from celery import shared_task
from backend.worker import *
from backend.models import db, Account, Assessment, ExamPerformance, CourseModule, Courses
from datetime import datetime, timedelta
from sqlalchemy import func
from backend.config import config_settings
import smtplib, os, tempfile, shutil, csv, json
from flask import render_template
from app import ns
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
# from celery.schedules import crontab

@shared_task
def greeting_task():
    print("Hello from the Celery task!")
    return "Greeting task completed successfully!"

def send_email(to_email, sub, body, att_path=None):
    smtp_server = config_settings['MAIL_SERVER']
    smtp_port = config_settings['MAIL_PORT']
    sender_email= config_settings['MAIL_DEFAULT_SENDER']
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg.attach(MIMEText(body, 'html'))
        msg['Subject'] = sub
        
        # Add attachment if provided
        if att_path and os.path.exists(att_path):
            with open(att_path, 'rb') as file:
                part = MIMEBase('text', 'csv')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(att_path)}'
                )
                msg.attach(part)
        #sending email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            # server.login(sender_email, config_settings['MAIL_PASSWORD'])
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False
        
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False

@shared_task(bind=True, name='backend.tasks.email_for_daily_reminders')
def email_for_daily_reminders(self):
    with ns.app_context():
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 0, 'status': 'Starting daily reminder task...'}
        )

        active_users = Account.query.filter_by(active=True, role='user').all()
        total_users = len(active_users)

        today = datetime.now().date()
        available_quizzes = Assessment.query.filter(
            Assessment.date_of_quiz >= today
        ).all()
        if not available_quizzes:
            return {'status': 'completed', 'message': 'No quizzes available for reminders'}

        reminder_count = 0
        for i, user in enumerate(active_users):
            week_ago = datetime.now() - timedelta(days=7)
            recent_attempts = ExamPerformance.query.filter(
                ExamPerformance.user_id == user.id,
                ExamPerformance.time_of_attempt >= week_ago
            ).count()
            utm_quizzes = []
            for quiz in available_quizzes:
                if not ExamPerformance.query.filter_by(user_id=user.id, quiz_id=quiz.id).first():
                    chapter = CourseModule.query.get(quiz.chapter_id)
                    print(f"Processing quiz: {quiz.q_name} for user: {user.username}")
                    if not chapter:
                        print(f"Warning: No chapter found for quiz ID {quiz.id}")
                        continue
                    print(f"Chapter found: {chapter.name} for quiz: {quiz.q_name}")
                    subject = Courses.query.get(chapter.subject_id)
                    if not subject:
                        print(f"Warning: No subject found for chapter ID {chapter.id}")
                        continue
                    print(f"Subject found: {subject.s_name} for quiz: {quiz.q_name}")
                    utm_quizzes.append({
                        'name': quiz.q_name,
                        'subject': subject.s_name,
                        'chapter': chapter.name,
                        'date': quiz.date_of_quiz.strftime('%Y-%m-%d'),
                        'duration': str(quiz.time_duration)
                    })

            if utm_quizzes:
                email_body = create_reminder_email_template(user, utm_quizzes)
                subject = f"Quiz Reminder - {len(utm_quizzes)} Unattempted Quizzes Available!"
                if send_email(user.email, subject, email_body):
                    reminder_count += 1

            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': total_users,
                    'status': f'Processed {i + 1}/{total_users} users'
                }
            )

        return {
            'status': 'completed',
            'total_users': total_users,
            'reminders_sent': reminder_count,
            'available_quizzes': len(available_quizzes)
        }

def create_reminder_email_template(user, quiz_list):
    quiz_rows = ""
    for quiz in quiz_list:
        quiz_rows += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{quiz['name']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{quiz['subject']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{quiz['chapter']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{quiz['date']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{quiz['duration']}</td>
        </tr>
        """
    
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f8f9fa; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background-color: #e9ecef; padding: 10px; text-align: left; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6c757d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🎯 Quiz Master - Daily Reminder</h2>
            </div>
            <div class="content">
                <h3>Hello {user.f_name} {user.l_name}!</h3>
                <p>Hope you're having a great day! We wanted to remind you about the exciting quizzes available on Quiz Master.</p>
                
                <h4>📚 Available Quizzes:</h4>
                <table>
                    <thead>
                        <tr>
                            <th>Quiz Name</th>
                            <th>Subject</th>
                            <th>Chapter</th>
                            <th>Date</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        {quiz_rows}
                    </tbody>
                </table>
                
                <p>💡 <strong>Why take quizzes?</strong></p>
                <ul>
                    <li>Test your knowledge and understanding</li>
                    <li>Track your progress over time</li>
                    <li>Identify areas for improvement</li>
                    <li>Boost your confidence</li>
                </ul>
                
                <p>🚀 Ready to challenge yourself? Login to Quiz Master and start your learning journey!</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:5000/login" style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Start Quiz Now!</a>
                </div>
            </div>
            <div class="footer">
                <p>Best regards,<br>Quiz Master Team</p>
                <p><small>You received this email because you're registered on Quiz Master. If you don't want to receive these reminders, please contact support.</small></p>
            </div>
        </div>
    </body>
    </html>
    """

@shared_task(bind=True, name='backend.tasks.generate_monthly_report')
def generate_monthly_report(self):
    self.update_state( state='PROGRESS', meta={'current': 0, 'total': 0, 'status': 'Starting monthly report generation...'})

    today = datetime.now().date()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)

    users = Account.query.filter_by(active=True, role='user').all()

    total_users = len(users)
    reports_sent = 0

    for i, user in enumerate(users):
        scores = ExamPerformance.query.filter(
            ExamPerformance.user_id == user.id,
            ExamPerformance.time_of_attempt >= first_day_previous_month,
            ExamPerformance.time_of_attempt < first_day_current_month
        ).all()

        if True : # True only for debugging purpose
            total_quizzes = len(scores)
            total_score = sum(s.score for s in scores)
            total_max = sum(s.max_marks for s in scores)
            avg_score = round((total_score / total_max) * 100, 2) if total_max > 0 else 0

            quiz_details = []
            for s in scores:
                quiz = Assessment.query.get(s.quiz_id)
                chapter = CourseModule.query.get(quiz.chapter_id) if quiz else None
                subject = Courses.query.get(chapter.subject_id) if chapter else None

                quiz_details.append({
                    'quiz_name': quiz.q_name if quiz else '',
                    'subject': subject.s_name if subject else '',
                    'chapter': chapter.name if chapter else '',
                    'score': s.score,
                    'max_marks': s.max_marks,
                    'percentage': round((s.score / s.max_marks) * 100, 2) if s.max_marks > 0 else 0,
                    'date': s.time_of_attempt.strftime('%Y-%m-%d'),
                    'time': s.time_of_attempt.strftime('%H:%M')
                })

            month_name = last_day_previous_month.strftime('%B %Y')
            try :
                html = create_monthly_report_template(user, quiz_details, total_quizzes, avg_score, month_name)
            except Exception as e:
                print(f"Error while generating report: {str(e)}")
                return {'status': 'error', 'message': f'Template error: {str(e)}'}
            subject = f"Monthly Activity Report - {month_name}"

            if send_email(user.email, subject, html):
                reports_sent += 1

        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': total_users,
                'status': f'Reports generated for {i + 1} of {total_users} users'
            }
        )

    return {
        'status': 'completed',
        'total_users': total_users,
        'reports_sent': reports_sent,
        'month': last_day_previous_month.strftime('%B %Y')
    }

def create_monthly_report_template(user, quiz_details, total_quizzes, average_score, month):
    quiz_rows_html = ""
    for quiz in quiz_details:
        quiz_rows_html += f"""
        <tr>
            <td>{quiz['quiz_name']}</td>
            <td>{quiz['subject']}</td>
            <td>{quiz['chapter']}</td>
            <td>{quiz['score']}/{quiz['max_marks']}</td>
            <td>{quiz['percentage']}%</td>
            <td>{quiz['date']} {quiz['time']}</td>
        </tr>
        """

    plural_suffix = 'es' if total_quizzes != 1 else ''
    
    if average_score >= 80:
        performance_feedback = "Excellent work! Keep it up!"
    elif average_score >= 60:
        performance_feedback = "Good effort! Try to improve your score next month."
    else:
        performance_feedback = "There's room for improvement. Practice more to boost your scores!"

    return render_template(
        'monthly_report.html',
        name=f"{user.f_name} {user.l_name}",
        quiz_rows=quiz_rows_html,
        total_quizzes=total_quizzes,
        average_score=average_score,
        month=month,
        plural_suffix=plural_suffix,
        performance_feedback=performance_feedback
    )

# @celery.task(bind=True, name='export_admin_user_data')
# def export_admin_user_data(self, admin_id):
#     self.update_state(
#         state='PROGRESS',
#         meta={'current': 0, 'total': 100, 'status': 'Starting admin CSV export...'}
#     )

#     admin = Account.query.get(admin_id)
#     if not admin or admin.role != 'admin':
#         return {'status': 'error', 'message': 'Unauthorized access'}

#     users = Account.query.filter_by(role='user').all()
#     if not users:
#         return {'status': 'error', 'message': 'No users found'}

#     temp_dir = tempfile.mkdtemp()
#     csv_filename = f"admin_users_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#     csv_path = os.path.join(temp_dir, csv_filename)

#     self.update_state(
#         state='PROGRESS',
#         meta={'current': 25, 'total': 100, 'status': 'Generating admin CSV file...'}
#     )

#     with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
#         fieldnames = [
#             'user_id', 'username', 'full_name', 'email', 'mobile_no',
#             'qualification', 'dob', 'registration_date', 'active_status',
#             'total_quizzes_taken', 'total_score', 'total_max_marks',
#             'average_percentage', 'last_quiz_date', 'performance_level'
#         ]
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()

#         for i, user in enumerate(users):
#             user_scores = ExamPerformance.query.filter_by(user_id=user.id).all()
#             total_quizzes = len(user_scores)
#             total_score = sum(score.score for score in user_scores)
#             total_max_marks = sum(score.max_marks for score in user_scores)
#             average_percentage = round((total_score / total_max_marks) * 100, 2) if total_max_marks > 0 else 0

#             last_quiz_date = ''
#             if user_scores:
#                 last_attempt = max(user_scores, key=lambda x: x.time_of_attempt)
#                 last_quiz_date = last_attempt.time_of_attempt.strftime('%Y-%m-%d %H:%M:%S')

#             performance_level = (
#                 'Excellent' if average_percentage >= 80 else
#                 'Good' if average_percentage >= 60 else
#                 'Average' if average_percentage >= 40 else
#                 'Below Average' if average_percentage >= 20 else
#                 'Poor'
#             )

#             writer.writerow({
#                 'user_id': user.id,
#                 'username': user.username,
#                 'full_name': f"{user.f_name} {user.l_name}",
#                 'email': user.email,
#                 'mobile_no': user.mobile_no,
#                 'qualification': user.edu_qul,
#                 'dob': user.dob,
#                 'registration_date': user.registration_date,
#                 'active_status': user.active,
#                 'total_quizzes_taken': total_quizzes,
#                 'total_score': total_score,
#                 'total_max_marks': total_max_marks,
#                 'average_percentage': average_percentage,
#                 'last_quiz_date': last_quiz_date,
#                 'performance_level': performance_level
#             })

#             progress = 25 + ((i + 1) * 50 // len(users))
#             current_task.update_state(
#                 state='PROGRESS',
#                 meta={
#                     'current': progress,
#                     'total': 100,
#                     'status': f'Processing user {i + 1}/{len(users)}'
#                 }
#             )

#     self.update_state(
#         state='PROGRESS',
#         meta={'current': 85, 'total': 100, 'status': 'Sending admin CSV via email...'}
#     )

#     with ns.app_context():
#         template = template_env.get_template("admin_export.html")
#         email_body = template.render(
#             admin_name=f"{admin.f_name} {admin.l_name}",
#             export_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             user_count=len(users)
#         )

#     subject = f"Admin User Data Export - {datetime.now().strftime('%Y-%m-%d')}"
#     email_sent = send_email(admin.email, subject, email_body, csv_path)

#     shutil.rmtree(temp_dir)

#     self.update_state(
#         state='SUCCESS',
#         meta={'current': 100, 'total': 100, 'status': 'Export completed successfully!'}
#     )

#     return {
#         'status': 'completed',
#         'message': 'CSV export completed and sent via email',
#         'total_users': len(users),
#         'email_sent': email_sent
#     }

# @celery_app.task(bind=True, name='backend.tasks.export_user_quiz_data')
# def export_user_quiz_data(self, user_id):
#     """
#     Export user's quiz data to CSV format
#     Triggered by user from dashboard
#     """
#     try:
#         current_task.update_state(
#             state='PROGRESS',
#             meta={'current': 0, 'total': 100, 'status': 'Starting CSV export...'}
#         )
        
#         # Get user information
#         user = Account.query.get(user_id)
#         if not user:
#             return {'status': 'error', 'message': 'User not found'}
        
#         # Get user's quiz scores
#         user_scores = ExamPerformance.query.filter_by(user_id=user_id).all()
        
#         if not user_scores:
#             return {'status': 'error', 'message': 'No quiz data found for this user'}
        
#         # Create temporary CSV file
#         temp_dir = tempfile.mkdtemp()
#         csv_filename = f"quiz_data_{user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#         csv_path = os.path.join(temp_dir, csv_filename)
        
#         current_task.update_state(
#             state='PROGRESS',
#             meta={'current': 25, 'total': 100, 'status': 'Generating CSV file...'}
#         )
        
#         # Generate CSV
#         with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
#             fieldnames = [
#                 'quiz_id', 'quiz_name', 'subject_name', 'chapter_name', 
#                 'date_of_quiz', 'time_duration', 'score', 'max_marks', 
#                 'percentage', 'attempt_date', 'attempt_time', 'remarks'
#             ]
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()
            
#             for i, score in enumerate(user_scores):
#                 quiz = Assessment.query.get(score.quiz_id)
#                 chapter = CourseModule.query.get(quiz.chapter_id)
#                 subject = Courses.query.get(chapter.subject_id)
                
#                 writer.writerow({
#                     'quiz_id': quiz.id,
#                     'quiz_name': quiz.q_name,
#                     'subject_name': subject.s_name,
#                     'chapter_name': chapter.name,
#                     'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d'),
#                     'time_duration': str(quiz.time_duration),
#                     'score': score.score,
#                     'max_marks': score.max_marks,
#                     'percentage': round((score.score / score.max_marks) * 100, 2),
#                     'attempt_date': score.time_of_attempt.strftime('%Y-%m-%d'),
#                     'attempt_time': score.time_of_attempt.strftime('%H:%M:%S'),
#                     'remarks': quiz.remarks or ''
#                 })
                
#                 # Update progress
#                 progress = 25 + (i + 1) * 50 // len(user_scores)
#                 current_task.update_state(
#                     state='PROGRESS',
#                     meta={'current': progress, 'total': 100, 'status': f'Processing record {i + 1}/{len(user_scores)}'}
#                 )
        
#         current_task.update_state(
#             state='PROGRESS',
#             meta={'current': 75, 'total': 100, 'status': 'Sending email with CSV attachment...'}
#         )
        
#         # Send email with CSV attachment
#         subject = f"Quiz Data Export - {datetime.now().strftime('%Y-%m-%d')}"
#         body = f"""
#         <html>
#         <body>
#             <h3>Hello {user.f_name} {user.l_name}!</h3>
#             <p>Your quiz data export has been completed successfully.</p>
#             <p><strong>Export Details:</strong></p>
#             <ul>
#                 <li>Total quizzes: {len(user_scores)}</li>
#                 <li>Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
#                 <li>File format: CSV</li>
#             </ul>
#             <p>Please find your quiz data attached to this email.</p>
#             <p>Best regards,<br>Quiz Master Team</p>
#         </body>
#         </html>
#         """
        
#         email_sent = send_email(user.email, subject, body, csv_path)
        
#         # Clean up temporary file
#         try:
#             os.remove(csv_path)
#             os.rmdir(temp_dir)
#         except:
#             pass
        
#         current_task.update_state(
#             state='PROGRESS',
#             meta={'current': 100, 'total': 100, 'status': 'Export completed successfully!'}
#         )
        
#         return {
#             'status': 'completed',
#             'message': 'CSV export completed and sent via email',
#             'total_records': len(user_scores),
#             'email_sent': email_sent
#         }
        
#     except Exception as e:
#         logger.error(f"Error in user CSV export: {str(e)}")
#         current_task.update_state(
#             state='FAILURE',
#             meta={'error': str(e)}
#         )
#         raise
