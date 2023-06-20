import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mantium_scanner.api.routes.auth import auth_router
from mantium_scanner.api.routes.providers import providers_router
from mantium_scanner.error_handling import add_error_handlers
from mantium_scanner.logging_config import setup_logging
from mantium_scanner.startup import startup_event

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

setup_logging()


app = FastAPI(on_startup=[startup_event])


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router, prefix='', tags=['auth'])
app.include_router(providers_router, prefix='', tags=['providers'])

add_error_handlers(app)


@app.get('/ping')
def pong() -> dict[str, str]:
    """Health check endpoint"""
    return {'ping': 'pong!'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
