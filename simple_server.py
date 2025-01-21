# from fastapi import FastAPI, Request, HTTPException
# import httpx

# app = FastAPI()

# LM_STUDIO_BASE_URL = "http://localhost:1234/v1"

# @app.post("/openai/deployments/{model}/chat/completions")
# async def proxy_chat_completions(model: str, request: Request):
#     # Parse the incoming JSON body
#     try:
#         incoming_data = await request.json()
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Invalid JSON body: {str(e)}")
    
#     # Transform the incoming data to fit LM Studio's /v1/chat/completions format
#     lm_studio_data = {
#         "model": model,  # Model name
#         "messages": incoming_data.get("messages", []),  # Chat messages
#         "temperature": incoming_data.get("temperature", 1.0),  # Optional parameter
#         "max_tokens": incoming_data.get("max_tokens", 256)  # Optional parameter
#     }
    
#     # Forward the request to LM Studio
#     async with httpx.AsyncClient() as client:
#         response = await client.post(f"{LM_STUDIO_BASE_URL}/chat/completions", json=lm_studio_data)

#     # Relay LM Studio's response
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)

#     return response.json()

# @app.get("/openai/deployments/meta-llama-3.1-8b-instruct/models")
# async def get_models():
#     # Fetch the models from LM Studio
#     async with httpx.AsyncClient() as client:
#         response = await client.get(f"{LM_STUDIO_BASE_URL}/models")

#     # Relay LM Studio's response
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)

#     return response.json()
import logging
from fastapi import FastAPI, Request, HTTPException
import httpx

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"


@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    logging.debug(f"🟩Incoming Request: {request.method} {request.url}")
    logging.debug(f"🟩Headers: {request.headers}")
    logging.debug(f"🟩Body: {body.decode('utf-8')}")
    
    response = await call_next(request)
    
    # Log outgoing response status and body
    logging.debug(f"Outgoing Response Status: {response.status_code}")
    try:
        response_body = [chunk async for chunk in response.aiter_bytes()]
        logging.debug(f"Outgoing Response Body: {b''.join(response_body).decode('utf-8')}")
    except Exception as e:
        logging.debug(f"Error logging response body: {str(e)}")
    
    return response



@app.post("/openai/deployments/{model}/chat/completions")
async def proxy_chat_completions(model: str, request: Request):
    try:
        # Log incoming request body
        incoming_data = await request.json()
        logger.debug(f"👉Incoming request data: {incoming_data}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {str(e)}")

    lm_studio_data = {
        "model": incoming_data.get("model", model),
        "messages": incoming_data.get("messages", []),
        "temperature": incoming_data.get("temperature", 0.2),
        "max_tokens": incoming_data.get("max_tokens", 4000),
        "tools": incoming_data.get("tools", [])  
    }

    logger.debug(f"👉👉Data sent to LM Studio: {lm_studio_data}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{LM_STUDIO_BASE_URL}/chat/completions", json=lm_studio_data)
            response.raise_for_status()  # This will raise an error for any non-2xx response.
            lm_response = response.json()
            logger.debug(f"LM Response: {lm_response}")
    except httpx.HTTPStatusError as e:
        # Log the detailed error response text
        logger.error(f"Error response from LM Studio: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"LM Studio Error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Failed to reach LM Studio: {str(e)}")

    # Relay the LM Studio response directly
    return lm_response



@app.get("/openai/deployments/meta-llama-3.1-8b-instruct/models")
async def get_models():
    """
    Fetch the list of models from LM Studio and relay them to the .NET application.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            lm_response = await client.get(f"{LM_STUDIO_BASE_URL}/models")
        
        if lm_response.status_code != 200:
            raise HTTPException(
                status_code=lm_response.status_code,
                detail=f"LM-Studio Error: {lm_response.text}"
            )
        
        return lm_response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"HTTP Request Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")



### INFO: 127.0.0.1:42938 - "POST /openai/deployments/meta-llama-3.1-8b-instruct/chat/completions?api-version=2024-08-01-preview HTTP/1.1" 200 OK

### INFO:     127.0.0.1:42938 - "POST /openai/deployments/meta-llama-3.1-8b-instruct/chat/completions?api-version=2024-08-01-preview HTTP/1.1" 400 Bad Request