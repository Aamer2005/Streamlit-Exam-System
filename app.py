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
    .success-status {
        color: #28a745;
        font-weight: bold;
    }
    .draft-status {
        color: #dc3545;
        font-weight: bold;
    }
    .question-container {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
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
            # Remove the create_demo_data() call since it's now in Database
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
            
            # Demo accounts info
            with st.expander("Demo Accounts"):
                st.write("**Admin:** username: `admin`, password: `admin123`")
                st.write("**Teacher:** username: `teacher1`, password: `teacher123`")
                st.write("**Student:** Register a new account or use any credentials")
            
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["Manage Questions", "Create Exams", "My Questions", "Publish Exams"])
    
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
                            "isCorrect": is_correct == "Yes",
                            "id": f"opt_{i+1}"
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
                            st.rerun()
                        else:
                            st.error("Failed to add question")
                    except Exception as e:
                        st.error(f"Error adding question: {e}")
    
    with tab2:
        st.subheader("Create New Exam")
        
        with st.form("create_exam_form"):
            exam_title = st.text_input("Exam Title")
            duration = st.number_input("Duration (minutes)", min_value=5, max_value=180, value=30)
            
            # Get teacher's questions
            db = st.session_state.db
            questions = db.get_teacher_questions(user['id'])
            
            if questions:
                st.subheader("Select Questions for Exam")
                selected_questions = []
                for q in questions:
                    if st.checkbox(f"Q: {q.get('text', 'No text')[:50]}...", key=f"q_select_{q.get('_id', '')}"):
                        selected_questions.append(q.get('_id'))
                
                submit_exam = st.form_submit_button("Create Exam")
                
                if submit_exam:
                    if not exam_title:
                        st.error("Exam title is required")
                    elif not selected_questions:
                        st.error("Please select at least one question")
                    else:
                        exam_data = {
                            "title": exam_title,
                            "duration": duration,
                            "questions": selected_questions
                        }
                        exam_id = db.create_exam(exam_data, user['id'])
                        if exam_id:
                            st.success("Exam created successfully! Go to 'Publish Exams' tab to publish it.")
                            st.rerun()
                        else:
                            st.error("Failed to create exam")
            else:
                st.info("No questions available. Please add questions first.")
    
    with tab3:
        st.subheader("My Questions")
        try:
            db = st.session_state.db
            questions = db.get_teacher_questions(user['id'])
            
            if questions:
                st.write(f"Total Questions: {len(questions)}")
                for i, question in enumerate(questions, 1):
                    st.write(f"**Question {i}:** {question.get('text', 'No text')}")
                    options = question.get('options', [])
                    for j, option in enumerate(options, 1):
                        correct_indicator = " ✅" if option.get('isCorrect') else ""
                        st.write(f"  {j}. {option.get('text', '')}{correct_indicator}")
                    st.divider()
            else:
                st.info("No questions created yet.")
        except Exception as e:
            st.error(f"Error loading questions: {e}")
    
    with tab4:
        st.subheader("Publish Exams")
        try:
            db = st.session_state.db
            exams = db.get_teacher_exams(user['id'])
            
            if exams:
                st.write(f"Total Exams: {len(exams)}")
                for exam in exams:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{exam.get('title', 'Untitled Exam')}**")
                        st.write(f"Duration: {exam.get('duration', 30)} min | Questions: {len(exam.get('questions', []))}")
                        status = "🟢 Published" if exam.get('isPublished') else "🔴 Draft"
                        st.write(f"Status: {status}")
                    
                    with col2:
                        if not exam.get('isPublished'):
                            if st.button("Publish", key=f"publish_{exam.get('id', '')}"):
                                if db.publish_exam(exam.get('id', ''), user['id']):
                                    st.success("Exam published successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to publish exam")
                        else:
                            st.success("Published")
                    
                    with col3:
                        if st.button("View", key=f"view_{exam.get('id', '')}"):
                            st.session_state.view_exam = exam
                    
                    st.divider()
                
                # View exam details
                if st.session_state.get('view_exam'):
                    exam = st.session_state.view_exam
                    st.subheader(f"Exam Details: {exam.get('title', '')}")
                    
                    questions = exam.get('questions', [])
                    st.write(f"**Total Questions:** {len(questions)}")
                    st.write(f"**Duration:** {exam.get('duration', 30)} minutes")
                    st.write(f"**Status:** {'Published' if exam.get('isPublished') else 'Draft'}")
                    
                    for i, question in enumerate(questions, 1):
                        st.write(f"**Question {i}:** {question.get('text', 'No text')}")
                        options = question.get('options', [])
                        for j, option in enumerate(options, 1):
                            correct_indicator = " ✅" if option.get('isCorrect') else ""
                            st.write(f"  {j}. {option.get('text', '')}{correct_indicator}")
                        st.write("---")
                    
                    if st.button("Close View"):
                        del st.session_state.view_exam
                        st.rerun()
                        
            else:
                st.info("No exams created yet. Create an exam in the 'Create Exams' tab.")
        except Exception as e:
            st.error(f"Error loading exams: {e}")

def show_student_dashboard(user):
    st.title("👨‍🎓 Student Dashboard")
    
    # Check if exam is in progress
    if st.session_state.get('exam_started', False):
        show_exam_interface(user)
        return
    
    tab1, tab2 = st.tabs(["Available Exams", "My Results"])
    
    with tab1:
        st.subheader("Available Exams")
        
        try:
            db = st.session_state.db
            exams = db.get_published_exams()
            
            if exams:
                st.info(f"Found {len(exams)} published exam(s) available")
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
                            # Initialize exam session state
                            st.session_state.current_exam = exam
                            st.session_state.exam_started = True
                            st.session_state.exam_start_time = datetime.now()
                            st.session_state.exam_answers = {}
                            st.session_state.exam_submitted = False
                            st.rerun()
            else:
                st.info("No exams available at the moment. Check back later or contact your teacher.")
        
        except Exception as e:
            st.error(f"Error loading exams: {e}")
    
    with tab2:
        st.subheader("My Exam Results")
        
        try:
            db = st.session_state.db
            results = db.get_student_results(user['id'])
            
            if results:
                st.info(f"You have completed {len(results)} exam(s)")
                for result in results:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{result.get('exam_title', 'Unknown Exam')}**")
                        submitted_date = result.get('submittedAt', datetime.now())
                        if hasattr(submitted_date, 'strftime'):
                            st.write(f"Date: {submitted_date.strftime('%Y-%m-%d %H:%M')}")
                        else:
                            st.write(f"Date: {str(submitted_date)}")
                    with col2:
                        score = result.get('score', 0)
                        total = result.get('total', 1)
                        percentage = result.get('percentage', 0)
                        st.metric("Score", f"{score}/{total} ({percentage:.1f}%)")
                    st.divider()
            else:
                st.info("No exam results yet. Take an exam to see your results here.")
        
        except Exception as e:
            st.error(f"Error loading results: {e}")

def show_exam_interface(user):
    if 'current_exam' not in st.session_state or not st.session_state.get('exam_started', False):
        st.error("No exam in progress")
        # Clean up session state and return to dashboard
        for key in ['current_exam', 'exam_started', 'exam_start_time', 'exam_answers', 'exam_submitted']:
            if key in st.session_state:
                del st.session_state[key]
        if st.button("Back to Dashboard"):
            st.rerun()
        return
        
    exam = st.session_state.current_exam
    duration = exam.get('duration', 30)
    start_time = st.session_state.exam_start_time
    end_time = start_time + timedelta(minutes=duration)
    current_time = datetime.now()
    
    time_left = end_time - current_time
    seconds_left = max(0, int(time_left.total_seconds()))
    
    # Timer display
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        st.subheader(f"⏰ Time Left: {minutes:02d}:{seconds:02d}")
        
        # Warning when time is running out
        if seconds_left < 300 and seconds_left > 0:  # 5 minutes
            st.warning("Time is running out! Consider submitting your exam soon.")
    
    # Progress bar
    total_time = duration * 60
    progress = max(0, min(1, (total_time - seconds_left) / total_time))
    st.progress(progress)
    
    # Auto-submit when time is up
    if seconds_left <= 0 and not st.session_state.get('exam_submitted', False):
        st.error("⏰ Time's up! Submitting your exam automatically...")
        submit_exam(user, exam)
        return
    
    # Check if exam was already submitted
    if st.session_state.get('exam_submitted', False):
        st.info("Exam already submitted. Please go back to dashboard.")
        if st.button("Back to Dashboard"):
            for key in ['current_exam', 'exam_started', 'exam_start_time', 'exam_answers', 'exam_submitted']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        return
    
    # Exam questions
    st.subheader(f"📝 {exam.get('title', 'Exam')}")
    st.write(f"**Instructions:** Answer all questions. You have {duration} minutes to complete.")
    st.write("---")
    
    questions = exam.get('questions', [])
    
    # DEBUG: Show exam data
    if st.session_state.get('debug', False):
        with st.expander("Debug Info"):
            st.write("Exam ID:", exam.get('id'))
            st.write("Questions found:", len(questions))
            st.write("Questions data:", questions)
    
    if not questions:
        st.error("❌ No questions found in this exam. Please contact your teacher.")
        if st.button("Back to Dashboard"):
            for key in ['current_exam', 'exam_started', 'exam_start_time', 'exam_answers', 'exam_submitted']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        return
    
    # Initialize answers in session state if not exists
    if 'exam_answers' not in st.session_state:
        st.session_state.exam_answers = {}
    
    # Display questions
    all_answered = True
    for i, question in enumerate(questions, 1):
        st.markdown(f'<div class="question-container">', unsafe_allow_html=True)
        st.write(f"**Question {i}: {question.get('text', 'No question text')}**")
        
        options = question.get('options', [])
        if not options:
            st.warning("No options available for this question.")
            st.markdown('</div>', unsafe_allow_html=True)
            continue
            
        option_texts = [opt.get('text', f'Option {j+1}') for j, opt in enumerate(options)]
        option_ids = [opt.get('id', f'opt_{j+1}') for j, opt in enumerate(options)]
        
        # Get current answer or set to None
        question_key = str(question.get('_id', f'q_{i}'))
        current_answer = st.session_state.exam_answers.get(question_key, None)
        current_index = None
        
        if current_answer:
            try:
                current_index = option_ids.index(current_answer)
            except ValueError:
                current_index = None
        
        # Display radio buttons for options
        selected_option = st.radio(
            f"Select your answer for Question {i}:",
            options=option_texts,
            key=f"radio_{question_key}",
            index=current_index
        )
        
        if selected_option:
            selected_index = option_texts.index(selected_option)
            selected_option_id = option_ids[selected_index]
            st.session_state.exam_answers[question_key] = selected_option_id
        else:
            all_answered = False
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Submit section
    st.write("## Submit Exam")
    
    # Show answer status
    answered_count = len([v for v in st.session_state.exam_answers.values() if v is not None])
    total_questions = len(questions)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write(f"**Progress:** {answered_count}/{total_questions} questions answered")
        if answered_count < total_questions:
            st.warning(f"You have {total_questions - answered_count} unanswered questions.")
        else:
            st.success("All questions answered! You can submit your exam.")
    
    with col2:
        if st.button("⏹️ Save & Exit", help="Save progress and return to dashboard"):
            st.info("Progress saved. You can resume this exam later.")
            time.sleep(2)
            # Don't clear session state - allow resuming
            st.rerun()
    
    with col3:
        submit_disabled = answered_count == 0
        if st.button("✅ Submit Exam", type="primary", disabled=submit_disabled, 
                    help="Submit your answers for grading" if not submit_disabled else "Answer at least one question to submit"):
            if answered_count == 0:
                st.error("Please answer at least one question before submitting.")
            else:
                submit_exam(user, exam)

def submit_exam(user, exam):
    # Mark as submitted first to prevent double submission
    st.session_state.exam_submitted = True
    
    answers = []
    for question_id, selected_option_id in st.session_state.exam_answers.items():
        if selected_option_id:  # Only include answered questions
            answers.append({
                "question_id": question_id,
                "selected_option_id": selected_option_id
            })
    
    try:
        db = st.session_state.db
        result_id, error = db.submit_exam_result(exam.get('id', ''), user['id'], answers)
        
        if result_id:
            st.success("🎉 Exam submitted successfully!")
            
            # Calculate and display results
            questions = exam.get('questions', [])
            total_questions = len(questions)
            score = 0
            
            # Calculate actual score
            for answer in answers:
                question_id = answer.get('question_id')
                selected_option_id = answer.get('selected_option_id')
                
                # Find the question
                question = next((q for q in questions if str(q.get('_id', '')) == question_id), None)
                if question:
                    options = question.get('options', [])
                    selected_option = next((opt for opt in options if opt.get('id') == selected_option_id), None)
                    if selected_option and selected_option.get('isCorrect'):
                        score += 1
            
            percentage = (score / total_questions) * 100 if total_questions > 0 else 0
            
            st.balloons()
            st.subheader("📊 Your Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{score}/{total_questions}")
            with col2:
                st.metric("Percentage", f"{percentage:.1f}%")
            with col3:
                status = "🎯 Pass" if percentage >= 60 else "❌ Fail"
                st.metric("Status", status)
            
            # Show detailed results
            with st.expander("View Detailed Results"):
                for i, question in enumerate(questions, 1):
                    st.write(f"**Question {i}:** {question.get('text', 'No text')}")
                    
                    # Find user's answer
                    question_key = str(question.get('_id', f'q_{i}'))
                    user_answer_id = st.session_state.exam_answers.get(question_key, None)
                    options = question.get('options', [])
                    
                    for j, option in enumerate(options, 1):
                        option_text = option.get('text', f'Option {j}')
                        is_correct = option.get('isCorrect', False)
                        is_user_answer = option.get('id') == user_answer_id
                        
                        if is_user_answer and is_correct:
                            st.write(f"  ✅ {j}. {option_text} (Your Answer - Correct)")
                        elif is_user_answer and not is_correct:
                            st.write(f"  ❌ {j}. {option_text} (Your Answer - Incorrect)")
                        elif is_correct:
                            st.write(f"  ✓ {j}. {option_text} (Correct Answer)")
                        else:
                            st.write(f"  {j}. {option_text}")
                    
                    st.write("---")
        else:
            st.error(f"Error submitting exam: {error}")
            # Allow retry if submission failed
            st.session_state.exam_submitted = False
    
    except Exception as e:
        st.error(f"Error submitting exam: {e}")
        # Allow retry if submission failed
        st.session_state.exam_submitted = False
    
    # Back to dashboard button
    st.write("---")
    if st.button("🏠 Back to Dashboard"):
        # Clean up session state
        for key in ['current_exam', 'exam_started', 'exam_start_time', 'exam_answers', 'exam_submitted']:
            if key in st.session_state:
                del st.session_state[key]
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
                                st.rerun()
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
                    st.info(f"Total Users: {len(users)}")
                    for user in users:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{user.get('name', 'No Name')}** ({user.get('role', 'student')})")
                            st.write(f"Username: {user.get('username', 'No username')} | Email: {user.get('email', 'No email')}")
                            created_date = user.get('createdAt', datetime.now())
                            if hasattr(created_date, 'strftime'):
                                st.write(f"Created: {created_date.strftime('%Y-%m-%d')}")
                            else:
                                st.write(f"Created: {created_date}")
                        with col2:
                            st.write(f"ID: {user.get('_id', '')[:8]}...")
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
                    st.info(f"Total Exams: {len(exams)}")
                    for exam in exams:
                        status_class = "success-status" if exam.get('isPublished') else "draft-status"
                        status_text = "Published" if exam.get('isPublished') else "Draft"
                        
                        st.write(f"**{exam.get('title', 'Untitled')}**")
                        st.write(f"Duration: {exam.get('duration', 0)} min | Status: <span class='{status_class}'>{status_text}</span>", unsafe_allow_html=True)
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
                    st.info(f"Total Results: {len(results)}")
                    for result in results:
                        st.write(f"**{result.get('exam_title', 'Unknown')}**")
                        st.write(f"Student: {result.get('student_name', 'Unknown')}")
                        st.write(f"Score: {result.get('score', 0)}/{result.get('total', 1)} ({result.get('percentage', 0):.1f}%)")
                        submitted_date = result.get('submittedAt', datetime.now())
                        if hasattr(submitted_date, 'strftime'):
                            st.write(f"Submitted: {submitted_date.strftime('%Y-%m-%d %H:%M')}")
                        else:
                            st.write(f"Submitted: {submitted_date}")
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
                
                # Add a simple chart
                if analytics.get('total_attempts', 0) > 0:
                    fig = px.pie(
                        values=[analytics.get('average_score', 0), 100 - analytics.get('average_score', 0)],
                        names=['Average Score', 'Remaining'],
                        title='Overall Performance'
                    )
                    st.plotly_chart(fig)
            else:
                st.info("No analytics data available.")
        
        except Exception as e:
            st.error(f"Error loading analytics: {e}")

if __name__ == "__main__":
    main()