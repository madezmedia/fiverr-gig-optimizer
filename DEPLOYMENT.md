# Deploying Fiverr Gig Optimizer on Elest.io

This guide provides step-by-step instructions for deploying the Fiverr Gig Optimizer application on Elest.io.

## Prerequisites

1. An account on [Elest.io](https://elest.io)
2. Your application code pushed to GitHub (https://github.com/madezmedia/fiverr-gig-optimizer)
3. Required environment variables:
   - OPENAI_API_KEY
   - SCRAPER_API_KEY
   - FIVERR_API_KEY (optional)

## Deployment Steps

### 1. Login to Elest.io

1. Go to [https://elest.io](https://elest.io)
2. Click on "Login" and authenticate with your account

### 2. Create a New Project

1. Click on "New Project"
2. Choose a name for your project (e.g., "fiverr-gig-optimizer")
3. Select your preferred region
4. Click "Create Project"

### 3. Configure Deployment

1. In your project dashboard, click "Deploy New Service"
2. Select "Docker Container" as the deployment type
3. Choose "GitHub" as the source
4. Select your repository (madezmedia/fiverr-gig-optimizer)
5. Configure the following settings:
   - Container Port: 8501
   - Health Check Path: /_stcore/health
   - Memory: At least 1GB
   - CPU: At least 1 vCPU

### 4. Configure Environment Variables

Add the following environment variables in the Elest.io dashboard:

```
OPENAI_API_KEY=your_openai_api_key
SCRAPER_API_KEY=your_scraper_api_key
FIVERR_API_KEY=your_fiverr_api_key (optional)
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
```

### 5. Deploy the Application

1. Click "Deploy" to start the deployment process
2. Elest.io will automatically:
   - Pull your code from GitHub
   - Build the Docker image using the provided Dockerfile
   - Start the container with the configured environment variables
   - Set up SSL/TLS certificate
   - Configure the load balancer

### 6. Verify Deployment

1. Once deployment is complete, click on the provided URL to access your application
2. Verify that:
   - The application loads successfully
   - You can perform profile analysis
   - API integrations are working

### 7. Monitoring and Maintenance

Elest.io provides several tools for monitoring your application:

1. **Logs**: Access container logs from the dashboard
2. **Metrics**: Monitor CPU, memory, and network usage
3. **Health Checks**: View the status of automated health checks

### 8. Automatic Updates

To enable automatic updates:

1. Go to your service settings
2. Enable "Auto Deploy"
3. Configure the branch to track (e.g., main)

This will automatically deploy new versions when you push changes to GitHub.

## Troubleshooting

### Common Issues

1. **Application Not Starting**
   - Check the container logs for error messages
   - Verify all required environment variables are set
   - Ensure the container has enough memory and CPU resources

2. **API Integration Issues**
   - Verify API keys are correctly set in environment variables
   - Check API rate limits
   - Review application logs for API-related errors

3. **Performance Issues**
   - Consider scaling up resources (memory/CPU)
   - Enable caching in the application
   - Monitor resource usage metrics

### Getting Help

If you encounter issues:

1. Check the application logs in Elest.io dashboard
2. Review the [Elest.io documentation](https://docs.elest.io)
3. Contact Elest.io support through their support portal

## Security Considerations

1. **Environment Variables**
   - Never commit sensitive values to the repository
   - Use Elest.io's secure environment variable storage
   - Regularly rotate API keys

2. **Access Control**
   - Configure IP restrictions if needed
   - Set up authentication for your application
   - Regularly review access logs

3. **Updates**
   - Keep base images updated
   - Regularly update dependencies
   - Monitor security advisories

## Backup and Recovery

1. **Database Backups**
   - Configure automated backups if using a database
   - Test backup restoration procedures

2. **Application State**
   - Use persistent storage for important data
   - Document recovery procedures

## Cost Optimization

1. **Resource Allocation**
   - Monitor usage patterns
   - Adjust resources based on actual needs
   - Consider using auto-scaling rules

2. **API Usage**
   - Monitor API call volumes
   - Implement caching where possible
   - Set up usage alerts

## Maintenance Schedule

1. **Regular Updates**
   - Schedule dependency updates
   - Plan maintenance windows
   - Test updates in staging environment

2. **Monitoring**
   - Set up alerts for critical metrics
   - Review logs regularly
   - Monitor API usage and costs
