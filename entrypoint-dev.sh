#!/bin/bash

./manage.py migrate
./manage.py seed

./manage.py runserver 0.0.0.0:8000