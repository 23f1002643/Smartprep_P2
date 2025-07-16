from flask import Flask, jsonify 
from flask_restful import Api, abort
import os
from flask_jwt_extended import JWTManager, exceptions as jwt_exceptions
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError
from datetime import datetime, timezone
from backend.models import db, Account
from backend.config import config_settings
from backend.worker import *
from backend.api  import (
    AccountRegisterAPI,
    AccountLoginAPI,
    AccountLogoutAPI,
    AccountDashboardAPI,
    SubManagementAPI,
    ModuleMngAPI,
    QueMngAPI,
    AssessmentMngAPI,
    UserMngAPI,
    caching, jwt_blocklist
)

def init_app(): # Function to initialize Flask app
    instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))

    # Creating the instance folder 
    os.makedirs(instance_path, exist_ok=True)
    print(f"✅ Instance folder ensured at: {instance_path}") 
    ns = Flask(__name__, instance_relative_config=True, instance_path=instance_path, template_folder=os.path.join('backend', 'templates'))
    ns.config.from_mapping(config_settings) 
    db.init_app(ns)
    caching.init_app(ns)  # Initializing cache with Flask app
    with ns.app_context():
        db.create_all()
        print("✅ Database tables created successfully.") 
        admin = Account.query.filter_by(username='admin').first()
        if not admin:
            new_admin = Account(
                username='admin',
                f_name='Quiz',
                l_name='Master',
                pwd='quiz12345', 
                edu_qul='Graduate',
                role='admin',
                email='admin@quizmaster.com', 
                mobile_no='9988776655',
                dob=datetime.strptime("2000-01-01", "%Y-%m-%d").date(), 
                active=True
            ) 
            db.session.add(new_admin)
            db.session.commit()
            print("✅ Default admin account created.") 
        else:
            print("ℹ️ Admin account already exists.") 
    return ns

ns = init_app() 
celery = make_celery(ns)
print("✅ Celery initialized with Flask app.")
celery.conf.beat_schedule = CeleryConfig.beat_schedule
my_api = Api(ns)

ns.config['JWT_SECRET_KEY'] = config_settings['SECRET_KEY']
ns.config['JWT_ACCESS_TOKEN_EXPIRES'] = config_settings['JWT_ACCESS_TOKEN_EXPIRES']
ns.config['CACHE_TYPE'] = config_settings['CACHE_TYPE']
ns.config['CACHE_REDIS_HOST'] = config_settings['REDIS_HOST']
ns.config['CACHE_REDIS_PORT'] = config_settings['REDIS_PORT']
ns.config['CACHE_REDIS_DB'] = config_settings['REDIS_DB_CACHE']
ns.config['CACHE_DEFAULT_TIMEOUT'] = 300  
ns.config['CACHE_REDIS_URL'] = config_settings['CACHE_REDIS_URL']

jwt = JWTManager(ns)
# <------------------------------------------------Admin APIs---------------------------------------------------------------->
my_api.add_resource(ModuleMngAPI,'/api/admin/sub/<int:sub_id>/chap', '/api/admin/sub/<int:sub_id>/chap/<int:chap_id>')
my_api.add_resource(QueMngAPI, '/api/admin/sub/<int:sub_id>/chap/<int:chap_id>/quiz/<int:exam_id>/que', '/api/admin/sub/<int:sub_id>/chap/<int:chap_id>/quiz/<int:exam_id>/que/<int:que_id>')
my_api.add_resource(AssessmentMngAPI, '/api/chap/<int:chap_id>/quiz', '/api/admin/sub/<int:sub_id>/chap/<int:chap_id>/quiz/<int:exam_id>')
my_api.add_resource(AccountRegisterAPI, '/api/register')
my_api.add_resource(AccountLoginAPI, '/api/login')
my_api.add_resource(AccountLogoutAPI, '/api/logout') 
my_api.add_resource(AccountDashboardAPI, '/api/dashboard')
my_api.add_resource(SubManagementAPI, '/api/sub', '/api/sub/<int:sub_id>')
my_api.add_resource(UserMngAPI, '/api/admin/user', '/api/admin/user/<int:user_id>')


jwt_blocklist = config_settings['JWT_BLOCKLIST']

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

# @jwt.expired_token_loader
# def expired_token_callback(jwt_header, jwt_payload):
#     print("Token expired!")
#     return {"msg": "Token has expired"}, 401

# @jwt.invalid_token_loader
# def invalid_token_callback(error):
#     print(f"Invalid token: {error}")
#     return {"msg": "Invalid token"}, 422

# @jwt.unauthorized_loader
# def missing_token_callback(error):
#     print(f"Missing token: {error}")
#     return {"msg": "Authorization token is required"}, 401

if __name__ == '__main__':   
    ns.run(debug=True)
