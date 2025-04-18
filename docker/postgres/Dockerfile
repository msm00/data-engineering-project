FROM postgres:16

# Instalace užitečných rozšíření
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-16-postgis-3 \
    postgresql-16-postgis-3-scripts \
    postgresql-16-cron \
    && rm -rf /var/lib/apt/lists/*

# Kopírování vlastních inicializačních skriptů
COPY ./init-scripts/ /docker-entrypoint-initdb.d/

# Volitelně: nastavení vlastní konfigurace
COPY ./postgresql.conf /etc/postgresql/postgresql.conf

# Vystav port
EXPOSE 5432

# Nastavení konfiguračního souboru jako hlavního konfiguračního souboru
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"] 