FROM parsertongue/python:3.8

LABEL author="enoriega"
LABEL description="Image definition for Python-based AZX project."

WORKDIR /app/

COPY . .

RUN chmod u+x scripts/* && \
    mv scripts/* /usr/local/bin/ && \
    rmdir scripts

RUN apt-get -y update && \
    apt-get -y upgrade

RUN pip install -U pip

RUN pip install .

EXPOSE 9999

CMD ["launch-notebook"]