FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

ENV TZ 'Europe/Amsterdam'
RUN echo $TZ > /etc/timezone && \
apt-get update && apt-get install -y tzdata && \
rm /etc/localtime && \
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
dpkg-reconfigure -f noninteractive tzdata && \
apt-get clean

COPY authentication/migrate.py ./migrate.py
COPY authentication/configuration.py ./configuration.py
COPY authentication/models.py ./models.py
COPY requirements.txt ./requirements.txt

#instaliranje modula dodajemo putanju do requirements
RUN pip install -r ./requirements.txt

#dodaj ako uvozis svoje fajlove i imas poddirektorijume
#ENV PYTHONPATH="opt/src/ime okruzujuceg foldera"

ENTRYPOINT ["python","./migrate.py"]