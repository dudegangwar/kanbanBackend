#! /bin/sh
echo "======================================================================================="
echo "Welcome to the setup. This will setup the local virtual env."
echo "And then it will install all the required python libraries."
echo "You can return this without any issues."
echo "---------------------------------------------------------------------------------------"
if [ -d ".env" ];
then
   echo "Enabling virtual env"
else
   echo "No Virtual env. Please run setup.sh first"
   exit N
fi

#Activate virtual env
. .env/Scripts/activate
export ENV=development
# pip install gevent

celery -A main.celery worker --pool=solo -l info

deactivate