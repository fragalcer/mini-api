# mini-api

To run this project make sure you run the following commands:

`docker-compose build`

`docker-compose up`

`docker-compose exec web bash`

`python manage.py migrate`

`python manage.py loaddata plans/fixtures/initial_plans_fixture.yaml`

`python manage.py createsuperuser`

To run tests just run the command below inside the container:

`python manage.py test`
