#!/bin/bash

# Set IGG Environment Variable
if [ "`hostname`" != "bunda" ]
then
	echo "FOO"
	IGG_ENV='dev'
	export IGG_ENV
fi

./src/manage.py $@

