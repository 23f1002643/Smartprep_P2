# 🧠 QuizMaster - Flask + Vue + Redis + Celery App

A full-stack quiz application built with **Flask** (Python) for the backend, **Vue 3** for the frontend, **Redis** for caching and Celery task queue management, and **MailHog** for development email testing.

---

## 🚀 Features

- 👨‍🏫 Admin panel to manage subjects, chapters, quizzes, and questions  
- 🧑‍🎓 User dashboard to take quizzes and view results  
- 📊 Score tracking and statistics  
- ✉️ Daily reminders and monthly reports via email (async with Celery)  
- 📥 Admin CSV export via Celery + Email  
- ⚡ Redis caching and task queuing  

---

## ⚙️ Setup Instructions

### 📦 Backend Setup (Flask + Celery + Redis)

#### 1. Clone the Repository

### 📦 Backend Setup (Flask + Celery + Redis)

#### 1. Clone the Repository

#### 2. Create a Virtual Environment and Activate It
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the Flask App
```bash
python3 app.py
# By default, the Flask app will run on: http://localhost:5000/
```

#### 5. Start Redis Server
```bash
redis-server
# ✅ Verify Redis is running
redis-cli ping
# Output: PONG
```
### for clear redis cache
```bash
redis-cli -n 1 FLUSHDB  # or redis-cli -n 0 FLUSHDB
```
#### 6. Start Celery Worker
```bash
python3 -m celery -A app.celery worker --loglevel=info
```

#### 7. Start Celery Beat Scheduler
```bash
python3 -m celery -A app.celery beat --loglevel=info
```

### 🌐 Frontend Setup (Vue 3)

#### 1. Move into Frontend Directory
```bash
cd frontend
```

#### 2. Install Node Modules
```bash
npm install
```

#### 3. Start the Vue Development Server
```bash
npm run dev
# By default, the frontend runs on: http://localhost:5173/
```

### 📧 Mail Testing with MailHog

#### 1. Start MailHog
```bash
mailhog
```

#### 2. View the Mail UI
Open in browser:
```arduino
http://localhost:8025
```

### 📌 Notes
- Ensure that Redis and MailHog are running before starting Flask or Celery.
- You can create a `.env` file to store environment variables like `MAIL_USER`, `MAIL_PASS`, `JWT_SECRET`, `REDIS_URL`, etc.
- The app will create a default admin user if one doesn’t exist.
- Use the CSV export feature to download and email user statistics asynchronously using Celery.

