# 🚀 Deployment Guide

## Streamlit Cloud Deployment (Recommended)

### Why Streamlit Cloud?
- Free for public repositories
- Automatic GitHub integration
- Handles dependencies automatically
- Built-in SSL/HTTPS
- Custom subdomain
- Environment variable management
- Automatic updates when you push to main

### Steps to Deploy

1. **Visit Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Deploy Your App**
   - Click "New app"
   - Select your repository: `madezmedia/fiverr-gig-optimizer`
   - Select branch: `main`
   - Set main file path: `src/app.py`

3. **Configure Environment Variables**
   In Streamlit Cloud settings, add these secrets:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key"
   SCRAPER_API_KEY = "your_scraper_api_key"
   FIVERR_API_KEY = "your_fiverr_api_key"  # Optional
   ```

4. **Advanced Settings**
   - Python version: 3.11
   - Memory: Standard (1GB)
   - Package dependencies: Will be read from requirements.txt

## Alternative Deployment Options

### 1. Docker Deployment
Create a Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Deploy using:
```bash
docker build -t fiverr-gig-optimizer .
docker run -p 8501:8501 fiverr-gig-optimizer
```

### 2. Heroku Deployment
1. Create Procfile:
```
web: streamlit run src/app.py
```

2. Deploy using Heroku CLI:
```bash
heroku create fiverr-gig-optimizer
heroku git:remote -a fiverr-gig-optimizer
git push heroku main
```

3. Set environment variables:
```bash
heroku config:set OPENAI_API_KEY=your_key
heroku config:set SCRAPER_API_KEY=your_key
```

### 3. AWS Elastic Beanstalk
1. Create requirements.txt at root:
```bash
cp requirements/requirements.txt .
```

2. Create .ebextensions/01_streamlit.config:
```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:container:python:
    WSGIPath: src/app.py
```

3. Deploy using AWS CLI:
```bash
eb init -p python-3.11 fiverr-gig-optimizer
eb create fiverr-gig-optimizer-env
```

## Production Considerations

### Security
- Always use HTTPS
- Keep API keys secure
- Implement rate limiting
- Monitor usage

### Performance
- Enable caching where appropriate
- Optimize database queries
- Use CDN for static assets
- Monitor memory usage

### Monitoring
- Set up error tracking
- Monitor API usage
- Track user analytics
- Set up alerts

### Scaling
- Use load balancing
- Implement caching
- Optimize database queries
- Use CDN for static assets

## Maintenance

### Regular Tasks
- Update dependencies
- Monitor error logs
- Check API usage
- Backup data
- Update SSL certificates

### Troubleshooting
1. Check application logs
2. Verify API connectivity
3. Monitor resource usage
4. Check environment variables
5. Verify database connections

## Backup and Recovery

### Data Backup
- Regular state backups
- Database backups if added
- Configuration backups
- Environment variable documentation

### Recovery Steps
1. Verify backup integrity
2. Restore configuration
3. Restore application state
4. Verify functionality
5. Update DNS if needed

## Scaling Considerations

### Vertical Scaling
- Increase memory
- Upgrade CPU
- Expand storage

### Horizontal Scaling
- Load balancing
- Multiple instances
- Database sharding
- Caching layers

## Cost Optimization

### Free Tier Options
- Streamlit Cloud (Recommended)
- Heroku (Limited)
- AWS Free Tier

### Paid Options
- AWS Elastic Beanstalk
- Google Cloud Run
- DigitalOcean App Platform

Choose based on:
- Expected traffic
- Budget constraints
- Scaling needs
- Support requirements
