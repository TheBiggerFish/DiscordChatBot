FROM python:3.8.10
EXPOSE 6463-6472
COPY . .
RUN pip install --upgrade pip
RUN pip install -e .
RUN echo "Installation finished"

COPY . /chatbot/
WORKDIR /chatbot/
CMD ["python","src/main.py"]
