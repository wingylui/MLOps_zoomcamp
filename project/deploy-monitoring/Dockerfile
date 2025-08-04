FROM python:3.9.7-slim

RUN pip install -U pip
RUN pip install pipenv 

WORKDIR /app

COPY [ "./flask_app/Pipfile", "./flask_app/Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

COPY [ "./flask_app/predict.py", "./model/artifacts/model.pkl", "./" ]

EXPOSE 9696

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app" ]
