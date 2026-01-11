from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

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
    return {"message": "EmbeddingLab API is running"}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    
    
    return {
        "filename": file.filename,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "message": "File received. Ready for dimensionality reduction."
    }

# To run: uvicorn app.main:app --reload