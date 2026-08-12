import mysql.connector
from config import Config
import datetime

class Task:
    def __init__(self, id, title, created_at, description, closed_at=None, status='creada'):
        self.id = id
        self.title = title
        self.created_at = created_at
        self.description = description
        self.closed_at = closed_at
        self.status = status

    @staticmethod
    def connect():
        return mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT,
            database=Config.MYSQL_DB,
            ssl_ca=Config.MYSQL_SSL_CA
        )

    def save(self):
        db = self.connect()
        cursor = db.cursor()
        if not self.id:
            cursor.execute("SELECT COUNT(*) FROM tasks")
            count = cursor.fetchone()[0] + 1
            self.id = f"TSK-{str(count).zfill(4)}"
            query = "INSERT INTO tasks (id, title, description, status) VALUES (%s, %s, %s, %s)"
            values = (self.id, self.title, self.description, self.status)
        else:
            query = "UPDATE tasks SET title=%s, description=%s, status=%s, closed_at=%s WHERE id=%s"
            values = (self.title, self.description, self.status, self.closed_at, self.id)
        cursor.execute(query, values)
        db.commit()
        cursor.close()
        db.close()
        return self.id

    @staticmethod
    def get_all():
        db = Task.connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = [Task(*row) for row in cursor.fetchall()]
        cursor.close()
        db.close()
        return tasks

    @staticmethod
    def get_by_id(task_id):
        db = Task.connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
        row = cursor.fetchone()
        cursor.close()
        db.close()
        return Task(*row) if row else None

    def append_description(self, new_desc):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.description = f"{self.description}\n--- {timestamp} ---\n{new_desc}" if self.description else new_desc