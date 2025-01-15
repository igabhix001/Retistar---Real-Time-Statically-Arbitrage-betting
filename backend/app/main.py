from fastapi import FastAPI
from app.auth.routes import auth_router
from app.db import db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth_router, prefix="/auth")

@app.get("/")
async def root():
    return {"message": "Welcome to the Auth API"}

# List all routes
if __name__ == "__main__":
    import uvicorn
    for route in app.routes:
        print(f"Path: {route.path}, Name: {route.name}, Methods: {route.methods}")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace '*' with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
