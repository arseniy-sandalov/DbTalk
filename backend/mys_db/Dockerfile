FROM python
WORKDIR /sqlite_db
COPY create_db.py /sqlite_db/
RUN pip install --no-cache-dir sqlalchemy requests 
EXPOSE 80
CMD [ "python3",  "create_db.py"]

