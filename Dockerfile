FROM python:3

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install waitress

COPY . .

CMD ["waitress-serve", "main:app"]