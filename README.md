## Be Social App

This is a basic social networking application built using django framework. Postman collection is added to the repository.

### API Endpoints

- /auth/login - provides auth token and refresh token
- /auth/signup - used for registering to the application by providing firstname, lastname, email and password
- /connections/search - used for searching all the users in the application given the search term
- /connections/create - sends connection request to others
- /connections - lists all friends
- /connections?status=P - list all pending requests
- /connections/<connection_id> - for accpeting / rejecting connection request

### Tech Stack

- Django
- Postgresql

### Installing Dependencies

`pip install -R requirements.txt`

### Running Test

This is developed using the TDD approach. To execute the unit testcases, execute the following command

`python manage.py test --parallel`

### Running application in local

`python manage.py runserver 8080`

### Running the Application

Docker file and docker compose file are available. Execute the following command to run application in docker

`docker compose up -d --build`
