# RentEase Backend - Setup Instructions

Backend API for RentEase rental booking platform.

## Requirements

- Python 3.10+
- pip (latest version)

## Quick Setup

### 1. Install uv Package Manager

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**
```bash
pip install uv
```

### 2. Extract & Navigate

```bash
# Extract the zip file
# Navigate to project directory
cd rentease
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Seed Database (Required!)

```bash
uv run python run_seed.py
```

### 5. Run Server

```bash
uv run python manage.py runserver
```

## Test Credentials

**Email:** `admin@rentease.com`  
**Password:** `admin`

**Note:** Use these credentials in the frontend application for testing.

## Backend URL

```
http://127.0.0.1:8000/
```