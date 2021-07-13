FROM python:3

RUN mkdir -p /opt/src/elections
WORKDIR /opt/src/elections

COPY elections/daemon/application.py ./application.py
COPY elections/daemon/configuration.py ./configuration.py
COPY elections/models.py ./elections/models.py
COPY requirements.txt ./requirements.txt

#instaliranje modula dodajemo putanju do requirements
RUN pip install -r ./requirements.txt

#dodaj ako uvozis svoje fajlove i imas poddirektorijume
ENV PYTHONPATH="opt/src"

ENTRYPOINT ["python","./application.py"]