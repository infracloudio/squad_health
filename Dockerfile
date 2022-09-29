FROM python:3.9
WORKDIR /squad_health
COPY . .
EXPOSE 8501
RUN pip install -r requirements.txt
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app.py" ]
