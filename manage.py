#!/bin/sh

# Set IGG Environment Variable
IGG_ENV='dev'
export IGG_ENV

./src/manage.py $@

