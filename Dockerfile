# Basis-Image von Microsoft/Playwright: enthält Python + Chromium + alle
# Systembibliotheken, die Playwright zum Steuern des Browsers braucht.
# Version muss zur playwright-Version in requirements.txt passen (1.44.0).
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Persistenter Speicher fürs Hosting: hier landet die Datenbank, damit sie
# nicht bei jedem Neustart/Deploy verloren geht (siehe render.yaml disk mount).
ENV DATEN_ORDNER=/var/data
RUN mkdir -p /var/data

EXPOSE 8000

# $PORT setzt der Hosting-Anbieter automatisch. Lokal (ohne $PORT) fällt es auf 8000 zurück.
CMD ["sh", "-c", "gunicorn -w 1 --threads 4 -b 0.0.0.0:${PORT:-8000} webapp:app"]
