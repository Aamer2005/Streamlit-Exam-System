import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from utils.auth import *
    from utils.database import Database
except ImportError as e:
    st.error(f"Import error: {e}")

# Page configuration
st.set_page_config(
    page_title="Online Examination System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .exam-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'db' not in st.session_state:
        try:
            st.session_state.db = Database()
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return
    
    if not st.session_state.user:
        show_login_page()
    else:
        user = st.session_state.user
        show_dashboard(user)

def show_login_page():
    st.markdown('<div class="main-header">📝 Online Examination System</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Student Registration"])
        
        with tab1:
            st.subheader("Login to Your Account")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        try:
                            db = st.session_state.db
                            user = db.authenticate_user(username, password)
                            if user:
                                st.session_state.user = user
                                st.success("Login successful!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Invalid username or password")
                        except Exception as e:
                            st.error(f"Login error: {e}")
        
        with tab2:
            st.subheader("Student Registration")
            
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name")
                    email = st.text_input("Email")
                
                with col2:
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                
                submit = st.form_submit_button("Register")
                
                if submit:
                    if not all([name, email, username, password, confirm_password]):
                        st.error("All fields are required")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        try:
                            db = st.session_state.db
                            user_id, error = db.create_user(username, password, "student", name, email)
                            if user_id:
                                st.success("Registration successful! You can now login.")
                            else:
                                st.error(f"Registration failed: {error}")
                        except Exception as e:
                            st.error(f"Registration error: {e}")

def show_dashboard(user):
    st.sidebar.title(f"Welcome, {user['name']}!")
    st.sidebar.write(f"Role: {user['role'].title()}")
    
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    if user['role'] == 'teacher':
        show_teacher_dashboard(user)
    elif user['role'] == 'student':
        show_student_dashboard(user)
    elif user['role'] == 'admin':
        show_admin_dashboard(user)

def show_teacher_dashboard(user):
    st.title("👨‍🏫 Teacher Dashboard")
    
    tab1, tab2 = st.tabs(["Manage Questions", "Manage Exams"])
    
    with tab1:
        st.subheader("Add New Question")
        
        with st.form("add_question_form"):
            question_text = st.text_area("Question Text")
            
            st.write("Options (Mark the correct answer):")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                option1 = st.text_input("Option 1")
            with col2:
                correct1 = st.radio("Correct", ["No", "Yes"], key="opt1", horizontal=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                option2 = st.text_input("Option 2")
            with col2:
                correct2 = st.radio("Correct", ["No", "Yes"], key="opt2", horizontal=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                option3 = st.text_input("Option 3")
            with col2:
                correct3 = st.radio("Correct", ["No", "Yes"], key="opt3", horizontal=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                option4 = st.text_input("Option 4")
            with col2:
                correct4 = st.radio("Correct", ["No", "Yes"], key="opt4", horizontal=True)
            
            submit = st.form_submit_button("Add Question")
            
            if submit:
                if not question_text or not all([option1, option2, option3, option4]):
                    st.error("All fields are required")
                else:
                    options_data = []
                    correct_options = [correct1, correct2, correct3, correct4]
                    option_texts = [option1, option2, option3, option4]
                    
                    for i, (opt_text, is_correct) in enumerate(zip(option_texts, correct_options)):
                        options_data.append({
                            "text": opt_text,
                            "isCorrect": is_correct == "Yes"
                        })
                    
                    question_data = {
                        "text": question_text,
                        "options": options_data
                    }
                    
                    try:
                        db = st.session_state.db
                        question_id = db.add_question(question_data, user['id'])
                        if question_id:
                            st.success("Question added successfully!")
                        else:
                            st.error("Failed to add question")
                    except Exception as e:
                        st.error(f"Error adding question: {e}")

def show_student_dashboard(user):
    st.title("👨‍🎓 Student Dashboard")
    
    tab1, tab2 = st.tabs(["Available Exams", "My Results"])
    
    with tab1:
        st.subheader("Available Exams")
        
        try:
            db = st.session_state.db
            exams = db.get_published_exams()
            
            if exams:
                for exam in exams:
                    with st.container():
                        st.markdown(f"""
                        <div class="exam-card">
                            <h4>{exam.get('title', 'Untitled Exam')}</h4>
                            <p>Duration: {exam.get('duration', 30)} minutes</p>
                            <p>Questions: {len(exam.get('questions', []))}</p>
                            <p>Created by: {exam.get('teacher', 'Unknown')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"Start Exam", key=f"start_{exam.get('id', '')}"):
                            st.session_state.current_exam = exam
                            st.session_state.exam_started = True
                            st.session_state.exam_start_time = datetime.now()
                            st.session_state.exam_answers = {}
                            st.rerun()
            else:
                st.info("No exams available at the moment.")
        
        except Exception as e:
            st.error(f"Error loading exams: {e}")
    
    # Exam taking interface
    if st.session_state.get('exam_started', False):
        show_exam_interface(user)
    
    with tab2:
        st.subheader("My Exam Results")
        
        try:
            db = st.session_state.db
            results = db.get_student_results(user['id'])
            
            if results:
                for result in results:
                    st.write(f"**{result.get('exam_title', 'Unknown Exam')}**")
                    st.write(f"Score: {result.get('score', 0)}/{result.get('total', 1)} ({result.get('percentage', 0):.1f}%)")
                    submitted_date = result.get('submittedAt', datetime.now())
                    if isinstance(submitted_date, str):
                        st.write(f"Date: {submitted_date}")
                    else:
                        st.write(f"Date: {submitted_date.strftime('%Y-%m-%d %H:%M')}")
                    st.divider()
            else:
                st.info("No exam results yet.")
        
        except Exception as e:
            st.error(f"Error loading results: {e}")

def show_exam_interface(user):
    if 'current_exam' not in st.session_state:
        st.error("No exam selected")
        return
        
    exam = st.session_state.current_exam
    duration = exam.get('duration', 30)
    start_time = st.session_state.exam_start_time
    end_time = start_time + timedelta(minutes=duration)
    current_time = datetime.now()
    
    time_left = end_time - current_time
    seconds_left = max(0, int(time_left.total_seconds()))
    
    # Timer
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader(f"Time Left: {seconds_left // 60:02d}:{seconds_left % 60:02d}")
    
    # Progress bar
    total_time = duration * 60
    progress = max(0, min(1, (total_time - seconds_left) / total_time))
    st.progress(progress)
    
    # Auto-submit when time is up
    if seconds_left <= 0:
        submit_exam(user, exam)
        return
    
    # Exam questions
    st.subheader(exam.get('title', 'Exam'))
    
    questions = exam.get('questions', [])
    for i, question in enumerate(questions, 1):
        st.write(f"**Question {i}: {question.get('text', 'No question text')}**")
        
        options = question.get('options', [])
        option_texts = [opt.get('text', '') for opt in options]
        
        selected_option = st.radio(
            f"Select your answer for Question {i}:",
            options=option_texts,
            key=f"q_{i}",
            index=None
        )
        
        if selected_option:
            selected_option_id = next((opt.get('_id', '') for opt in options if opt.get('text') == selected_option), '')
            st.session_state.exam_answers[str(question.get('_id', i))] = selected_option_id
    
    # Submit button
    if st.button("Submit Exam"):
        submit_exam(user, exam)

def submit_exam(user, exam):
    answers = []
    for question_id, selected_option_id in st.session_state.exam_answers.items():
        answers.append({
            "question_id": question_id,
            "selected_option_id": selected_option_id
        })
    
    try:
        db = st.session_state.db
        result_id, error = db.submit_exam_result(exam.get('id', ''), user['id'], answers)
        
        if result_id:
            st.success("Exam submitted successfully!")
            
            # Show score
            score = sum(1 for answer in answers if answer.get('selected_option_id'))
            total = len(exam.get('questions', []))
            
            st.subheader("Your Results")
            st.write(f"Score: {score}/{total}")
            st.write(f"Percentage: {(score/total)*100:.1f}%")
        else:
            st.error(f"Error submitting exam: {error}")
    
    except Exception as e:
        st.error(f"Error submitting exam: {e}")
    
    # Clean up session state
    for key in ['current_exam', 'exam_started', 'exam_start_time', 'exam_answers']:
        if key in st.session_state:
            del st.session_state[key]
    
    if st.button("Back to Dashboard"):
        st.rerun()

def show_admin_dashboard(user):
    st.title("👨‍💼 Admin Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["User Management", "System Overview", "Analytics"])
    
    with tab1:
        st.subheader("User Management")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Add New User")
            
            with st.form("add_user_form"):
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                role = st.selectbox("Role", ["student", "teacher", "admin"])
                
                submit = st.form_submit_button("Add User")
                
                if submit:
                    if not all([name, email, username, password]):
                        st.error("All fields are required")
                    else:
                        try:
                            db = st.session_state.db
                            user_id, error = db.create_user(username, password, role, name, email)
                            if user_id:
                                st.success("User created successfully!")
                            else:
                                st.error(f"Error creating user: {error}")
                        except Exception as e:
                            st.error(f"Error creating user: {e}")
        
        with col2:
            st.subheader("All Users")
            
            try:
                db = st.session_state.db
                users = db.get_all_users()
                
                if users:
                    for user in users:
                        st.write(f"**{user.get('name', 'No Name')}** ({user.get('role', 'student')})")
                        st.write(f"Username: {user.get('username', 'No username')} | Email: {user.get('email', 'No email')}")
                        created_date = user.get('createdAt', datetime.now())
                        if isinstance(created_date, str):
                            st.write(f"Created: {created_date}")
                        else:
                            st.write(f"Created: {created_date.strftime('%Y-%m-%d')}")
                        st.divider()
                else:
                    st.info("No users found.")
            
            except Exception as e:
                st.error(f"Error loading users: {e}")
    
    with tab2:
        st.subheader("System Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("All Exams")
            try:
                db = st.session_state.db
                exams = db.get_all_exams()
                
                if exams:
                    for exam in exams:
                        st.write(f"**{exam.get('title', 'Untitled')}**")
                        st.write(f"Duration: {exam.get('duration', 0)} min | Status: {'Published' if exam.get('isPublished') else 'Draft'}")
                        st.write(f"Teacher: {exam.get('teacher', 'Unknown')}")
                        st.divider()
                else:
                    st.info("No exams found.")
            except Exception as e:
                st.error(f"Error loading exams: {e}")
        
        with col2:
            st.subheader("All Results")
            try:
                db = st.session_state.db
                results = db.get_all_results()
                
                if results:
                    for result in results:
                        st.write(f"**{result.get('exam_title', 'Unknown')}**")
                        st.write(f"Student: {result.get('student_name', 'Unknown')}")
                        st.write(f"Score: {result.get('score', 0)}/{result.get('total', 1)} ({result.get('percentage', 0):.1f}%)")
                        st.divider()
                else:
                    st.info("No results found.")
            except Exception as e:
                st.error(f"Error loading results: {e}")
    
    with tab3:
        st.subheader("System Analytics")
        
        try:
            db = st.session_state.db
            analytics = db.get_analytics()
            
            if analytics:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Exams", analytics.get('total_exams', 0))
                with col2:
                    st.metric("Total Students", analytics.get('total_students', 0))
                with col3:
                    st.metric("Average Score", f"{analytics.get('average_score', 0):.1f}%")
                with col4:
                    st.metric("Total Attempts", analytics.get('total_attempts', 0))
            else:
                st.info("No analytics data available.")
        
        except Exception as e:
            st.error(f"Error loading analytics: {e}")

if __name__ == "__main__":
    main()