#   ▗▄▄▖ ▗▄▖ ▗▖  ▗▖▗▖  ▗▖ ▗▄▖  ▗▄▄▖
#  ▐▌   ▐▌ ▐▌▐▛▚▖▐▌▐▌  ▐▌▐▌ ▐▌▐▌
#  ▐▌   ▐▛▀▜▌▐▌ ▝▜▌▐▌  ▐▌▐▛▀▜▌ ▝▀▚▖
#  ▝▚▄▄▖▐▌ ▐▌▐▌  ▐▌ ▝▚▞▘ ▐▌ ▐▌▗▄▄▞▘

FROM python:3.13.5-slim-bookworm AS canvas

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE canvas.settings 

# Set working directory in the container
WORKDIR /canvas

# Install system dependencies required for Python packages 
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  git \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt /canvas/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project
COPY /canvas_project /canvas/

# Collect static files into a directory that Nginx can serve
RUN python manage.py collectstatic --noinput --clear

# Expose the port were the website is running
EXPOSE 8000

# Start the daphne python server 
CMD [ "daphne", "-b", "0.0.0.0", "-p", "8000", "canvas.asgi:application" ]

#  ▗▖  ▗▖ ▗▄▄▖▗▄▄▄▖▗▖  ▗▖▗▖  ▗▖
#  ▐▛▚▖▐▌▐▌     █  ▐▛▚▖▐▌ ▝▚▞▘
#  ▐▌ ▝▜▌▐▌▝▜▌  █  ▐▌ ▝▜▌  ▐▌
#  ▐▌  ▐▌▝▚▄▞▘▗▄█▄▖▐▌  ▐▌▗▞▘▝▚▖

FROM nginx:alpine AS nginx

# Remove default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
# This file will tell Nginx how to serve the static files
COPY nginx.conf /etc/nginx/conf.d/nginx.conf

# Copy collected static files from the django_build stage
COPY --from=canvas canvas/collected_static_files /usr/share/nginx/html/static

RUN mkdir /usr/share/nginx/ssl && chmod 700 /usr/share/nginx/ssl

# Copy the test ssl keys and certificate
COPY test.crt /usr/share/nginx/ssl
COPY test.key /usr/share/nginx/ssl

# Expose port 80 for incoming HTTP requests
EXPOSE 80

# Command to run Nginx when the container starts
CMD ["nginx", "-g", "daemon off;"]

# TODO: Add logger or dashboard for Django
