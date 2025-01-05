#!/bin/sh

./wait-for db:3306

python app.py --host=0.0.0.0
