FROM python:3.12-slim
RUN pip install --no-cache-dir "requests>=2.32"
COPY loadgen.py /loadgen.py
ENTRYPOINT ["python", "/loadgen.py"]
