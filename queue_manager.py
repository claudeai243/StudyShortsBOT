import asyncio
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import OrderedDict
import time


@dataclass
class QueueItem:
    user_id: int
    task_text: str
    message_id: int
    chat_id: int
    added_at: float = field(default_factory=time.time)
    is_processing: bool = False


class QueueManager:
    def __init__(self):
        self._queue: OrderedDict[int, QueueItem] = OrderedDict()
        self._current_processing: Optional[int] = None
        self._lock = asyncio.Lock()
        self._position_update_tasks: Dict[int, asyncio.Task] = {}
        self._processing_event = asyncio.Event()
        self._processing_event.set()
    
    async def add_to_queue(self, item: QueueItem) -> int:
        
        async with self._lock:
            self._queue[item.user_id] = item
            position = list(self._queue.keys()).index(item.user_id) + 1
            return position
    
    async def remove_from_queue(self, user_id: int):
        
        async with self._lock:
            if user_id in self._queue:
                del self._queue[user_id]
            if user_id in self._position_update_tasks:
                self._position_update_tasks[user_id].cancel()
                del self._position_update_tasks[user_id]
    
    async def get_position(self, user_id: int) -> int:
        
        async with self._lock:
            if user_id not in self._queue:
                return 0
            return list(self._queue.keys()).index(user_id) + 1
    
    async def get_queue_length(self) -> int:
        
        async with self._lock:
            return len(self._queue)
    
    async def is_first_in_queue(self, user_id: int) -> bool:
        
        async with self._lock:
            if not self._queue:
                return False
            first_user = next(iter(self._queue.keys()))
            return first_user == user_id
    
    async def is_user_in_queue(self, user_id: int) -> bool:
        
        async with self._lock:
            return user_id in self._queue
    
    async def get_item(self, user_id: int) -> Optional[QueueItem]:
        
        async with self._lock:
            return self._queue.get(user_id)
    
    async def set_processing(self, user_id: int, is_processing: bool):
        
        async with self._lock:
            if user_id in self._queue:
                self._queue[user_id].is_processing = is_processing
            if is_processing:
                self._current_processing = user_id
                self._processing_event.clear()
            else:
                self._current_processing = None
                self._processing_event.set()
    
    async def is_processing(self) -> bool:
        
        async with self._lock:
            return self._current_processing is not None
    
    async def wait_for_turn(self, user_id: int) -> bool:
        
        while True:
            if await self.is_first_in_queue(user_id) and not await self.is_processing():
                return True
            if not await self.is_user_in_queue(user_id):
                return False
            await asyncio.sleep(0.5)
    
    def add_update_task(self, user_id: int, task: asyncio.Task):
        
        self._position_update_tasks[user_id] = task
    
    def cancel_update_task(self, user_id: int):
        
        if user_id in self._position_update_tasks:
            self._position_update_tasks[user_id].cancel()
            del self._position_update_tasks[user_id]
queue_manager = QueueManager()
