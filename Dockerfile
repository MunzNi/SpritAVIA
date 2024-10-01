FROM --platform=linux/amd64 python:3.11

# Install dependencies, including Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libnss3 \
    libgconf-2-4 \
    chromium-driver \
    cron

# Install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# set display port to avoid crash
ENV DISPLAY=:99

# upgrade pip
RUN pip install --upgrade pip

# Copy the requirements.txt file to /app
COPY requirements.txt /app/requirements.txt

# Install Python dependencies listed in requirements.txt
RUN pip install -r /app/requirements.txt

# Set the working directory inside the image to /app
WORKDIR /app

# Copy the Python script 'app.py' to /app
COPY scrape.py /app/
RUN chmod +x /app/scrape.py

RUN touch /var/log/cron.log

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]