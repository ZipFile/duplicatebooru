FROM ubuntu:focal as build-base

RUN apt-get update && \
    apt-get install -y python3-all python3-venv

RUN python3 -m venv /env

ENV PATH "/env/bin:$PATH"

RUN pip install -U pip wheel setuptools

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

FROM ubuntu:focal

RUN adduser --system --ingroup users user
RUN apt-get update && \
    apt-get install -y ca-certificates imagemagick python3-all

COPY --from=build-base /env /env

ENV PATH "/env/bin:$PATH"

COPY . /app

WORKDIR /app

RUN pip install --no-deps -e .

USER user:users
ENV PYTHONASYNCIODEBUG "1"

ENTRYPOINT ["duplicatebooru"]
