from fastapi import FastAPI

from app.api import router as api_router


app = FastAPI()
app.include_router(api_router)

@app.get("/", tags=["INDEX"])
async def index():
    return {"message": "Welcom! Api docs here -> "}



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
