FROM python:3.8
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get -y install firefox-esr-l10n-ru

RUN mkdir -p usr/src/app/
WORKDIR usr/src/app/

COPY . .
COPY /zakupki/drivers/linux/geckodriver /usr/local/bin
RUN pip install --no-cache-dir -r requirements.txt

ENV TZ Europe/Moscow
