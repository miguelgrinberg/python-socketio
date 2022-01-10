import uvicorn

if __name__ == "__main__":
    uvicorn.run('core.asgi:application', reload=True)