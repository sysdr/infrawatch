# Use nginx for serving static files - common in production
FROM nginx:alpine

# Copy our HTML files to nginx serve directory
COPY public /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Nginx starts automatically in the base image
