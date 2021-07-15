FROM python:3

RUN mkdir -p /opt/src/tests
WORKDIR /opt/src/tests

COPY tests/authenticationTests.py ./authenticationTests.py
COPY tests/data.py ./data.py
COPY tests/requirements.txt ./requirements.txt
COPY tests/electionTests.py ./electionTests.py
COPY tests/main.py ./main.py
COPY tests/participantTests.py ./participantTests.py
COPY tests/utilities.py ./utilities.py
COPY tests/voteTests.py ./voteTests.py
COPY tests/temp.csv ./temp.csv


#instaliranje modula dodajemo putanju do requirements
RUN pip install -r ./requirements.txt

#dodaj ako uvozis svoje fajlove i imas poddirektorijume
ENV PYTHONPATH="opt/src"

ENTRYPOINT ["python","./application.py"]