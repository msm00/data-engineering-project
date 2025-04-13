# Nastavení projektu

## Požadavky

- **Python** 3.10 - 3.12
- **Docker** a Docker Compose
- **Git**
- Minimálně 8GB RAM pro lokální development

## Instalace pro vývojáře

### 1. Klonování repozitáře

```bash
git clone https://github.com/msm00/data-engineering-project
cd data-engineering-project
```

### 2. Nastavení Python prostředí

Doporučujeme používat pyenv pro správu verzí Pythonu:

```bash
# Instalace potřebné verze Pythonu
pyenv install 3.12.2

# Nastavení pro tento projekt
pyenv local 3.12.2

# Instalace Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Instalace závislostí
poetry install
```

### 3. Nastavení prostředí

Vytvořte soubor `.env` podle vzoru v `.env.example`:

```bash
cp .env.example .env
# Upravte proměnné podle potřeby
```

### 4. Spuštění kontejnerů

```bash
cd docker
docker-compose up -d
```

### 5. Inicializace Airflow

Po prvním spuštění je potřeba inicializovat Airflow databázi:

```bash
docker-compose exec airflow airflow db init
docker-compose exec airflow airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

## Přístup k webovým rozhraním

- **Airflow**: http://localhost:8080
- **Spark UI**: http://localhost:4040
- **HDFS UI**: http://localhost:9870

## Testování

Spuštění testů:

```bash
poetry run pytest
```

## Nejčastější problémy

### Nedostatek paměti v Dockeru

Pokud se kontejnery zasekávají nebo nechtějí spustit, zvyšte přidělení paměti v nastavení Dockeru.

### Problém s připojením k PostgreSQL

Zkontrolujte, zda jsou správně nastavené přístupové údaje v `.env` souboru.

### Chyba při spuštění Spark jobů

Projděte logy pomocí:

```bash
docker-compose logs -f spark-master
```
