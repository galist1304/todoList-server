from fastapi import FastAPI, HTTPException
from routes import tasks, users
from pymongo import MongoClient
from database import db
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with the actual origins you want to allow
    allow_methods=["GET", "POST", "PATCH","PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
    expose_headers=["Content-Disposition"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def check_db_health():
    try:
        # Try to ping the database to check the connection status
        db.command("ping")
        return {"status": "Database is connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

app.include_router(tasks.router)
app.include_router(users.router)
