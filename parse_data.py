import aiohttp
from fastapi import HTTPException, status, UploadFile
from bs4 import BeautifulSoup
from typing import Dict, Union
import os
import tempfile
import shutil
import ssl

SUIP_URL = "https://suip.biz/ru/?act=mat"


async def post_data_file_with_suip(file_path: str) -> str:
    """Отправка файла на сервер SUIP.

    :param file_path: Путь к файлу для отправки

    :return: Ответ сервера в виде текста
    """
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            file_name = os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('fileforsending', f, filename=file_name, content_type='application/pdf')
                
                async with session.post(SUIP_URL, data=data) as response:
                    return await response.text()
                    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке файла: {str(e)}"
        )
       

def parse_metadata(metadata_text: str) -> Dict[str, str]:
    """Извлекает метаданные из текста ответа."""
    metadata = {}
    for line in metadata_text.splitlines():
        if ":" not in line:
            continue
            
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.strip("-").strip()
        
        if key and value:
            metadata[key] = value
    
    if not metadata:
        raise ValueError("Не удалось извлечь метаданные файла")
    
    return metadata


async def parse_suip_data(file_input: Union[str, UploadFile]) -> Dict:
    """Парсер метаданных файла.

    :param file_input: загрузка файла для парсинга
    
    :return: Словарь с метаданными файла
    """
    temp_file_path = None
    original_filename = None
    try:
        if isinstance(file_input, str):
            file_path = file_input
            original_filename = os.path.basename(file_input)
        else:
            original_filename = file_input.filename
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_input.filename)[1])
            temp_file_path = temp_file.name
            temp_file.close()
            
            with open(temp_file_path, 'wb') as buffer:
                shutil.copyfileobj(file_input.file, buffer)
            
            file_path = temp_file_path

        html = await post_data_file_with_suip(file_path)
        if not html:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Получен пустой ответ от сервера"
            )
        
        soup = BeautifulSoup(html, 'html.parser')
        metadata_text = soup.find('pre')
        if not metadata_text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Метаданные файла не найдены"
            )
        
        metadata = parse_metadata(metadata_text.text)

        return {
            "filename": original_filename or metadata.get("Название файла", ""),
            "catalog": metadata.get("Каталог", ""),
            "size_file": metadata.get("Размер файла", ""),
            "date_edited_file": metadata.get("Дата редактирования файла", ""),
            "date_access_file": metadata.get("Дата последнего доступа к файлу", ""),
            "date_update_index_file": metadata.get("Дата изменения файлового индекса", ""),
            "resolution_file": metadata.get("Разрешения файла", ""),
            "extension_file": metadata.get("Тип файла", ""),
            "filetype": metadata.get("Расширение файла", "").lower(),
            "mime_type": metadata.get("MIME тип", ""),
            "version_file": metadata.get("Версия PDF", ""),
            "page_count": metadata.get("Количество страниц", ""),
            "creator": metadata.get("Создатель", ""),
            "producer": metadata.get("Производитель", ""),
            "date_digitization": metadata.get("Дата оцифровки", ""),
        }
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при парсинге данных: {str(e)}"
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
