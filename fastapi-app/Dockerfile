FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables
ENV USER=${USER}
ENV PASSWORD=${PASSWORD}
ENV HOST=${HOST}
ENV PORT=${PORT}
ENV DB=${DB}
ENV API_KEY=${PORT}
ENV SECRET_KEY=${DB}

CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8000"]