import uvicorn
from src.configs.settings import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "src.api.index:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,  # Auto-reload en desarrollo
        log_level="info"
    )