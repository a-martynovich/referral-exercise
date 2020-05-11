# Amitree Take Home Technical Challenge

## Implementation
The server is written in Python37/Django. It uses PostgreSQL for storing data and Bootstrap for fancy forms and cards.
Tests are in `referral_sample/tests.py`.

### Execution
One way to execute the code is to build a Docker container with the supplied Dockerfile. It has everything needed for 
running the code and it runs automatically. And it's the same container which is going to run in Google Cloud once 
deployed.

Another way is to run the Python code directly, without building Docker image. Simply install the dependencies, set 
Postgres connection options, and run the server:
```
# install dependencies
pip3 install -r requirements.txt

# set Postgres connection options
export DB_NAME=<database name>
export DB_USER=<Postgres username>
export DB_PASSWORD=...
export DB_HOST=<Postgres IP address>
export DB_PORT=<Postgres port>

# Run the server
python3 manage.py runserver
# or 
gunicorn --bind :8000 referral_sample.wsgi
```  

In both cases the server should be running at port 8000.

### Deployment
```
# Create Google Storage bucket (if needed)
gsutil mb gs://[BUCKET_NAME]
gsutil defacl set public-read gs://[BUCKET_NAME]

# Upload static files (media, scripts, styles) to Google Storage
python manage.py collectstatic
gsutil -m rsync -r ./staticfiles gs://a-martynovich/static

# Connect CloudSQL to the server
gcloud sql instances create [INSTANCE_NAME] --tier=[MACHINE_TYPE] --region=[REGION]
gcloud run services update [INSTANCE_NAME] --platform managed \
  --add-cloudsql-instances [INSTANCE_CONNECTION_NAME] \
  --set-env-vars DB_USER=...,DB_PASSWORD=...,DB_NAME=...,\
        DB_HOST=/cloudsql/[CONNECTION_STRING]

# Connect to CloudSQL and set up the database (if needed):
gcloud sql connect [CONNECTION_STRING]
# or
cloud_sql_proxy -instances="[CONNECTION_STRING]"=tcp:3306
psql postgres -d postgres://localhost:3306/
postgres=> create database "[DATABASE_NAME]";

# Build and submit the server image
gcloud builds submit --tag gcr.io/[PROJECT_ID]/django-test
gcloud run deploy --image gcr.io/[PROJECT_ID]/django-test --platform managed
```
The server should be running immediately after deployment. It is possible to automate deployment using CI/CD, for 
example CircleCI which integrates with Github.

### Usage
The server-rendered UI is self-explanatory. It is also possible to use all endpoints as AJAX API (in a React SPA for 
example). One common requirement is to set header `Accept: application/json`. For POST requests it is also necessary to 
set `X-CSRFToken` header to the value of CSRF token written in cookies. Here's an example of using the `/` endpoint with 
Javascript Fetch API:
```
fetch('http://localhost:8000', {
    headers: {'Accept': 'application/json'}}
);
```
If the user is authorized this request will respond with a JSON object containing two fields: 
"referral_link" and "balance".

Here's how to login with a POST request:
```
fetch('http://localhost:8000/login/', {
    headers: {
        'Accept': 'application/json',
        "X-CSRFToken": getCookie('csrftoken'),
        "Content-type": "application/x-www-form-urlencoded"
    },
    method: 'POST',
    body: "username=...&password=..."
});
```
The function `getCookie()` looks for a value of the cookie. One may use a helper library to read cookies or write this 
code from scratch.

The server provides session-based authorization. 

### Endopints
* `/signup[?ref=...]` 

   Sign up (create a new user). Supply referral token if needed. 
   The required fields (username, password1, password2) should be www-form-urlencoded and supplied in the body.
    
   Response: 200 and `{}` on success, or 40x and `{field: error}`.
* `/login`

   Log in. Will authorize the session. In non-AJAX mode will redirect to root page after successful login, or display 
   errors otherwise.
   
   Response: 200 and `{}` on success, or 40x and `{field: [errors]}`.
* `/logout`

   Log out. Deauthorize the session. In non-AJAX mode will display logout message and redirect to login page.

   Response: 200 and `{}` on success. No failures expected except for general server failures.
* `/`

   The "main" page. In non-AJAX mode displays user info (balance and referral link). In AJAX mode returns those values 
   in JSON format.
   
   Response: 200 and `{}` on success, or 401 and `{error: unauthorized}`.

