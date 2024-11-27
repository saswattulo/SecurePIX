# docker file to containerize the application
FROM python:3.11.3-slim-buster

# Set the environment variables both at build and at run time.
# in this case, we make sure python output is visible in docker logs
ENV PYTHONBUFFERED=1

# Copy application code into the container
COPY . /app

# Set working directory from now (like cd)
WORKDIR /app

# install python dependencies
RUN python3 -m pip install -r requirements.txt

# Expose the streamlit default port
EXPOSE 8501

# set default command when container starts
ENTRYPOINT ["streamlit","run","app.py"]

# pass the main application file to streamlit
CMD ["app.py"]