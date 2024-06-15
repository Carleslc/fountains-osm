FROM python:3.12

WORKDIR /fountains-osm

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY .env.template .env

COPY ./app /fountains-osm/app
COPY ./queries /fountains-osm/queries

CMD ["fastapi", "run", "app/main.py", "--port", "80", "--workers", "2"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--workers", "2", "--proxy-headers"]
