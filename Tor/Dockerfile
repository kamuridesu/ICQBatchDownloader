FROM icqdownloader:latest
RUN apt-get update
RUN apt-get install tor cowsay curl -y
ENV TOR=enabled
COPY ./entrypoint.sh .
ENTRYPOINT [ "bash", "entrypoint.sh"]
