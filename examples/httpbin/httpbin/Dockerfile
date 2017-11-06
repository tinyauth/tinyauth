FROM python:2.7
RUN pip install httpbin gunicorn
CMD ["gunicorn", "httpbin:app", "-b", "0.0.0.0:8000"]
