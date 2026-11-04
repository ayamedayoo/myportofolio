FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 80

# Migrasi dijalankan saat container start (bukan saat build) karena database
# produksi baru bisa diakses lewat environment variable PWS saat runtime.
# Kalau migrate gagal (mis. database belum terhubung), gunicorn tetap dijalankan
# supaya halaman yang tidak membutuhkan database masih bisa diakses.
CMD ["sh", "-c", "python manage.py migrate --noinput || echo 'WARNING: migrate gagal'; exec gunicorn portofolio.wsgi:application --bind 0.0.0.0:80"]
