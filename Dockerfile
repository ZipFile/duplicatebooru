FROM alpine:20210212 as build-base

RUN apk add --no-cache python3-dev build-base

RUN python3 -m venv /env

ENV PATH "/env/bin:$PATH"

RUN pip install -U pip wheel setuptools

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

FROM alpine:20210212

RUN adduser --system --ingroup users user
RUN apk add --no-cache ca-certificates imagemagick optipng python3

COPY --from=build-base /env /env

ENV PATH "/env/bin:$PATH"

COPY . /app

WORKDIR /app

RUN pip install --no-deps -e .

USER user:users

ENTRYPOINT ["duplicatebooru"]
