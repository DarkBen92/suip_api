import json

from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


def save_to_json(data: Dict) -> str:
    """Сохранение данных в JSON-файл.

    :param data: Данные для сохранения

    :return: Путь к сохраненному файлу
    """
    save_dir = Path("saved_metadata")
    save_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"metadata_{timestamp}.json"
    filepath = save_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return str(filepath)


def filter_by_filetype(data: List[Dict], filetype: str) -> List[Dict]:
    """Фильтрация по типу файла.

    :param data: Список данных
    :param filetype: Тип файла

    :return: Список данных, отфильтрованных по типу файла
    """
    if not filetype:
        return data

    return [item for item in data if filetype.lower() in item["filetype"].lower()]


def check_file(data: List[Dict], new_file: Dict) -> Optional[Dict]:
    """Проверка на существование похожего файла.

    :param data: Список существующих файлов
    :param new_file: Новый файл для проверки

    :return: Схожий файл или None
    """
    for file in data:
        if file["filetype"] == new_file["filetype"]:

            existing_name = file["filename"].rsplit(".", 1)[0]
            new_name = new_file["filename"].rsplit(".", 1)[0]

            if existing_name == new_name:
                return file
    return None
