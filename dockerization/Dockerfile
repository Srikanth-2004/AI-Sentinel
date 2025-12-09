# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (punkt tokenizer)
RUN python -m nltk.downloader punkt

# Copy the rest of the application code
COPY . .

# Command to run the application
# We use unbuffered output so logs show up immediately
CMD ["python", "-u", "brain_v2.0_cascade.py"]