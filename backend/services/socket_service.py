from socketio import Server
from typing import Dict, Any

class SocketService:
    def __init__(self, sio: Server):
        self.sio = sio
    
    def notify_progress(self, task_id: str, progress: int, message: str) -> None:
        self.sio.emit('task_update', {
            'task_id': task_id,
            'status': 'PROGRESS',
            'progress': progress,
            'message': message
        })
    
    def notify_success(self, task_id: str, result: Dict[str, Any]) -> None:
        self.sio.emit('task_update', {
            'task_id': task_id,
            'status': 'SUCCESS',
            'progress': 100,
            'result': result
        })
    
    def notify_failure(self, task_id: str, error_msg: str) -> None:
        self.sio.emit('task_update', {
            'task_id': task_id,
            'status': 'FAILURE',
            'message': error_msg
        })