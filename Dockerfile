
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir streamlit pandas openpyxl matplotlib networkx
EXPOSE 8501
CMD ["streamlit", "run", "fe_funding_app.py"]
