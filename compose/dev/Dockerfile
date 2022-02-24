FROM python:3.9.1-alpine

RUN apk --update add \
    bash \
    sqlite \
    sudo \
    wget \
    vim

WORKDIR /usr/src/app

COPY ./requirements/dev.txt ./

RUN pip install --upgrade pip && \
    pip install -r dev.txt

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/src"

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
