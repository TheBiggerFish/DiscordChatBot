FROM python:3.8.10

ENV HOME /chatbot
ENV CONFIG_PATH ${HOME}/config.yml

COPY . ${HOME}
WORKDIR ${HOME}

RUN pip install --upgrade pip
RUN pip install -e .

CMD ["python","src/main.py"]
