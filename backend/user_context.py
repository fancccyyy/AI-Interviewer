# user_context.py

from datetime import datetime
import uuid


class QARecord:
    """Single QA record, default status is 'pending'"""
    def __init__(self, question, answer=None, status="pending", timestamp=None, qa_id=None):
        self.question = question
        self.answer = answer
        self.status = status
        self.timestamp = timestamp or datetime.now().isoformat()
        self.qa_id = qa_id or f"q_{uuid.uuid4().hex}"

    def to_dict(self):
        return {
            "question": self.question,
            "answer": self.answer,
            "status": self.status,
            "timestamp": self.timestamp,
            "qa_id": self.qa_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            question=data["question"],
            answer=data.get("answer"),
            status=data.get("status", "pending"),
            timestamp=data.get("timestamp"),
            qa_id=data.get("qa_id")
        )


class UserContextManager:
    def __init__(self):
        self._store = {}  # { uid: { 'qa_list': [QARecord], 'progress': UserProgress } }

    def get_user_data(self, uid):
        return self._store.get(uid)

    def get_user_qa(self, uid):
        user_data = self.get_user_data(uid)
        return user_data['qa_list'] if user_data else []

    def get_user_progress(self, uid):
        user_data = self.get_user_data(uid)
        return user_data['progress'] if user_data else None

    def get_user_current_question(self, uid):
        progress = self.get_user_progress(uid)
        # print(progress)
        if progress is None:
            return None
        for qa in self.get_user_qa(uid):
            if qa.qa_id == progress.current_qa_id:
                return qa

    def init_new_user(self, uid):
        if uid not in self._store:
            self._store[uid] = {
                'qa_list': [],
                'progress': UserProgress()
            }
        # else:
        #     print(self._store.keys())
        #     raise ValueError('New user already created!')

    def start_new_question(self, uid, question, question_type):
        if question_type not in ['given', 'probe']:
            raise ValueError('Invalid question type!')

        # 1. Initialize user data if not exists
        if uid not in self._store:
            self._store[uid] = {
                'qa_list': [],
                'progress': UserProgress()
            }

        # 2. Create a new QARecord and update user data
        user_data = self._store[uid]
        progress = user_data['progress']
        qa_record = QARecord(question=question)

        user_data['qa_list'].append(qa_record)
        progress.in_progress = True
        progress.current_qa_id = qa_record.qa_id
        progress.current_status = "pending"
        progress.current_question_type = question_type
        progress.last_updated = datetime.now().isoformat()

        return qa_record.qa_id

    def update_answer(self, uid, answer_text):
        user_data = self._store.get(uid)
        if not user_data:
            return False

        progress = user_data['progress']
        current_qa_id = progress.current_qa_id

        for record in user_data['qa_list']:
            if record.qa_id == current_qa_id:
                record.answer = answer_text
                record.end_time = datetime.now().isoformat()
                record.status = "answered"

                progress.current_status = "answered"
                if progress.current_question_type == "given":
                    progress.total_questions["given"] += 1
                elif progress.current_question_type == "probe":
                    progress.total_questions["probe"] += 1
                else:
                    raise ValueError(f"Unknown question type: {progress.current_question_type}")
                progress.in_progress = False
                progress.last_updated = datetime.now().isoformat()
                return True

        return False

    def mark_timeout(self, uid):
        """标记当前问题超时未答"""
        user_data = self._store.get(uid)
        if not user_data:
            return False

        progress = user_data['progress']
        current_qa_id = progress.current_qa_id

        for record in user_data['qa_list']:
            if record.qa_id == current_qa_id:
                record.status = "timeout"
                record.end_time = datetime.now().isoformat()

                progress.current_status = "timeout"
                progress.in_progress = False
                progress.last_updated = datetime.now().isoformat()
                return True

        return False

    def is_in_progress(self, uid):
        """检查用户是否正在答题"""
        user_data = self._store.get(uid)
        if not user_data:
            return False
        return user_data['progress'].in_progress

    def is_interview_done(self, uid):
        """检查用户是否面试完成"""
        user_data = self._store.get(uid)
        if not user_data:
            return False
        return user_data['progress'].interview_done

    def set_interview_done(self, uid):
        """设置用户面试完成"""
        user_data = self._store.get(uid)
        if user_data:
            user_data['progress'].interview_done = True
        else:
            raise ValueError(f"User {uid} not found")

    def clear_user_data(self, uid):
        """清除某个用户的所有数据"""
        if uid in self._store:
            del self._store[uid]

class UserProgress:
    def __init__(self):
        self.in_progress = False     # 是否正在答题
        self.interview_done = False
        self.total_questions = {
            "given": 0,
            "probe": 0
        }     # 完成的总题数
        self.current_question_type = None     # 当前问题类型(given/probe)
        self.current_qa_id = None    # 当前问题 ID
        self.current_status = None   # 当前问题状态（pending/answered/timeout）
        self.last_updated = datetime.now().isoformat()

    def to_dict(self):
        return {
            "in_progress": self.in_progress,
            "interview_done": self.interview_done,
            "total_questions": self.total_questions,
            "current_qa_id": self.current_qa_id,
            "current_status": self.current_status,
            "last_updated": self.last_updated
        }

    @classmethod
    def from_dict(cls, data):
        progress = cls()
        progress.in_progress = data.get("in_progress", False)
        progress.interview_done = data.get("interview_done", False)
        progress.total_questions = data.get("total_questions", {"given": 0, "probe": 0})
        progress.current_qa_id = data.get("current_qa_id")
        progress.current_status = data.get("current_status")
        progress.last_updated = data.get("last_updated")
        return progress