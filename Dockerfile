FROM python:3.6-slim
RUN pip3 install facebook-sdk==2.0.0 \
                 google==1.9.3 \
                 google-api-python-client==1.6.4

RUN pip3 install ipython
CMD ["ipython"]

VOLUME /fest
COPY . /fest
RUN pip3 install -e /fest
