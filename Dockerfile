FROM python:3.6-slim
ENV GOOGLE_ACCOUNT_TYPE=service_account \
    GOOGLE_SCOPE=https://www.googleapis.com/auth/calendar
VOLUME /fest
COPY . /fest
RUN pip3 install ipython==6.2.1 && \
    pip3 install -e /fest
ENTRYPOINT ["fest"]
CMD ["--help"]
