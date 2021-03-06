FROM duplocloud/shell:sso_v1

ENV DEBIAN_FRONTEND=noninteractive
#Terraform v0.12.24
ENV TERRAFORM_VERSION=0.12.24

RUN apt-get update && apt-get upgrade -y && apt-get clean
RUN apt-get install -y python-pip
RUN pip install awscli

RUN apt-get update \
  && apt-get install -y wget vim unzip curl jq bash ca-certificates git openssl unzip wget \
  && cd /tmp \
  && wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
  && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /usr/bin

RUN mkdir -p /duplocli
COPY . /duplocli/

WORKDIR /duplocli
RUN ls -altR .
RUN python3 -V
RUN python -V

RUN apt-get update &&  apt-get install -y graphviz
ENV PATH=/usr/local/bin/dot:$PATH
RUN pip install boto3
RUN pip install requests
RUN pip install psutil
RUN pip install graphviz
RUN pip install -r /duplocli/duplocli/terraform/requirements.txt

RUN rm -rf /tmp/* \
  && rm -rf /var/lib/apt/lists/* \
  rm -rf /var/tmp/*

RUN chmod +x /duplocli/*.sh

ENV PYTHONPATH=/duplocli

COPY shell/shell.conf /etc/supervisor/conf.d/
COPY shell/nginx-custom.conf /etc/nginx/sites-available/default
COPY shell/shell_init.sh /shell/shell_init.sh
COPY shell/shell.sh /shell/shell.sh
COPY shell/docker_init.sh /shell/docker_init.sh
COPY shell/app /shell/app
COPY shell/uwsgi.ini /etc/uwsgi/uwsgi.ini

RUN chmod +x /shell/*.sh

ENTRYPOINT [ "supervisord", "-n" ]
