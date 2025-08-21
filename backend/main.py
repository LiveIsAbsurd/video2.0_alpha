import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Путь к файлам в контейнере (совпадает с nginx)
FILES_DIR = "/usr/share/nginx/files"

@app.get("/api/getFiles")  # Изменил путь для лучшей практики
def list_files():
    try:
        # Проверяем существование директории
        if not os.path.exists(FILES_DIR):
            os.makedirs(FILES_DIR, exist_ok=True)
            return JSONResponse({"message": "Files directory created", "files": []})

        files = os.listdir(FILES_DIR)
        file_list = [
            {
                "name": file,
                "url": f"/files/{file}",  # Путь через nginx
                "size": os.path.getsize(os.path.join(FILES_DIR, file)),
            }
            for file in files
            if os.path.isfile(os.path.join(FILES_DIR, file))
        ]
        return JSONResponse({"files": file_list})
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)  # Стандартный порт для FastAPI