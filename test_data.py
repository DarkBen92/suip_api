import pytz

from datetime import datetime, timedelta
from typing import List, Dict


TEST_FILES = [
    {
        "id": 1,
        "filename": "document_2024.pdf",
        "filetype": ".pdf",
        "created_at": datetime.now(pytz.utc) - timedelta(days=1)
    },
    {
        "id": 2,
        "filename": "image_001.jpg",
        "filetype": ".jpeg",
        "created_at": datetime.now(pytz.utc) - timedelta(hours=12)
    },
    {
        "id": 3,
        "filename": "report_2024.mp3",
        "filetype": ".mp3",
        "created_at": datetime.now(pytz.utc) - timedelta(hours=6)
    },
    {
        "id": 4,
        "filename": "presentation.tar",
        "filetype": ".tar",
        "created_at": datetime.now(pytz.utc) - timedelta(hours=3)
    },
    {
        "id": 5,
        "filename": "archive.torrent",
        "filetype": ".torrent",
        "created_at": datetime.now(pytz.utc) - timedelta(hours=1)
    }
]


class TestDataManager:
    data: List[Dict] = []
    
    @classmethod
    def initialize(cls):
        """Инициализация тестовых данных."""
        cls.data = TEST_FILES.copy()
    
    @classmethod
    def get_all(cls) -> List[Dict]:
        """Получить все данные."""
        return cls.data
    
    @classmethod
    def add(cls, item: Dict):
        """Добавить новую запись."""
        item["id"] = len(cls.data) + 1
        item["created_at"] = datetime.now(pytz.utc)
        cls.data.append(item)
