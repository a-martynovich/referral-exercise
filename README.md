```
gcloud builds submit --tag gcr.io/artem-252303/django-test
gcloud run deploy --image gcr.io/artem-252303/django-test --platform managed

gsutil mb gs://a-martynovich
gsutil defacl set public-read gs://a-martynovich

python manage.py collectstatic
gsutil -m rsync -r ./staticfiles gs://a-martynovich/static

gcloud sql instances create [INSTANCE_NAME] --tier=[MACHINE_TYPE] --region=[REGION]
gcloud run services update [INSTANCE_NAME] \
  --add-cloudsql-instances [INSTANCE_CONNECTION_NAME] \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME=[INSTANCE_CONNECTION_NAME],\
  DB_USER=postgres,DB_PASS=[DATABASE_USER_PASSWORD],DB_NAME=guestbook
gcloud run services update django-test --add-cloudsql-instances artem-252303:europe-north1:django-test
gcloud run services update django-test --platform managed --set-env-vars DB_USER=postgres,DB_PASS=grimuwya,DB_NAME=django-test,DB_HOST=/cloudsql/artem-252303:europe-north1:django-test

# Connect to CloudSQL:
gcloud sql connect artem-252303:europe-north1:django-test
# or
cloud_sql_proxy -instances="artem-252303:europe-north1:django-test"=tcp:3306
psql postgres -d postgres://localhost:3306/
postgres=> create database "django-test";
```