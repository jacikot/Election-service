FROM python:3

RUN mkdir -p /opt/src/elections
WORKDIR /opt/src/elections

ENV TZ 'Europe/Amsterdam'
RUN echo $TZ > /etc/timezone && \
apt-get update && apt-get install -y tzdata && \
rm /etc/localtime && \
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
dpkg-reconfigure -f noninteractive tzdata && \
apt-get clean


COPY elections/admin/application.py ./application.py
COPY elections/admin/configuration.py ./configuration.py
COPY elections/models.py ./elections/models.py
COPY requirements.txt ./requirements.txt
COPY roleDecorater.py ./roleDecorater.py

#instaliranje modula dodajemo putanju do requirements
RUN pip install -r ./requirements.txt

#dodaj ako uvozis svoje fajlove i imas poddirektorijume
ENV PYTHONPATH="opt/src/"

ENTRYPOINT ["python","./application.py"]