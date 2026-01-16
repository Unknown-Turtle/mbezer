import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.manifold import TSNE
from io import StringIO

# Handle UMAP separately as it's an external library
try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False

def process_data(contents: bytes, filename: str, method: str = "pca", n_neighbors: int = 5, n_clusters: int = 5):
    # 1. READ DATA
    # Decodes the bytes from the upload and loads into a Pandas DataFrame
    df = pd.read_csv(StringIO(contents.decode('utf-8')))
    
    # 2. DATA CLEANING & SEPARATION
    # We only want numbers for the math, and text for the labels
    numeric_df = df.select_dtypes(include=[np.number])
    metadata_df = df.select_dtypes(exclude=[np.number])
    
    # If the file has no numbers at all, we can't process it
    if numeric_df.empty:
        raise ValueError("The CSV must contain at least some numeric columns.")
        
    # Fill missing values with 0 so the algorithms don't crash
    features = numeric_df.fillna(0).values
    
    # Pick the first text column found as the 'Label' for tooltips
    labels = None
    label_column_name = "No Label Column Found"
    if not metadata_df.empty:
        label_column_name = metadata_df.columns[0]
        labels = metadata_df[label_column_name].astype(str).values
    
    # 3. SCALING
    # Algorithms like PCA and K-Means are sensitive to the scale of numbers
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # 4. SAFETY CHECK: DIMENSIONALITY LIMITS
    # We want 3D, but math requires: n_components <= min(rows, columns)
    n_samples, n_features = features_scaled.shape
    target_dims = 3
    actual_dims = min(target_dims, n_samples, n_features)

    # 5. DIMENSIONALITY REDUCTION (The Map)
    coords = None
    
    if method == "pca":
        pca = PCA(n_components=actual_dims)
        coords = pca.fit_transform(features_scaled)

    elif method == "tsne":
        # Standard practice: PCA down to 50 dims first to remove noise for t-SNE
        pca_pre = PCA(n_components=min(50, n_samples, n_features))
        reduced_feats = pca_pre.fit_transform(features_scaled)
        
        # t-SNE initialization
        tsne = TSNE(
            n_components=actual_dims, 
            random_state=42, 
            init='pca', 
            learning_rate='auto',
            perplexity=min(30, n_samples - 1) # Perplexity must be less than n_samples
        )
        coords = tsne.fit_transform(reduced_feats)

    elif method == "umap":
        if not HAS_UMAP:
            raise ImportError("UMAP library is not installed on the server.")
        
        # UMAP SAFETY CHECK
        # UMAP fails on tiny datasets (< 5 points) because it can't build a graph.
        # If n_samples < 5, we silently fallback to PCA so the app doesn't crash.
        if n_samples < 5:
            pca_fallback = PCA(n_components=actual_dims)
            coords = pca_fallback.fit_transform(features_scaled)
        else:
            # Dynamic n_neighbors: 
            # Default is 15, but we can't look for 15 neighbors if we only have 10 points.
            # We set it to n_samples - 1 (max possible neighbors) or 15, whichever is smaller.
            safe_neighbors = min(15, n_samples - 1)
            
            reducer = umap.UMAP(
                n_components=actual_dims, 
                n_neighbors=safe_neighbors, 
                random_state=42
            )
            coords = reducer.fit_transform(features_scaled)

    # RECOVERY: If the file was too small for 3D, pad the rest with Zeros
    # This ensures the Frontend always gets an [x, y, z] structure
    if coords.shape[1] < 3:
        padding = np.zeros((coords.shape[0], 3 - coords.shape[1]))
        coords = np.hstack((coords, padding))

    # 6. AUTO-CLUSTERING (K-Means)
    # Even if labels aren't provided, we "discover" groups
    # Safety: can't have more clusters than samples
    clusters_to_find = min(n_clusters, n_samples)
    kmeans = KMeans(n_clusters=clusters_to_find, random_state=42, n_init=10)
    cluster_ids = kmeans.fit_predict(features_scaled)

    # 7. NEAREST NEIGHBORS (Vector Search)
    # Find the 'n' most similar points for every point
    neighbors_to_find = min(n_neighbors + 1, n_samples)
    nn = NearestNeighbors(n_neighbors=neighbors_to_find, metric='euclidean')
    nn.fit(features_scaled)
    _, indices = nn.kneighbors(features_scaled)

    # 8. PACKAGING FOR FRONTEND
    result_points = []
    for i in range(len(coords)):
        # Extract neighbor IDs (skipping the first one as it is the point itself)
        point_neighbors = indices[i][1:].tolist()
        
        result_points.append({
            "id": i,
            "x": float(coords[i][0]),
            "y": float(coords[i][1]),
            "z": float(coords[i][2]),
            "label": labels[i] if labels is not None else f"Point {i}",
            "cluster": int(cluster_ids[i]),
            "neighbors": point_neighbors
        })

    return {
        "filename": filename,
        "method": method,
        "points": result_points,
        "label_column": label_column_name,
        "total_clusters": clusters_to_find
    }