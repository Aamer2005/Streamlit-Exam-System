import pymongo
from bson import ObjectId
import bcrypt
from datetime import datetime
import streamlit as st

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
                    questions = self.questions.find({"_id": {"$in": exam.get("questions", [])}})
                    exam_data = {
                        "id": str(exam.get("_id", "")),
                        "title": exam.get("title", ""),
                        "duration": exam.get("duration", 30),
                        "questions": list(questions),
                        "isPublished": exam.get("isPublished", False),
                        "createdAt": exam.get("createdAt", datetime.now())
                    }
                    exam_list.append(exam_data)
                return exam_list
            else:
                teacher_exams = [e for e in self.exams_data if e.get('createdBy') == teacher_id]
                for exam in teacher_exams:
                    exam["id"] = exam.get("_id", "")
                return teacher_exams
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
                exam = next((e for e in self.exams_data if e.get('_id') == exam_id), None)
                if exam:
                    exam["isPublished"] = True
                    return True
                return False
        except:
            return False

    def get_published_exams(self):
        try:
            if self.using_mongodb:
                exams = self.exams.find({"isPublished": True})
                exam_list = []
                for exam in exams:
                    teacher = self.users.find_one({"_id": ObjectId(exam.get("createdBy", ""))})
                    questions = self.questions.find({"_id": {"$in": exam.get("questions", [])}})
                    exam_data = {
                        "id": str(exam.get("_id", "")),
                        "title": exam.get("title", ""),
                        "duration": exam.get("duration", 30),
                        "questions": list(questions),
                        "teacher": teacher.get("name", "Unknown") if teacher else "Unknown"
                    }
                    exam_list.append(exam_data)
                return exam_list
            else:
                published_exams = [e for e in self.exams_data if e.get('isPublished')]
                for exam in published_exams:
                    exam["id"] = exam.get("_id", "")
                    exam["teacher"] = "Demo Teacher"
                return published_exams
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

            # Simple scoring - for demo, give random score
            import random
            score = random.randint(5, len(answers))
            total = len(answers)

            result_data = {
                "exam": exam_id,
                "student": student_id,
                "answers": answers,
                "score": score,
                "total": total,
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
                        "percentage": (result.get("score", 0) / result.get("total", 1)) * 100,
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
                        "percentage": (result.get("score", 0) / result.get("total", 1)) * 100,
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
                    teacher = self.users.find_one({"_id": ObjectId(exam.get("createdBy", ""))})
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
                        "percentage": (result.get("score", 0) / result.get("total", 1)) * 100,
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
                        "percentage": (result.get("score", 0) / result.get("total", 1)) * 100,
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
            if results:
                total_exams = len(set(r.get('exam_title', '') for r in results))
                total_students = len(set(r.get('student_name', '') for r in results))
                avg_score = sum(r.get('percentage', 0) for r in results) / len(results) if results else 0
                
                return {
                    "total_exams": total_exams,
                    "total_students": total_students,
                    "average_score": avg_score,
                    "total_attempts": len(results)
                }
            return {}
        except Exception as e:
            st.error(f"Error getting analytics: {e}")
            return {}