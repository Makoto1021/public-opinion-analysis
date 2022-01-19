# Analysis of public opinions for politicians
### Video Demo:  <https://youtu.be/xaUhVlViFYM>
### Description:

If you are a politician, this is the perfect tool for further your political career. In this application, you can see public sentiment towards politicians in Japan's National Diet. You, as a politician, can monitor how people are reacting to your job on a daily basis. Today's politics is not only about attending as many meetings as possible to make themselves known to the public. Politicians are required to adjust and improve their manifesto by analyzing people's reaction. This website provides the politicians with power to better understand public, by leveraging the technology of Natural Language Processing.

### Composition

#### environments
It requires python3.8. Run `pip install -r requirements.txt` to create a virtual environment.

#### main.py
This main.py is a scraper and analyzer of the tweets. It reads the credentials stored in `credentials_v2.yaml` and collects tweets about the given politicians during a specified day. It sotres the results in a table `tweets_processed` on a postgresql database.

#### application.py
It is a python script with flask framework. In order to see the application, run the command `export FLASK_APP=application.py; flask run` in your terminal. 

### Usage
##### Register as a user
If you are visiting this website for the first time, you need to register as a user. Follow the instructions on the screen.

##### Login as a user
If you are an already registered user, you can log in by providing a user name and a password.

##### Daily analysis
You can pick up a date and visualize the sentiment of the people tweeting about you. From here you can see how people are reacting to your day-to-day job. In the future release, we will add a fuctionality to visualize the topics with associated sentiments.

##### Historical analysis
You can visualize the evolution of public sentiments for each politicians that you select from the dropdown menu. You can select multiple politicians at the same time for a comparison.

###### Notes
This is a minimal viable product for my analysis of public opinion for politicians. We are continuously improving this tool. Our roadmap includes:
- adding more politicians in our analysis scope
- including wordclouds as part of the daily analysis
- adding topic-aspect sentiment analysis to provide deeper insights on the public reaction
- ...