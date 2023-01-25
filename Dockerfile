FROM python:3.8-slim
RUN apt-get update
RUN apt-get install gcc git -y
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/giampaolo/psutil.git

FROM python:3.9-slim
COPY --from=0 /usr/local/lib/python3.8/__pycache__ /usr/local/lib/python3.9/__pycache__
COPY --from=0 /usr/local/lib/python3.8/asyncio /usr/local/lib/python3.9/asyncio
COPY --from=0 /usr/local/lib/python3.8/collections /usr/local/lib/python3.9/collections
COPY --from=0 /usr/local/lib/python3.8/concurrent /usr/local/lib/python3.9/concurrent
COPY --from=0 /usr/local/lib/python3.8/ctypes /usr/local/lib/python3.9/ctypes
COPY --from=0 /usr/local/lib/python3.8/distutils /usr/local/lib/python3.9/distutils
COPY --from=0 /usr/local/lib/python3.8/email /usr/local/lib/python3.9/email
COPY --from=0 /usr/local/lib/python3.8/encodings /usr/local/lib/python3.9/encodings
COPY --from=0 /usr/local/lib/python3.8/html /usr/local/lib/python3.9/html
COPY --from=0 /usr/local/lib/python3.8/http /usr/local/lib/python3.9/http
COPY --from=0 /usr/local/lib/python3.8/importlib /usr/local/lib/python3.9/importlib
COPY --from=0 /usr/local/lib/python3.8/json /usr/local/lib/python3.9/json
COPY --from=0 /usr/local/lib/python3.8/logging /usr/local/lib/python3.9/logging
COPY --from=0 /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=0 /usr/local/lib/python3.8/urllib /usr/local/lib/python3.9/urllib
COPY --from=0 /usr/local/lib/python3.8/xml /usr/local/lib/python3.9/xml
COPY --from=0 /usr/local/lib/python3.8/xmlrpc /usr/local/lib/python3.9/xmlrpc
COPY --from=0 /usr/local/bin/filetype /usr/local/bin/filetype
COPY --from=0 /usr/local/bin/normalizer /usr/local/bin/normalizer
WORKDIR /app
COPY ./src ./src/
COPY ./main.py .
ENTRYPOINT [ "python", "main.py" ]
