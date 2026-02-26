# 🛍️ Amazon Product & User API

A FastAPI application that serves product and user data from a MySQL RDS database. This repository originally contained a recommendation engine, which has been removed.

---

## 📁 Project Structure

```
.
├── .env                        # DB credentials (never commit this)
├── .gitignore
├── requirements.txt
├── amazon_categories.csv       # Raw category data
├── amazon_products.csv         # Raw product data (~367 MB)
├── to_rds.py                   # Step 1: Load CSVs into RDS
└── api.py                      # Step 2: FastAPI REST API
```

---

## 🗄️ Database Schema

```
amazon_categories       ← loaded by to_rds.py
amazon_products         ← loaded by to_rds.py
users                   ← user profiles (populated via external scripts)
product_ratings         ← star ratings (populated via external scripts)
```

---

## ⚙️ Setup

### 1. Clone & install dependencies

```bash
git clone <your-repo-url>
cd <project-folder>

python -m venv venv
source venv/bin/activate        # Windows: venv\\Scripts\\activate

pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=3306
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

---

## 🚀 Usage

### Step 1 — Load Amazon product data into RDS

```bash
python to_rds.py
```

Reads `amazon_categories.csv` and `amazon_products.csv` and uploads them to MySQL. The products file (~367 MB) is handled in chunks to keep memory usage low.

### Step 2 — Start the API

```bash
uvicorn api:app --reload
```

The API serves product and user profile data over HTTP.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/users/{user_id}/profile` | Get user info and their product ratings |
| `GET` | `/stats` | High-level system stats |

---

## 📋 Requirements

```
pandas
sqlalchemy
pymysql
python-dotenv
cryptography
faker
fastapi
uvicorn
```

Install all with:

```bash
pip install -r requirements.txt
```
