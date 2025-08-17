from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from config import settings
from database import create_tables
from api.websocket import websocket_endpoint, manager
from orchestra import OrchestraManager


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(settings.log_file)],
)

logger = logging.getLogger(__name__)

# Global Orchestra manager instance
orchestra_manager: OrchestraManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    global orchestra_manager

    # Startup
    logger.info("Starting Con-AI Backend")

    # Create database tables
    try:
        create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    # Initialize Orchestra manager
    try:
        orchestra_manager = OrchestraManager(manager)
        await orchestra_manager.initialize()

        # Store reference for API access
        app.state.orchestra_manager = orchestra_manager

        logger.info("Orchestra framework initialized successfully")
    except Exception as e:
        logger.error(f"Orchestra initialization failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Con-AI Backend")

    # Shutdown Orchestra manager
    if orchestra_manager:
        try:
            await orchestra_manager.shutdown()
            logger.info("Orchestra manager shutdown complete")
        except Exception as e:
            logger.error(f"Orchestra manager shutdown failed: {e}")


# Create FastAPI application
app = FastAPI(
    title="Con-AI Backend",
    description="Construction Intelligence Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Orchestra API router
from api.orchestra import router as orchestra_router

app.include_router(orchestra_router, prefix="/api")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "con-ai-backend",
        "version": "0.1.0",
        "websocket_connections": manager.get_connection_count(),
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket_endpoint(websocket)


# Basic API endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Con-AI Backend API", "version": "0.1.0", "docs": "/docs"}


@app.get("/api/status")
async def api_status():
    """API status endpoint."""
    return {
        "api_status": "operational",
        "database": "connected", 
        "websocket_connections": manager.get_connection_count(),
        "orchestra_enabled": True,
        "settings": {
            "cors_origins": settings.cors_origins,
        },
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404, content={"error": "Endpoint not found", "message": str(exc)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.host}:{settings.port}")

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
