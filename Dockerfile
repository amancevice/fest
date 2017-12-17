FROM python:3.6-slim
VOLUME /fest
COPY . /fest
RUN pip3 install -e /fest
ENTRYPOINT ["fest"]
CMD ["--help"]
