import pymongo
from bson import ObjectId
import bcrypt
from datetime import datetime
import streamlit as st
import random

class Database:
    def __init__(self):
        try:
            # Try local MongoDB first
            try:
                self.client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
                self.client.admin.command('ismaster')
                st.success("✅ Connected to local MongoDB!")
                self.using_mongodb = True
            except:
                st.info("📋 Using in-memory database for demo")
                self.using_mongodb = False
                self._setup_in_memory()
                return
                
            self.db = self.client["examSystem"]
            self.users = self.db["users"]
            self.questions = self.db["questions"]
            self.exams = self.db["exams"]
            self.results = self.db["results"]
            self._create_indexes()
            self._create_admin_user()
        except Exception as e:
            st.error(f"Database setup error: {e}")
            self.using_mongodb = False
            self._setup_in_memory()

    def _setup_in_memory(self):
        """Setup in-memory storage for demo purposes"""
        self.users_data = []
        self.questions_data = []
        self.exams_data = []
        self.results_data = []
        self._create_admin_user_memory()
        
        # Create demo questions and exams
        self._create_demo_data()

    def _create_demo_data(self):
        """Create demo questions and exams"""
        # Create demo teacher
        teacher_id = "teacher_001"
        hashed_password = self._hash_password('teacher123')
        self.users_data.append({
            "_id": teacher_id,
            "username": "teacher1",
            "password": hashed_password,
            "role": "teacher",
            "name": "Demo Teacher",
            "email": "teacher@demo.com",
            "createdAt": datetime.now()
        })
        
        # Create demo questions
        demo_questions = [
            {
                "_id": "q_1",
                "text": "What is the capital of France?",
                "options": [
                    {"text": "London", "isCorrect": False, "id": "opt_1"},
                    {"text": "Paris", "isCorrect": True, "id": "opt_2"},
                    {"text": "Berlin", "isCorrect": False, "id": "opt_3"},
                    {"text": "Madrid", "isCorrect": False, "id": "opt_4"}
                ],
                "createdBy": teacher_id,
                "createdAt": datetime.now()
            },
            {
                "_id": "q_2",
                "text": "Which programming language is known for its use in web development?",
                "options": [
                    {"text": "Python", "isCorrect": False, "id": "opt_1"},
                    {"text": "JavaScript", "isCorrect": True, "id": "opt_2"},
                    {"text": "C++", "isCorrect": False, "id": "opt_3"},
                    {"text": "Java", "isCorrect": False, "id": "opt_4"}
                ],
                "createdBy": teacher_id,
                "createdAt": datetime.now()
            },
            {
                "_id": "q_3",
                "text": "What does CPU stand for?",
                "options": [
                    {"text": "Computer Processing Unit", "isCorrect": False, "id": "opt_1"},
                    {"text": "Central Processing Unit", "isCorrect": True, "id": "opt_2"},
                    {"text": "Central Program Utility", "isCorrect": False, "id": "opt_3"},
                    {"text": "Computer Program Unit", "isCorrect": False, "id": "opt_4"}
                ],
                "createdBy": teacher_id,
                "createdAt": datetime.now()
            }
        ]
        
        self.questions_data.extend(demo_questions)
        
        # Create demo exams
        demo_exams = [
            {
                "_id": "exam_1",
                "title": "Geography Basics",
                "duration": 5,
                "questions": ["q_1"],  # Only first question
                "createdBy": teacher_id,
                "isPublished": True,  # Published by default
                "createdAt": datetime.now()
            },
            {
                "_id": "exam_2",
                "title": "Programming Fundamentals", 
                "duration": 10,
                "questions": ["q_2"],  # Only second question
                "createdBy": teacher_id,
                "isPublished": False,  # Not published
                "createdAt": datetime.now()
            },
            {
                "_id": "exam_3",
                "title": "Computer Science Test",
                "duration": 15,
                "questions": ["q_1", "q_2", "q_3"],  # All questions
                "createdBy": teacher_id,
                "isPublished": True,  # Published by default
                "createdAt": datetime.now()
            }
        ]
        
        self.exams_data.extend(demo_exams)

    def _create_admin_user_memory(self):
        """Create admin user in memory"""
        admin_exists = any(user.get('username') == 'admin' for user in self.users_data)
        if not admin_exists:
            hashed_password = self._hash_password('admin123')
            self.users_data.append({
                "_id": "admin_001",
                "username": "admin",
                "password": hashed_password,
                "role": "admin",
                "name": "System Administrator",
                "email": "admin@examsystem.com",
                "createdAt": datetime.now()
            })

    def _hash_password(self, password):
        """Hash password with proper encoding"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _check_password(self, password, hashed_password):
        """Check password with proper encoding"""
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def _create_indexes(self):
        try:
            self.users.create_index("username", unique=True)
            self.users.create_index("email", unique=True)
            self.questions.create_index("createdBy")
        except:
            pass

    def _create_admin_user(self):
        admin_exists = self.users.find_one({"username": "admin"})
        if not admin_exists:
            hashed_password = self._hash_password("admin123")
            self.users.insert_one({
                "username": "admin",
                "password": hashed_password,
                "role": "admin",
                "name": "System Administrator",
                "email": "admin@examsystem.com",
                "createdAt": datetime.now()
            })

    # User Management Methods
    def create_user(self, username, password, role, name, email):
        try:
            # Check if username already exists
            if self.using_mongodb:
                existing_user = self.users.find_one({"username": username})
            else:
                existing_user = next((u for u in self.users_data if u.get('username') == username), None)
            
            if existing_user:
                return None, "Username already exists"
                
            hashed_password = self._hash_password(password)
            user_data = {
                "username": username,
                "password": hashed_password,
                "role": role,
                "name": name,
                "email": email,
                "createdAt": datetime.now()
            }
            
            if self.using_mongodb:
                result = self.users.insert_one(user_data)
                return str(result.inserted_id), None
            else:
                user_data["_id"] = f"user_{len(self.users_data) + 1}"
                self.users_data.append(user_data)
                return user_data["_id"], None
                
        except Exception as e:
            return None, str(e)

    def authenticate_user(self, username, password):
        try:
            if self.using_mongodb:
                user = self.users.find_one({"username": username})
            else:
                user = next((u for u in self.users_data if u.get('username') == username), None)
            
            if user and self._check_password(password, user.get('password', '')):
                return {
                    "id": str(user.get("_id", "")),
                    "username": user.get("username", ""),
                    "role": user.get("role", "student"),
                    "name": user.get("name", "")
                }
            return None
        except Exception as e:
            st.error(f"Auth error: {e}")
            return None

    def get_user_by_id(self, user_id):
        try:
            if self.using_mongodb:
                user = self.users.find_one({"_id": ObjectId(user_id)})
            else:
                user = next((u for u in self.users_data if u.get('_id') == user_id), None)
            
            if user:
                return {
                    "id": str(user.get("_id", "")),
                    "username": user.get("username", ""),
                    "role": user.get("role", ""),
                    "name": user.get("name", ""),
                    "email": user.get("email", "")
                }
            return None
        except:
            return None

    def get_all_users(self):
        try:
            if self.using_mongodb:
                users = self.users.find({}, {"password": 0})
                user_list = []
                for user in users:
                    user_list.append({
                        "_id": str(user.get("_id", "")),
                        "username": user.get("username", ""),
                        "role": user.get("role", ""),
                        "name": user.get("name", ""),
                        "email": user.get("email", ""),
                        "createdAt": user.get("createdAt", datetime.now())
                    })
                return user_list
            else:
                # Return users without passwords and ensure createdAt exists
                user_list = []
                for user in self.users_data:
                    user_list.append({
                        "_id": user.get("_id", ""),
                        "username": user.get("username", ""),
                        "role": user.get("role", ""),
                        "name": user.get("name", ""),
                        "email": user.get("email", ""),
                        "createdAt": user.get("createdAt", datetime.now())
                    })
                return user_list
        except Exception as e:
            st.error(f"Error getting users: {e}")
            return []

    # Question Management Methods
    def add_question(self, question_data, teacher_id):
        try:
            question_data["createdBy"] = teacher_id
            question_data["createdAt"] = datetime.now()
            
            if self.using_mongodb:
                result = self.questions.insert_one(question_data)
                return str(result.inserted_id)
            else:
                question_data["_id"] = f"q_{len(self.questions_data) + 1}"
                self.questions_data.append(question_data)
                return question_data["_id"]
        except Exception as e:
            st.error(f"Error adding question: {e}")
            return None

    def get_teacher_questions(self, teacher_id):
        try:
            if self.using_mongodb:
                questions = self.questions.find({"createdBy": teacher_id})
                return list(questions)
            else:
                return [q for q in self.questions_data if q.get('createdBy') == teacher_id]
        except:
            return []

    # Exam Management Methods
    def create_exam(self, exam_data, teacher_id):
        try:
            exam_data["createdBy"] = teacher_id
            exam_data["createdAt"] = datetime.now()
            exam_data["isPublished"] = False
            
            if self.using_mongodb:
                result = self.exams.insert_one(exam_data)
                return str(result.inserted_id)
            else:
                exam_data["_id"] = f"exam_{len(self.exams_data) + 1}"
                self.exams_data.append(exam_data)
                return exam_data["_id"]
        except Exception as e:
            st.error(f"Error creating exam: {e}")
            return None

    def get_teacher_exams(self, teacher_id):
        try:
            if self.using_mongodb:
                exams = self.exams.find({"createdBy": teacher_id})
                exam_list = []
                for exam in exams:
                    # Get questions for this exam
                    question_ids = exam.get("questions", [])
                    questions = []
                    for qid in question_ids:
                        question = self.questions.find_one({"_id": ObjectId(qid)})
                        if question:
                            questions.append(question)
                    
                    exam_data = {
                        "id": str(exam.get("_id", "")),
                        "title": exam.get("title", ""),
                        "duration": exam.get("duration", 30),
                        "questions": questions,
                        "isPublished": exam.get("isPublished", False),
                        "createdAt": exam.get("createdAt", datetime.now())
                    }
                    exam_list.append(exam_data)
                return exam_list
            else:
                teacher_exams = [e for e in self.exams_data if e.get('createdBy') == teacher_id]
                exam_list = []
                for exam in teacher_exams:
                    # Get questions for this exam
                    question_ids = exam.get('questions', [])
                    questions = []
                    for qid in question_ids:
                        question = next((q for q in self.questions_data if q.get('_id') == qid), None)
                        if question:
                            questions.append(question)
                    
                    exam_data = {
                        "id": exam.get("_id", ""),
                        "title": exam.get("title", ""),
                        "duration": exam.get("duration", 30),
                        "questions": questions,
                        "isPublished": exam.get("isPublished", False),
                        "createdAt": exam.get("createdAt", datetime.now())
                    }
                    exam_list.append(exam_data)
                return exam_list
        except Exception as e:
            st.error(f"Error getting teacher exams: {e}")
            return []

    def publish_exam(self, exam_id, teacher_id):
        try:
            if self.using_mongodb:
                result = self.exams.update_one(
                    {"_id": ObjectId(exam_id), "createdBy": teacher_id},
                    {"$set": {"isPublished": True}}
                )
                return result.modified_count > 0
            else:
                exam = next((e for e in self.exams_data if e.get('_id') == exam_id and e.get('createdBy') == teacher_id), None)
                if exam:
                    exam["isPublished"] = True
                    return True
                return False
        except Exception as e:
            st.error(f"Error publishing exam: {e}")
            return False

    def get_published_exams(self):
        try:
            if self.using_mongodb:
                exams = self.exams.find({"isPublished": True})
                exam_list = []
                for exam in exams:
                    # Get teacher info
                    teacher = self.get_user_by_id(exam.get("createdBy", ""))
                    
                    # Get questions for this exam
                    question_ids = exam.get("questions", [])
                    questions = []
                    for qid in question_ids:
                        question = self.questions.find_one({"_id": ObjectId(qid)})
                        if question:
                            questions.append(question)
                    
                    exam_data = {
                        "id": str(exam.get("_id", "")),
                        "title": exam.get("title", ""),
                        "duration": exam.get("duration", 30),
                        "questions": questions,
                        "teacher": teacher.get("name", "Unknown") if teacher else "Unknown",
                        "isPublished": exam.get("isPublished", False)
                    }
                    exam_list.append(exam_data)
                return exam_list
            else:
                # In-memory database
                published_exams = [e for e in self.exams_data if e.get('isPublished')]
                exam_list = []
                for exam in published_exams:
                    # Get questions for this exam
                    question_ids = exam.get('questions', [])
                    questions = []
                    for qid in question_ids:
                        question = next((q for q in self.questions_data if q.get('_id') == qid), None)
                        if question:
                            questions.append(question)
                    
                    exam_data = {
                        "id": exam.get("_id", ""),
                        "title": exam.get("title", ""),
                        "duration": exam.get("duration", 30),
                        "questions": questions,
                        "teacher": "Demo Teacher",
                        "isPublished": exam.get("isPublished", False)
                    }
                    exam_list.append(exam_data)
                return exam_list
        except Exception as e:
            st.error(f"Error getting published exams: {e}")
            return []

    # Results Management
    def submit_exam_result(self, exam_id, student_id, answers):
        try:
            if self.using_mongodb:
                exam = self.exams.find_one({"_id": ObjectId(exam_id)})
            else:
                exam = next((e for e in self.exams_data if e.get('_id') == exam_id), None)
                
            if not exam:
                return None, "Exam not found"

            # Calculate actual score based on correct answers
            score = 0
            total_questions = len(exam.get('questions', []))
            
            for answer in answers:
                question_id = answer.get('question_id')
                selected_option_id = answer.get('selected_option_id')
                
                if not selected_option_id:
                    continue  # Skip unanswered questions
                    
                # Find the question
                if self.using_mongodb:
                    question = self.questions.find_one({"_id": ObjectId(question_id)})
                else:
                    question = next((q for q in self.questions_data if str(q.get('_id')) == question_id), None)
                
                if question:
                    # Find the selected option and check if it's correct
                    options = question.get('options', [])
                    selected_option = next((opt for opt in options if opt.get('id') == selected_option_id), None)
                    if selected_option and selected_option.get('isCorrect'):
                        score += 1

            percentage = (score / total_questions) * 100 if total_questions > 0 else 0

            result_data = {
                "exam": exam_id,
                "student": student_id,
                "answers": answers,
                "score": score,
                "total": total_questions,
                "percentage": percentage,
                "submittedAt": datetime.now()
            }
            
            if self.using_mongodb:
                result = self.results.insert_one(result_data)
                return str(result.inserted_id), None
            else:
                result_data["_id"] = f"result_{len(self.results_data) + 1}"
                self.results_data.append(result_data)
                return result_data["_id"], None
                
        except Exception as e:
            return None, str(e)

    def get_student_results(self, student_id):
        try:
            if self.using_mongodb:
                results = self.results.find({"student": student_id})
                result_list = []
                for result in results:
                    exam = self.exams.find_one({"_id": ObjectId(result.get("exam", ""))})
                    result_data = {
                        "id": str(result.get("_id", "")),
                        "exam_title": exam.get("title", "Unknown Exam") if exam else "Unknown Exam",
                        "score": result.get("score", 0),
                        "total": result.get("total", 1),
                        "percentage": result.get("percentage", 0),
                        "submittedAt": result.get("submittedAt", datetime.now())
                    }
                    result_list.append(result_data)
                return result_list
            else:
                student_results = [r for r in self.results_data if r.get('student') == student_id]
                result_list = []
                for result in student_results:
                    exam = next((e for e in self.exams_data if e.get('_id') == result.get("exam")), None)
                    result_data = {
                        "id": result.get("_id", ""),
                        "exam_title": exam.get("title", "Unknown Exam") if exam else "Unknown Exam",
                        "score": result.get("score", 0),
                        "total": result.get("total", 1),
                        "percentage": result.get("percentage", 0),
                        "submittedAt": result.get("submittedAt", datetime.now())
                    }
                    result_list.append(result_data)
                return result_list
        except Exception as e:
            st.error(f"Error getting student results: {e}")
            return []

    def get_all_exams(self):
        try:
            if self.using_mongodb:
                exams = self.exams.find()
                exam_list = []
                for exam in exams:
                    teacher = self.get_user_by_id(exam.get("createdBy", ""))
                    exam_data = {
                        "id": str(exam.get("_id", "")),
                        "title": exam.get("title", ""),
                        "duration": exam.get("duration", 30),
                        "isPublished": exam.get("isPublished", False),
                        "teacher": teacher.get("name", "Unknown") if teacher else "Unknown",
                        "createdAt": exam.get("createdAt", datetime.now())
                    }
                    exam_list.append(exam_data)
                return exam_list
            else:
                exam_list = []
                for exam in self.exams_data:
                    exam_list.append({
                        "id": exam.get("_id", ""),
                        "title": exam.get("title", ""),
                        "duration": exam.get("duration", 30),
                        "isPublished": exam.get("isPublished", False),
                        "teacher": "Demo Teacher",
                        "createdAt": exam.get("createdAt", datetime.now())
                    })
                return exam_list
        except Exception as e:
            st.error(f"Error getting all exams: {e}")
            return []

    def get_all_results(self):
        try:
            if self.using_mongodb:
                results = self.results.find()
                result_list = []
                for result in results:
                    exam = self.exams.find_one({"_id": ObjectId(result.get("exam", ""))})
                    student = self.users.find_one({"_id": ObjectId(result.get("student", ""))})
                    result_data = {
                        "id": str(result.get("_id", "")),
                        "exam_title": exam.get("title", "Unknown") if exam else "Unknown",
                        "student_name": student.get("name", "Unknown") if student else "Unknown",
                        "score": result.get("score", 0),
                        "total": result.get("total", 1),
                        "percentage": result.get("percentage", 0),
                        "submittedAt": result.get("submittedAt", datetime.now())
                    }
                    result_list.append(result_data)
                return result_list
            else:
                result_list = []
                for result in self.results_data:
                    exam = next((e for e in self.exams_data if e.get('_id') == result.get("exam")), None)
                    student = next((u for u in self.users_data if u.get('_id') == result.get("student")), None)
                    result_data = {
                        "id": result.get("_id", ""),
                        "exam_title": exam.get("title", "Unknown") if exam else "Unknown",
                        "student_name": student.get("name", "Unknown") if student else "Unknown",
                        "score": result.get("score", 0),
                        "total": result.get("total", 1),
                        "percentage": result.get("percentage", 0),
                        "submittedAt": result.get("submittedAt", datetime.now())
                    }
                    result_list.append(result_data)
                return result_list
        except Exception as e:
            st.error(f"Error getting all results: {e}")
            return []

    def get_analytics(self):
        try:
            results = self.get_all_results()
            users = self.get_all_users()
            exams = self.get_all_exams()
            
            total_exams = len(exams)
            total_students = len([u for u in users if u.get('role') == 'student'])
            total_attempts = len(results)
            
            if results:
                avg_score = sum(r.get('percentage', 0) for r in results) / len(results) if results else 0
            else:
                avg_score = 0
            
            return {
                "total_exams": total_exams,
                "total_students": total_students,
                "average_score": avg_score,
                "total_attempts": total_attempts
            }
        except Exception as e:
            st.error(f"Error getting analytics: {e}")
            return {}
        
    # Add these methods to the Database class

    def delete_user(self, user_id):
        """Delete a user by ID"""
        try:
            if self.using_mongodb:
                # Check if user exists
                user = self.users.find_one({"_id": ObjectId(user_id)})
                if not user:
                    return False
                
                # Don't allow deletion if user has created exams
                exams_count = self.exams.count_documents({"createdBy": user_id})
                if exams_count > 0:
                    st.error(f"Cannot delete user. They have created {exams_count} exam(s).")
                    return False
                
                # Delete user
                result = self.users.delete_one({"_id": ObjectId(user_id)})
                return result.deleted_count > 0
            else:
                # In-memory database
                user_index = next((i for i, u in enumerate(self.users_data) if u.get('_id') == user_id), None)
                if user_index is not None:
                    user = self.users_data[user_index]
                    
                    # Check if user has created exams
                    exams_count = len([e for e in self.exams_data if e.get('createdBy') == user_id])
                    if exams_count > 0:
                        st.error(f"Cannot delete user. They have created {exams_count} exam(s).")
                        return False
                    
                    # Delete user
                    del self.users_data[user_index]
                    return True
                return False
        except Exception as e:
            st.error(f"Error deleting user: {e}")
            return False

    def delete_exam(self, exam_id):
        """Delete an exam by ID"""
        try:
            if self.using_mongodb:
                # Check if exam exists
                exam = self.exams.find_one({"_id": ObjectId(exam_id)})
                if not exam:
                    return False
                
                # Check if exam has results
                results_count = self.results.count_documents({"exam": exam_id})
                if results_count > 0:
                    st.error(f"Cannot delete exam. It has {results_count} result(s).")
                    return False
                
                # Delete exam
                result = self.exams.delete_one({"_id": ObjectId(exam_id)})
                return result.deleted_count > 0
            else:
                # In-memory database
                exam_index = next((i for i, e in enumerate(self.exams_data) if e.get('_id') == exam_id), None)
                if exam_index is not None:
                    exam = self.exams_data[exam_index]
                    
                    # Check if exam has results
                    results_count = len([r for r in self.results_data if r.get('exam') == exam_id])
                    if results_count > 0:
                        st.error(f"Cannot delete exam. It has {results_count} result(s).")
                        return False
                    
                    # Delete exam
                    del self.exams_data[exam_index]
                    return True
                return False
        except Exception as e:
            st.error(f"Error deleting exam: {e}")
            return False

    def unpublish_exam(self, exam_id, teacher_id):
        """Unpublish an exam"""
        try:
            if self.using_mongodb:
                result = self.exams.update_one(
                    {"_id": ObjectId(exam_id), "createdBy": teacher_id},
                    {"$set": {"isPublished": False}}
                )
                return result.modified_count > 0
            else:
                exam = next((e for e in self.exams_data if e.get('_id') == exam_id and e.get('createdBy') == teacher_id), None)
                if exam:
                    exam["isPublished"] = False
                    return True
                return False
        except Exception as e:
            st.error(f"Error unpublishing exam: {e}")
            return False