Clone the repo go to backend folder and run the following command in your terminal

#pip install -r requirements.txt

if pip not work try this command

#pip install -r requirements.txt --breaks-system-packages


#create .env file and add the following lines
SECRET_KEY=##########
MONGO_URI=###########

#uvicorn app.main:app --reload

And you are good to go . You can access the API at https://localhost:8000/

