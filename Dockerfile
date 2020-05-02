FROM python:3.8.2

maintainer Alpha Man "yo@alphaman.me"

ENV APP_HOST=0.0.0.0
ENV APP_PORT=1234
ENV REDIS_URL=redis://:passwordROFL@redis:6379
ENV SECRET_KEY=updateYourSecretKeyInDockerComposeFile

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./myapp.py" ]
