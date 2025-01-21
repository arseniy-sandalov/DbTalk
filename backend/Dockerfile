FROM python:3.12-slim
WORKDIR /app
COPY . ./
RUN pip install --no-cache-dir fastapi pydantic configparser langchain_openai langchain_core langchain_community sqlalchemy langchain python-jose uvicorn websockets passlib langgraph langfuse logging redis
RUN pip install "fastapi[standard]"
EXPOSE 8000 
EXPOSE 6379
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]