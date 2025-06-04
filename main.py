from fastapi import FastAPI, HTTPException, status, UploadFile, File
from typing import Optional, List, Dict
from pydantic import BaseModel
from helper import filter_by_filetype, check_file, save_to_json
from parse_data import parse_suip_data
from test_data import TestDataManager

app = FastAPI(title="SUIP API")

TestDataManager.initialize()


class SuipDataResponse(BaseModel):
    id: int
    filename: Optional[str] = None
    catalog: Optional[str] = None
    size_file: Optional[str] = None 
    date_edited_file: Optional[str] = None
    date_access_file: Optional[str] = None
    date_update_index_file: Optional[str] = None
    resolution_file: Optional[str] = None
    filetype: Optional[str] = None
    extension_file: Optional[str] = None
    mime_type: Optional[str] = None
    version_file: Optional[str] = None
    page_count: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    date_digitization: Optional[str] = None


@app.get("/suip-data", response_model=List[SuipDataResponse])
async def get_suip_data(filetype: Optional[str] = None) -> List[Dict]:
    """Ручка GET для получения данных о файлах.

    :param filetype: Необязательный фильтр по типу файла

    :return: Список данных о файлах
    """
    try:
        existing_data = TestDataManager.get_all()

        if not filetype:
            return existing_data
            
        filtered_data = filter_by_filetype(data=existing_data, filetype=filetype)
        if not filtered_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тип файла '{filetype}' не найден"
            )
        return filtered_data
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@app.post("/suip-data/parse", response_model=SuipDataResponse)
async def parse_and_save(file_path: UploadFile = File(...)) -> Dict[str, str]:
    """Ручка POST для парсинга и сохранения данных о файлах.
    
    :param file_path: ID файла

    :return: Сохраненные данные о файле и путь к файлу с метаданными
    """
    try:
        result_parsing = await parse_suip_data(file_path)
        existing_data = TestDataManager.get_all()
        conflict_file = check_file(data=existing_data, new_file=result_parsing)

        if conflict_file:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": f"Обнаружен схожий файл {conflict_file['filename']}"}
            )
        
        saved_file_path = save_to_json(result_parsing)
        response_data = result_parsing.copy()
        response_data["saved_file_path"] = saved_file_path
        
        TestDataManager.add(result_parsing)
        return response_data and result_parsing
        
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
