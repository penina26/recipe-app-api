FROM python:3.9-alpine3.13
LABEL maintainer="ninaru.com"

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Copy only requirements first to leverage Docker layer caching
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

ARG DEV=false

# 1. Create virtual environment and upgrade pip
# 2. Install Pillow/Postgres permanent system dependencies (jpeg-dev)
# 3. Install temporary build dependencies (zlib)
# 4. Install Python packages (and dev packages if ARG DEV=true)
# 5. Clean up temp folders and build dependencies to reduce image size
# 6. Create non-root user for security
# 7. Create media/static upload folders and assign permissions
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

# Set virtual environment to be used by default
ENV PATH="/py/bin:$PATH"

# Set working directory and copy application code
WORKDIR /app
COPY ./app /app

# Expose Django development server port
EXPOSE 8000

# Switch to the non-root user
USER django-user