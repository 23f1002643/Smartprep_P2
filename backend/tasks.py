from celery import shared_task
from backend.worker import *
from backend.models import db, Account, Assessment, ExamPerformance, CourseModule, Courses
from datetime import datetime, timedelta
from sqlalchemy import func
from backend.config import config_settings
import smtplib, os, tempfile, shutil, csv, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

@shared_task
def greeting_task():
    print("Hello from the Celery task!")
    return "Greeting task completed successfully!"

def send_email(to_email, sub, body, att_path=None):
    smtp_server = config_settings['MAIL_SERVER']
    smtp_port = config_settings['MAIL_PORT']
    sender_email= config_settings['MAIL_DEFAULT_SENDER']
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = sub

        # Attach the HTML body
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
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
    from app import ns
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
                    <a href="http://localhost:5173/" style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Start Quiz Now!</a>
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
    start_date = today.replace(day=1)
    end_date = today + timedelta(days=1)

    users = Account.query.filter_by(active=True, role='user').all()

    total_users = len(users)
    reports_sent = 0

    for i, user in enumerate(users):
        scores = ExamPerformance.query.filter(
            ExamPerformance.user_id == user.id,
            ExamPerformance.time_of_attempt >= start_date,
            ExamPerformance.time_of_attempt < end_date
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

            month_name = end_date.strftime('%B %Y')
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
        'month': end_date.strftime('%B %Y')
    }

def create_monthly_report_template(user, quiz_details, total_quizzes, average_score, month):
    quiz_rows_html = "".join(f"""
        <tr>
            <td>{quiz['quiz_name']}</td>
            <td>{quiz['subject']}</td>
            <td>{quiz['chapter']}</td>
            <td>{quiz['score']}/{quiz['max_marks']}</td>
            <td>{quiz['percentage']}%</td>
            <td>{quiz['date']} {quiz['time']}</td>
        </tr>
    """ for quiz in quiz_details)

    plural_suffix = 'es' if total_quizzes != 1 else ''

    performance_feedback = (
        "Excellent work! Keep it up!" if average_score >= 80 else
        "Good effort! Try to improve your score next month." if average_score >= 60 else
        "There's room for improvement. Practice more to boost your scores!"
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Monthly Activity Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f8f9fa; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat-box {{ background-color: white; padding: 20px; border-radius: 5px; text-align: center; min-width: 150px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background-color: #e9ecef; padding: 10px; text-align: left; }}
            td {{ padding: 8px; border-bottom: 1px solid #eee; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6c757d; }}
        </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h2>📊 Monthly Activity Report - {month}</h2>
            <p>Your Quiz Performance Summary</p>
        </div>
        <div class="content">
            <h3>Hello {user.f_name} {user.l_name}!</h3>
            <p>Here's your quiz performance summary for {month}. Keep up the great work!</p>

            <div class="stats">
                <div class="stat-box">
                    <h4>🎯 Total Quizzes</h4>
                    <h2>{total_quizzes}</h2>
                </div>
                <div class="stat-box">
                    <h4>📈 Average Score</h4>
                    <h2>{average_score}%</h2>
                </div>
            </div>

            <h4>📚 Detailed Quiz Results:</h4>
            <table>
                <thead>
                    <tr>
                        <th>Quiz Name</th>
                        <th>Subject</th>
                        <th>Chapter</th>
                        <th>Score</th>
                        <th>Percentage</th>
                        <th>Date & Time</th>
                    </tr>
                </thead>
                <tbody>
                    {quiz_rows_html}
                </tbody>
            </table>

            <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h4>💡 Performance Insights:</h4>
                <ul>
                    <li>You completed {total_quizzes} quiz{plural_suffix} this month</li>
                    <li>Your average score was {average_score}%</li>
                    <li>{performance_feedback}</li>
                </ul>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5173/" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Continue Learning</a>
            </div>
        </div>
        <div class="footer">
            <p>Best regards,<br>Quiz Master Team</p>
            <p><small>This report was automatically generated based on your quiz activity.</small></p>
        </div>
    </div>
    </body>
    </html>
    """

@shared_task(bind=True, name='export_user_data_by_admin')
def export_user_data_by_admin(self, admin_id):
    self.update_state(
        state='PROGRESS',
        meta={'current': 0, 'total': 100, 'status': 'Starting user data export...'}
    )
    from app import ns # for delay due to circular import
    with ns.app_context():
        admin = Account.query.get(admin_id)
        if not admin or admin.role != 'admin':
            self.update_state(state='FAILURE', meta={'status': 'Error', 'message': 'Unauthorized access'})
            return {'status': 'error', 'message': 'Unauthorized access'}

        users = Account.query.filter_by(role='user').all()
        if not users:
            self.update_state(state='FAILURE', meta={'status': 'Error', 'message': 'No users found to export'})
            return {'status': 'error', 'message': 'No users found'}
        
        temp_dir = tempfile.mkdtemp()
        csv_filename = f"admin_users_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path = os.path.join(temp_dir, csv_filename)

        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Generating CSV file...'}
        )
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'user_id', 'username', 'full_name', 'email', 'mobile_no',
                'qualification', 'dob', 'registration_date', 'active_status',
                'total_quizzes_taken', 'total_score', 'total_max_marks',
                'average_percentage', 'last_quiz_date', 'performance_level'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            total_users = len(users)
            for i, user in enumerate(users):
                user_scores = ExamPerformance.query.filter_by(user_id=user.id).all()
                total_quizzes = len(user_scores)
                total_score = sum(score.score for score in user_scores)
                total_max_marks = sum(score.max_marks for score in user_scores)
                average_percentage = round((total_score / total_max_marks) * 100, 2) if total_max_marks > 0 else 0
                last_quiz_date = ''
                if user_scores:
                    last_attempt = max(user_scores, key=lambda x: x.time_of_attempt)
                    last_quiz_date = last_attempt.time_of_attempt.strftime('%Y-%m-%d %H:%M:%S')
                performance_level = (
                    'Excellent' if average_percentage >= 80 else
                    'Good' if average_percentage >= 60 else
                    'Average' if average_percentage >= 40 else
                    'Below Average'
                )
                writer.writerow({
                    'user_id': user.id, 'username': user.username, 'full_name': f"{user.f_name} {user.l_name}",
                    'email': user.email, 'mobile_no': user.mobile_no, 'qualification': user.edu_qul,
                    'dob': user.dob, 'registration_date': user.reg_date, 'active_status': user.active,
                    'total_quizzes_taken': total_quizzes, 'total_score': total_score, 'total_max_marks': total_max_marks,
                    'average_percentage': average_percentage, 'last_quiz_date': last_quiz_date, 'performance_level': performance_level
                })   
                progress = 20 + int((i + 1) / total_users * 60)
                self.update_state(
                    state='PROGRESS',
                    meta={'current': progress, 'total': 100, 'status': f'Processing user {i + 1}/{total_users}'}
                )   
        self.update_state(
            state='PROGRESS',
            meta={'current': 85, 'total': 100, 'status': 'Sending CSV via email...'}
        )  
        admin_name = f"{admin.f_name} {admin.l_name}"
        export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        email_body = f"""
        <html>
        <body>
            <p>Hello {admin_name},</p>
            <p>Your requested user data export is complete and attached to this email.</p>
        </body>
        </html>
        """

        subject = f"Admin User Data Export - {export_time}"
        email_sent = send_email(admin.email, subject, email_body, csv_path)
        shutil.rmtree(temp_dir)
        
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Export completed successfully!'}
        )

    return {
        'status': 'completed',
        'message': 'CSV export completed and sent via email',
        'total_users': len(users),
        'email_sent': email_sent
    }
