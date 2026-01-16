from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware

from app.processing import process_data

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "mbezer API is running"}

@app.post("/upload")
async def upload_csv(
    file: UploadFile = File(...), 
    method: str = Query("pca") # Explicitly define as Query parameter
):
    try:
        contents = await file.read()
        result = process_data(contents, file.filename, method)
        return result
    except Exception as e:
        print(f"Error during processing: {e}")
        return {"error": str(e)}

# unicorn app.main:app --reload