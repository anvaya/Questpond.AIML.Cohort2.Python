"""
Database operations for Jobs table
"""
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any
from Shared.db import connect_db
import jsonpickle

class JobRepository:
    def __init__(self):
        # Don't store connection - create new one for each operation
        pass

    def _get_connection(self):
        """Create a new connection for each operation to avoid threading issues"""
        return connect_db()

    def create_job(
        self,
        job_type: str,
        input_data: Dict[str, Any]
    ) -> str:
        """Create a new job record"""
        job_id = str(uuid.uuid4())
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO Jobs (JobID, JobType, Status, Progress, Message, InputData, CreatedAt, UpdatedAt)
                VALUES (?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
            """, (
                job_id,
                job_type,
                'queued',
                0,
                'Job queued',
                json.dumps(input_data)
            ))

            conn.commit()
            return job_id
        finally:
            conn.close()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT JobID, JobType, Status, Progress, Message, Result,
                       CreatedAt, CompletedAt, ErrorMessage
                FROM Jobs WHERE JobID = ?
            """, (job_id,))

            row = cursor.fetchone()

            if row:
                result = {
                    'id': str(row.JobID),
                    'type': row.JobType,
                    'status': row.Status,
                    'progress': row.Progress,
                    'message': row.Message,
                    'result': json.loads(row.Result) if row.Result else None,
                    'created_at': row.CreatedAt,
                    'error_message': row.ErrorMessage
                }
                return result

            return None
        finally:
            conn.close()

    
    def json_serializer(self, obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


    def update_job_status(
        self,
        job_id: str,
        status: str,
        progress: int,
        message: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update job status and progress"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            result_json = json.dumps(result, default=self.json_serializer) if result else None

            if status == 'completed':
                cursor.execute("""
                    UPDATE Jobs
                    SET Status = ?, Progress = ?, Message = ?, Result = ?,
                        UpdatedAt = GETDATE(), CompletedAt = GETDATE()
                    WHERE JobID = ?
                """, (status, progress, message, result_json, job_id))
            elif status == 'failed':
                cursor.execute("""
                    UPDATE Jobs
                    SET Status = ?, Progress = ?, Message = ?, ErrorMessage = ?,
                        UpdatedAt = GETDATE(), CompletedAt = GETDATE()
                    WHERE JobID = ?
                """, (status, progress, message, error_message, job_id))
            else:
                cursor.execute("""
                    UPDATE Jobs
                    SET Status = ?, Progress = ?, Message = ?, Result = ?, UpdatedAt = GETDATE()
                    WHERE JobID = ?
                """, (status, progress, message, result_json, job_id))

            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_job_input(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job input data"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT InputData FROM Jobs WHERE JobID = ?", (job_id,))
            row = cursor.fetchone()

            if row and row.InputData:
                return json.loads(row.InputData)

            return None
        finally:
            conn.close()
