import random

from fastapi import FastAPI, HTTPException, status
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel

from test_data import TestDataManager

app = FastAPI(title="SUIP API")

TestDataManager.initialize()


class SuipDataResponse(BaseModel):
    id: int
    filename: str
    filetype: str
    created_at: datetime


async def parse_suip_data():
    """Имитация парсера данных файлов."""
    return {
        "filename": f"parsed_file_{random.randint(1, 15)}.txt",
        "filetype": ".txt"
    }


def filter_by_filetype(data: List[Dict], filetype: str) -> List[Dict]:
    """Фильтрация по типу файла.
    
    :param data: Список данных
    :param filetype: Тип файла

    :return: Список данных, отфильтрованных по типу файла
    """
    if not filetype:
        return data
    
    filtered_data = [item for item in data if filetype.lower() in item["filetype"].lower()]
    
    if not filtered_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тип файла '{filetype}' не найден"
        )
    
    return filtered_data


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


@app.get("/suip-data", response_model=List[SuipDataResponse])
async def get_suip_data(filetype: Optional[str] = None) -> List[Dict]:
    """Ручка GET для получения данных о файлах.

    :param filetype: Необязательный фильтр по типу файла

    :return: Список данных о файлах
    """
    try:
        existing_data = TestDataManager.get_all()
        return filter_by_filetype(data=existing_data, filetype=filetype) if filetype else existing_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@app.post("/suip-data/parse", response_model=SuipDataResponse)
async def parse_and_save() -> Dict[str, str]:
    """Ручка POST для парсинга и сохранения данных о файлах.
    
    :return: Сохраненные данные о файле
    """
    try:
        new_file = await parse_suip_data()
        existing_data = TestDataManager.get_all()
        file = check_file(data=existing_data, new_file=new_file)

        if file:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": f"Обнаружен схожий файл {file['filename']}"}
            )
        
        TestDataManager.add(new_file)
        return new_file
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении данных: {str(e)}"
        )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
