FROM python:3.8

# set a directory for the app
WORKDIR /usr/src/app_fronted

# copy all the files to the container
COPY . .

ARG twitter_api_token
ENV twitter_api_var=$twitter_api_token

# install dependencies
RUN --mount=type=cache,target=/root/.cache/pip pip -q install -r requirements.txt

# define the port number the container should expose
EXPOSE 8050

# run the command
CMD ["gunicorn"  , "--bind", "0.0.0.0:8050", "app_multi:server"]

