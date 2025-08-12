# LicenseHub - Software License Management (FastAPI + MariaDB + AD)

LicenseHub is a minimal web service to manage software licenses and assignments with Active Directory login.

- Python FastAPI backend, SQLAlchemy ORM
- MariaDB database
- LDAP (Active Directory) username/password login with JWT
- Basic REST APIs and a simple server-rendered dashboard
- Scheduled expiration checks

## Quickstart (Docker)

1. Copy environment file

```bash
cp .env.example .env
```

2. Edit `.env` to point to your MariaDB and AD

3. Start services

```bash
docker compose up -d --build
```

4. Open the app:

- API docs: http://localhost:8000/docs
- UI: http://localhost:8000/

## Manual run (without Docker)

Prereqs: Python 3.11+, MariaDB 10.6+

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # update values
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Active Directory (LDAP) Login

- POST `/auth/login` with `{ "username": "DOMAIN\\user", "password": "***" }` or `user@domain.local`
- On success, you receive a JWT. Use it as `Authorization: Bearer <token>`
- First login will auto-provision a local user record with AD display name, email, department

Configure AD in `.env`:

- `AD_SERVER_URI=ldaps://dc01.domain.local:636` (recommend LDAPS)
- `AD_BASE_DN=DC=domain,DC=local`
- `AD_USER_DN_FORMAT={username}` (supports `DOMAIN\\{username}` or `{username}@domain.local`)

Optionally set a service account for searches:

- `AD_SERVICE_ACCOUNT_DN=CN=svc_ldap,OU=Service Accounts,DC=domain,DC=local`
- `AD_SERVICE_ACCOUNT_PASSWORD=***`

## Database

By default uses SQLAlchemy async engine with `aiomysql` driver. Configure via `DATABASE_URL`, e.g.:

```
DATABASE_URL=mysql+aiomysql://licensehub:licensehub@db:3306/licensehub
```

Tables are auto-created at startup for convenience. For production, switch to migrations (Alembic).

## APIs (high level)

- Auth: `/auth/login`
- Users: `/users/me`, `/users`
- Vendors: `/vendors`
- Products: `/products`
- Licenses: `/licenses` (CRUD)
- Assignments: `/assignments`
- Purchase Orders: `/purchase-orders`
- Memos: `/memos`
- Health: `/healthz`
- Expiration checks: `/jobs/check-expirations`

## Windows Server + IIS (optional)

- Run app with `uvicorn` as a Windows service or behind IIS reverse proxy
- For Integrated Windows Authentication (SSO), place IIS in front with Windows Auth enabled and forward a trusted header (e.g., `X-REMOTE-USER`). Extend `auth.py` to accept SSO header and auto-login

## Security

- Use LDAPS (port 636) or LDAP over StartTLS
- Store JWT secret securely (e.g., Azure Key Vault, DPAPI, or env)
- Restrict DB user permissions to necessary CRUD only

## License

MIT