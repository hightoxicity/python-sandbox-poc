FROM python:3

RUN apt-get update && \
    apt-get install -y libcap-dev

RUN mkdir /sandbox

#RUN /usr/local/bin/pip3 install pandas numpy python-prctl

ADD chroot.py /
ADD requirements.txt /

RUN pip3 install -r requirements.txt

RUN DEBIAN_FRONTEND=noninteractive addgroup --gid 1000 untrusted \
  && DEBIAN_FRONTEND=noninteractive adduser --gecos "First Last,RoomNumber,WorkPhone,HomePhone" \
  --disabled-login --uid 1000 --ingroup untrusted --shell /bin/sh untrusted

CMD [ "/usr/local/bin/python3", "/chroot.py" ]
