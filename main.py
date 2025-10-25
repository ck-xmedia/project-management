from fastapi import FastAPI

# Create FastAPI instance
app = FastAPI(title="Project Management API", version="1.0.0")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "🚀 FastAPI is running successfully!"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Example endpoint
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name} 👋"}
