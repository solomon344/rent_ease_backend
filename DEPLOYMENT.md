# RentEase Backend Deployment Guide

This guide covers deploying the RentEase Django backend to production environments.

## Environment Configuration

### 1. Copy and Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your production values
nano .env
```

### 2. Required Environment Variables

#### Django Core
- `SECRET_KEY`: Generate a secure random key for production
- `DEBUG`: Must be `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of your domain(s)

#### Database
The backend supports multiple database engines via environment variables:

**SQLite (Development)**
```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=./db.sqlite3
```

**PostgreSQL (Production Recommended)**
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=rentease_db
DB_USER=rentease_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

**MySQL**
```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=rentease_db
DB_USER=rentease_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306
```

### 3. Generate a Secret Key

```bash
# Using Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Or using OpenSSL
openssl rand -base64 64
```

## Docker Deployment

The project includes a Dockerfile for containerized deployment.

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t rentease-backend .

# Run the container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name rentease-backend \
  rentease-backend
```

### Docker Compose (with PostgreSQL)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: rentease_db
      POSTGRES_USER: rentease_user
      POSTGRES_PASSWORD: your_secure_password
    ports:
      - "5432:5432"

  web:
    build: .
    command: gunicorn rent_ease_backend.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=rentease_db
      - DB_USER=rentease_user
      - DB_PASSWORD=your_secure_password
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      - db

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
- [ ] Set up a production database (PostgreSQL recommended)
- [ ] Configure HTTPS/SSL
- [ ] Set up proper logging and monitoring
- [ ] Configure backup strategy for database
- [ ] Set up rate limiting
- [ ] Review and secure CORS settings
- [ ] Ensure `.env` file is in `.gitignore`

## Security Considerations

1. **Never commit `.env` files** - The `.env` file contains sensitive credentials and is already in `.gitignore`

2. **Use environment variables for all secrets** - All sensitive configuration should come from environment variables

3. **Enable HTTPS** - Always use HTTPS in production

4. **Set secure headers** - Consider adding Django security middleware

5. **Rate limiting** - Implement rate limiting for API endpoints

## Troubleshooting

### Database Connection Issues

If you're having trouble connecting to your database:

1. Verify all database environment variables are correct
2. Ensure the database server is running
3. Check firewall rules allow connections
4. For PostgreSQL, ensure the user has proper permissions

### Static Files

Make sure to collect static files:

```bash
python manage.py collectstatic --noinput
```

### Migrations

Always run migrations after deployment:

```bash
python manage.py migrate
```

## Support

For issues and questions, please open an issue on the GitHub repository.