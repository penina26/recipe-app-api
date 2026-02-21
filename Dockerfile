FROM python:3.9-alpine3.13
LABEL maintainer="ninaru.com"

# Using key=value format
ENV PYTHONUNBUFFERED=1

# 1. Copy ONLY requirements first to leverage Docker layer caching
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# 2. Install dependencies conditionally based on DEV argument
ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Update the PATH so "python" runs from the virtual env
ENV PATH="/py/bin:$PATH"

# 3. Set workdir and COPY the app code AFTER dependencies are installed
WORKDIR /app
COPY ./app /app

EXPOSE 8000

# Switch to the non-root user for security
USER django-user