FROM python:3.8-alpine

RUN addgroup hacker
RUN adduser --disabled-password -G hacker hacker
USER hacker 

# install autorecon tools

# virustotal key
ARG VIRUSTOTAL_KEY
ENV VIRUSTOTAL_KEY=${VIRUSTOTAL_KEY}

# amass
WORKDIR /home/hacker/
RUN wget https://github.com/OWASP/Amass/releases/download/v3.10.5/amass_linux_amd64.zip
RUN unzip amass_linux_amd64.zip
RUN rm amass_linux_amd64.zip
ENV PATH="/home/hacker/amass_linux_amd64/:${PATH}"

# dig
USER root
RUN apk update
RUN apk add bind-tools
RUN apk add git
USER hacker

# dnsgen
WORKDIR /home/hacker/
RUN git clone https://github.com/ProjectAnte/dnsgen
WORKDIR /home/hacker/dnsgen/
RUN pip install -r requirements.txt
USER root
RUN python setup.py install
USER hacker

RUN mkdir /home/hacker/tools-for-exploiting-webapps/
WORKDIR /home/hacker/tools-for-exploiting-webapps/
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .


WORKDIR /home/hacker/tools-for-exploiting-webapps/
EXPOSE 5000
CMD python server/run.py