from fastapi import FastAPI, HTTPException, status, UploadFile, File, Request
from fastapi.exceptions import RequestValidationError
from typing import Optional, List, Dict
from pydantic import BaseModel

from database_psycopg2 import save_metadata, get_all_metadata
from helper import filter_by_filetype, check_file, save_to_json
from parse_data import parse_suip_data

app = FastAPI(title="SUIP API")


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

    :param filetype: Необязательный фильтр, поиск по типу файла

    :return: Список данных о файлах
    """
    try:
        data = get_all_metadata()
        
        if not filetype:
            return data
            
        filtered_data = filter_by_filetype(data=data, filetype=filetype)
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
async def parse_and_save(uploaded_file: UploadFile = File(...)) -> Dict[str, str]:
    """Ручка POST для парсинга и сохранения данных о файлах.
    
    :param uploaded_file: Файл, который загружен для парсинга

    :return: Сохраненные данные о файле и путь к файлу с метаданными
    """
    try:
        result_parsing = await parse_suip_data(uploaded_file)
        data = get_all_metadata()
        conflict_file = check_file(data=data, new_file=result_parsing)

        if conflict_file:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": f"Обнаружен схожий файл {conflict_file['filename']}"}
            )
        
        save_metadata(result_parsing)
    
        existing_data = get_all_metadata()
        new_id = max([item.get('id', 0) for item in existing_data], default=0) + 1
        result_parsing['id'] = new_id
        
        saved_file_path = save_to_json(result_parsing)
        response_data = result_parsing.copy()
        response_data["saved_file_path"] = saved_file_path

        return response_data
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении данных: {str(e)}"
        )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации запроса."""
    if any(error["loc"][-1] == "uploaded_file" and error["type"] == "missing" for error in exc.errors()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отсутствует передача файла для парсинга. Обязательный параметр uploaded_file"
        )
    raise exc

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
