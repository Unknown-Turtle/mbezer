# mbezer
An application for the visualisation of embeddings into 3-d space for debugging and insights. It uses combines a **React** frontend with a **FastAPI** backend and uses a custom **C++** extension for accelerated vector search operations.


## How to use

Open two terminal windows to run the frontend and backend simultaneously.

### Terminal 1 - Backend

Navigate to the backend folder, set up the environment, and compile the C++ module.

```
cd backend

# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install requirements.txt

# 3. Compile the C++ Accelerator
# This builds the 'mbezer_cpp' module for high-performance math
cd app
python setup.py build_ext --inplace
cd ..

# 4. Start the Server
uvicorn app.main:app --reload\
```

### Terminal 2 - Frontend


```
cd frontend

# 1. Install Node modules
npm install

# 2. Start the Development Server
npm run dev
```
