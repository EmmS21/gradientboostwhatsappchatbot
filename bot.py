from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
import random
import re
from datetime import datetime, timedelta
import pytz
from flask import Flask
import urllib.request

app = Flask(__name__)
db = SQLAlchemy(app)
#connect to mysql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql3329289:rPjlLCL7kp@sql3.freemysqlhosting.net:3306/sql3329289'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#creating mapping to database
class Users(db.Model):
    __tablename__ = 'users'
    cell_number = db.Column(db.Integer, primary_key = True)
    interaction_date = db.Column(db.DateTime, default = datetime.now(pytz.timezone('Africa/Harare')), nullable=False)
    request_key = db.Column(db.String(64000))
    counter = db.Column(db.Integer())
@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    #extract phone number from ngrok
    number = request.values.get('From', '')
    #remove non numerical values
    cleaned_number = re.sub('[^0-9]', '', number)
    msg = resp.message()
    #set start and end time
    current = datetime.now(pytz.timezone('Africa/Harare'))
    start = datetime.now(pytz.timezone('Africa/Harare')) - timedelta(hours=23, minutes=59)
    #count interactions in last 24 hours
    total_interactions = Users.query.filter(Users.cell_number == cleaned_number).\
        filter(Users.interaction_date <= current).\
        filter(Users.interaction_date >= start).\
        filter(Users.counter == 1).count()
    responded = False
    #in instances when we don't want to increment attempts
    def action_control_no_increment(output, incoming_msg):
        msg.body(output)
        user_object = Users()
        user_object.request_key = incoming_msg
        db.session.add(user_object)
        db.session.commit
    #when we want to increment attempts
    def action_control(file_path, incoming_msg):
        file = urllib.request.urlopen(url)
        full_text = [line.decode("utf-8").replace('\n', '') for line in file]
        chall = random.choice(full_text)
        challenge = ''.join(map(str, chall))
        msg.body(challenge)
        user_object = Users()
        user_object.cell_number = int(cleaned_number)
        user_object.request_key = incoming_msg
        user_object.counter = 1
        db.session.add(user_object)
        db.session.commit()
    #when out of attempts
    def action_else():
        output = 'Unfortunately, for costing reasons we currently cap the number of requests to 5 every 24 hours. We are happy about your enthusiasm in learning how to code. Maybe you should consider enrolling into your Introduction to Data Science course?. Visit our typeform to presign up: https://techmentor.typeform.com/to/PpUG1P'
        msg.body(output)
    if 'help' in incoming_msg:
        output = "This is a chatbot designed to send statistics and probabiliy, numpy, web scraping, object oriented programming, list comprehension and other programming concepts that will help you further develop your programming and statistical skills. " \
                 "If you are stuck on something feel free to drop a Slack message in the whatsapp channel to get guidance from either a learning peer or one of our mentors. " \
                 "You can type the keywords: 'python-easy', 'python-intermediate', 'python-advanced' or 'stats-probability' for coding challenges. Note: you can only send 5 requests per 24 hour period. You can also type in 'attempts' to find out how many attempts you have made, 'help' to re-read this message, 'the-gradient-boost' to learn more about our bootcamp, 'site' to get a link to our site, 'blog' to get the url to our blog for interesting articles we have written on our bootcamp , 'twitter' or 'facebook'  to visit our Twitter and Facebook pages for updates. Typing these keywords will not increase your attempts. Remember programming is all about practise, the more you keep trying the better you will develop your skills. You can also type in contact-details to get our email address."
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if 'number' in incoming_msg:
        output = str(cleaned_number)
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if 'python-easy' in incoming_msg:
        if total_interactions <= 5:
            file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/python_test.txt"
            action_control(file_path=file_path, incoming_msg=incoming_msg)
            responded = True
        else:
            action_else()
            responded = True
    if 'python-intermediate' in incoming_msg:
        if total_interactions <= 5:
            file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/python_medium.txt"
            action_control(file_path=file_path, incoming_msg=incoming_msg)
            responded = True
        else:
            action_else()
            responded = True
    if 'python-advanced' in incoming_msg:
        if total_interactions <= 5:
            file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/advanced.txt"
            action_control(file_path=file_path, incoming_msg=incoming_msg)
            responded = True
        else:
            action_else()
            responded = True
    if 'stats-probability' in incoming_msg:
        if total_interactions <=5:
            file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/statistics_probability.txt"
            action_control(file_path=file_path, incoming_msg=incoming_msg)
            responded = True
        else:
            action_else()
            responded = True
    if 'the-gradient-boost' in incoming_msg:
        url = 'https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/welcome.txt'
        file = urllib.request.urlopen(url)
        full_text = [line.decode("utf-8") for line in file]
        file_read = ''.join(map(str, full_text))
        msg.body(file_read)
        user_object = Users()
        user_object.cell_number = int(cleaned_number)
        user_object.request_key = incoming_msg
        user_object.counter = 0
        db.session.add(user_object)
        db.session.commit()
        responded = True
    if 'site' in incoming_msg:
        output = 'http://thegradientboost.com/'
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if 'blog' in incoming_msg:
        output = 'https://medium.com/gradientboost'
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if 'twitter' in incoming_msg:
        output = 'https://twitter.com/gradient_the'
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if 'facebook' in incoming_msg:
        output = 'https://www.facebook.com/thegradientboost'
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if 'attempts' in incoming_msg:
        output = str(total_interactions)
        msg.body(output)
        responded = True
    if 'contact-details' in incoming_msg:
        output = 'emmanuel@thegradientboost.com'
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if not responded:
        msg.body("The phrase '{}' is currently not recognised by this app. I currently only know how to respond to the key words: 'the-gradient-boost', 'python-easy', 'python-intermediate', 'python-advanced', 'stats-probability', 'contact-details', 'attempts', 'help' and 'site'. In the near future I will be able to send notifications regarding assignments and projects and Data Science interview tips from recruiters to students enrolled in The Gradient Boost online school.".format(incoming_msg))
        user_object = Users()
        user_object.cell_number = int(cleaned_number)
        user_object.request_key = incoming_msg
        user_object.counter = 0
        db.session.add(user_object)
        db.session.commit()
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
