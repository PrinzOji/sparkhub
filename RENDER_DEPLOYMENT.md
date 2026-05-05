# Render Deployment Guide for Sparkhub

## Prerequisites
- GitHub account with your repository
- Render account (https://render.com)

## Environment Variables Required

Set these on Render dashboard for your service:

```
SECRET_KEY=your-very-secure-random-secret-key
DEBUG=false
ALLOWED_HOSTS=your-service.onrender.com,www.your-service.onrender.com
DATABASE_URL=postgresql://user:password@host/dbname
MPESA_ENVIRONMENT=sandbox (or production)
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_PASSKEY=your-passkey
MPESA_SHORTCODE=your-shortcode
MPESA_CALLBACK_URL=https://your-service.onrender.com/mpesa-express-simulate/
```

## Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create PostgreSQL Database on Render**
   - Go to Render Dashboard
   - Click "New +" → PostgreSQL
   - Create a free PostgreSQL instance
   - Copy the Database URL

3. **Create Web Service**
   - Go to Render Dashboard
   - Click "New +" → Web Service
   - Connect your GitHub repository
   - Select the branch to deploy

4. **Configure Service**
   - Name: `sparkhub`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn sparkhub.wsgi`
   - Plan: Free (or paid as needed)

5. **Add Environment Variables**
   - In the Render dashboard, go to your service settings
   - Add all environment variables listed above
   - **Important**: Set a strong SECRET_KEY using a generator or:
     ```python
     from django.core.management.utils import get_random_secret_key
     print(get_random_secret_key())
     ```

6. **Deploy**
   - Render will automatically deploy when you push to GitHub
   - Watch the logs in Render dashboard

## Database Migration

After deployment, you may need to run:
```bash
python manage.py migrate
python manage.py createsuperuser
```

You can do this via Render's shell or by adding commands to the release phase in `Procfile`.

## Static Files

WhiteNoise is configured to handle static files automatically. Run:
```bash
python manage.py collectstatic --noinput
```

This is already in the build command.

## Media Files

For production, consider using cloud storage (AWS S3, etc.) instead of local media files.

## Troubleshooting

- **502 Bad Gateway**: Check application logs for errors
- **Static files not loading**: Ensure `collectstatic` ran successfully
- **Database connection errors**: Verify DATABASE_URL is correct
- **Import errors**: Ensure all dependencies are in `requirements.txt`

## Production Checklist

- [ ] SECRET_KEY changed and kept secure
- [ ] DEBUG set to false
- [ ] ALLOWED_HOSTS updated with your domain
- [ ] DATABASE_URL pointing to PostgreSQL
- [ ] All MPesa credentials configured
- [ ] CSRF_TRUSTED_ORIGINS configured if needed
- [ ] Static files collecting successfully
- [ ] HTTPS enforced (automatic on Render)

## Notes

- The free tier on Render has limitations (spins down after inactivity)
- Consider paid tier for production applications
- Monitor usage and upgrade if needed
