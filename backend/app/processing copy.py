import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, LabelEncoder
from io import StringIO
from processing import process_data

# Try importing UMAP (It might fail if not installed, so we handle it gracefully)
try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False

def process_data(contents: bytes, filename: str, method: str = "pca"):
    # 1. READ DATA
    # We assume the CSV has a header.
    df = pd.read_csv(StringIO(contents.decode('utf-8')))
    
    # 2. SEPARATE NUMBERS (Features) FROM TEXT (Metadata)
    # This is the "Janitor" phase.
    numeric_df = df.select_dtypes(include=[np.number])
    metadata_df = df.select_dtypes(exclude=[np.number])
    
    # Fill empty numbers with 0 (prevents crashes)
    features = numeric_df.fillna(0).values
    
    # 3. HANDLE LABELS (For Coloring)
    # If we find a text column, we'll use the first one as a label.
    labels = None
    label_column_name = "No Label"
    
    if not metadata_df.empty:
        # Pick the first text column as the "Category"
        label_column_name = metadata_df.columns[0]
        labels = metadata_df[label_column_name].astype(str).values
    else:
        # If no text, check if there's a numeric column that looks like an ID
        pass 

    # 4. DIMENSIONALITY REDUCTION (The Math)
    # We force the output to be 3 Dimensions (n_components=3)
    
    coords = None
    
    # -- OPTION A: PCA --
    if method == "pca":
        # Standardize first (Scale data so big numbers don't dominate)
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        pca = PCA(n_components=3)
        coords = pca.fit_transform(features_scaled)

    # -- OPTION B: UMAP --
    elif method == "umap":
        if not HAS_UMAP:
            return {"error": "UMAP is not installed on the server."}
            
        # UMAP doesn't always need scaling, but it's often safer
        reducer = umap.UMAP(n_components=3, random_state=42)
        coords = reducer.fit_transform(features)
        
    # -- OPTION C: t-SNE (Add this later if you want) --
    
    # 5. PACKAGING THE RESULT
    # We merge the new 3D coords back with the metadata
    result = []
    
    for i in range(len(coords)):
        point = {
            "x": float(coords[i][0]),
            "y": float(coords[i][1]),
            "z": float(coords[i][2]),
            # Add metadata for tooltips
            "label": labels[i] if labels is not None else f"Point {i}",
            "id": i
        }
        result.append(point)

    return {
        "filename": filename,
        "method": method,
        "points": result,
        "label_column": label_column_name
    }

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), method: str = "pca"):
    contents = await file.read()
    
    # Call the worker function
    try:
        result = process_data(contents, file.filename, method)
        return result
    except Exception as e:
        return {"error": str(e)}