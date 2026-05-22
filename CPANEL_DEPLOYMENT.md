# cPanel Deployment

Use these steps to deploy this Django inventory system to `sujalnepaligaire.com.np`.

## 1. Check Python Support

In cPanel, open **Setup Python App**.

- Choose Python 3.12 or newer for Django 6.
- If your hosting only offers Python 3.10 or 3.11, ask the host to enable a newer Python version or downgrade the project to Django 5.2 LTS.

## 2. Create The Python App

Recommended settings:

- Application root: `inventory_ms`
- Application URL: `sujalnepaligaire.com.np`
- Application startup file: `passenger_wsgi.py`
- Application entry point: `application`

After creating it, cPanel will show an activate command for the virtual environment. Copy that command.

## 3. Upload Project Files

Upload the project files into the application root. Do not upload these local-only files/folders:

- `.venv/`
- `__pycache__/`
- `*.pyc`
- `staticfiles/`
- `server.log`
- `server.err.log`

Upload `db.sqlite3` only if you want to keep the current local data. For a real business database, make regular backups or move to MySQL.

## 4. Set Environment Variables

In **Setup Python App**, add these environment variables:

```text
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=sujalnepaligaire.com.np,www.sujalnepaligaire.com.np
DJANGO_CSRF_TRUSTED_ORIGINS=https://sujalnepaligaire.com.np,https://www.sujalnepaligaire.com.np
```

Generate a new secret key inside the Python app terminal:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then add it as:

```text
DJANGO_SECRET_KEY=paste-generated-key-here
```

When `DJANGO_DEBUG=False`, the project automatically enables HTTPS redirect and secure cookies. Enable AutoSSL before opening the site. If you must test before SSL is ready, temporarily add:

```text
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
```

## 5. Install And Prepare The App

In cPanel Terminal or SSH:

```bash
cd ~/inventory_ms
# paste the virtualenv activate command shown by cPanel
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Restart the Python app from cPanel after running these commands.

## 6. Point The Domain

In your domain DNS, point these records to your hosting server IP:

```text
sujalnepaligaire.com.np      A      your-hosting-ip
www.sujalnepaligaire.com.np  CNAME  sujalnepaligaire.com.np
```

Then enable SSL in cPanel using **SSL/TLS Status** or **AutoSSL**.

## 7. Open The Site

After DNS and SSL are ready, open:

```text
https://sujalnepaligaire.com.np/
```

Admin panel:

```text
https://sujalnepaligaire.com.np/admin/
```
