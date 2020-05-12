from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
import random
import re
from datetime import datetime, timedelta
import pytz
from flask import Flask
import urllib.request
from fuzzywuzzy import fuzz

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
    interaction_date = db.Column(db.DateTime, default = datetime.now(), nullable=False)
    request_key = db.Column(db.String(64000))
    counter = db.Column(db.Integer())
    tutorial_counter = db.Column(db.Integer())
@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    #extract phone number from ngrok
    number = request.values.get('From', '')
    #remove non numerical values
    cleaned_number = re.sub('[^0-9]', '', number)
    #permitted numbers
    permitted = ['27652581300','27713287062','27615304405']
    names = ['Emmanuel','Jasmine','Vusi']
    name_num = dict(zip(permitted,names))
    msg = resp.message()
    #set start and end time
    current = datetime.now()
    start = datetime.now() - timedelta(hours=23, minutes=59)
    #count interactions in last 24 hours
    total_interactions = Users.query.filter(Users.cell_number == cleaned_number).\
        filter(Users.interaction_date <= current).\
        filter(Users.interaction_date >= start).\
        filter(Users.counter == 1).count()
    #counting tutorial requests
    tutorial_interactions = Users.query.filter(Users.cell_number == cleaned_number).\
        filter(Users.interaction_date <= current).\
        filter(Users.interaction_date >= start).\
        filter(Users.tutorial_counter == 1).count()
    responded = False
    #in instances when we don't want to increment attempts
    def action_control_no_increment(output, incoming_msg):
        msg.body(output)
        user_object = Users()
        user_object.cell_number = int(cleaned_number)
        user_object.request_key = incoming_msg
        user_object.counter = 0
        user_object.tutorial_counter = 0
        db.session.add(user_object)
        db.session.commit
    #when we want to increment attempts
    def action_control(file_path, incoming_msg):
        file = urllib.request.urlopen(file_path)
        full_text = [line.decode("utf-8").replace('\n', '') for line in file]
        chall = random.choice(full_text)
        challenge = ''.join(map(str, chall))
        try:
            msg.body(challenge)
            user_object = Users()
            user_object.cell_number = int(cleaned_number)
            user_object.request_key = incoming_msg
            user_object.counter = 1
            user_object.tutorial_counter = 0
            db.session.add(user_object)
            db.session.commit()
        except:
            error = 'Sorry, we ran into a mistake somewhere, this will not be added as an attempt. Please try again'
            msg.body(error)
            user_object = Users()
            user_object.cell_number = int(cleaned_number)
            user_object.request_key = incoming_msg
            user_object.counter = 0
            user_object.tutorial_counter = 0
            db.session.add(user_object)
            db.session.commit()
    #links to articles
    def link_articles(file_path,incoming_msg):
        file = urllib.request.urlopen(file_path)
        full_text = [line.decode("utf-8").replace('\n','') for line in file]
        chall = random.choice(full_text).split('|')
        hyperlink = "{link},  Title:{text}".format(link=chall[0], text=chall[1])
        try:
            msg.body(hyperlink)
            user_object = Users()
            user_object.cell_number = int(cleaned_number)
            user_object.request_key = incoming_msg
            user_object.counter = 1
            user_object.tutorial_counter = 0
            db.session.add(user_object)
            db.session.commit()
        except:
            error = 'Sorry, we ran into a mistake somewhere, this will not be added as an attempt. Please try again'
            msg.body(error)
            user_object = Users()
            user_object.cell_number = int(cleaned_number)
            user_object.request_key = incoming_msg
            user_object.counter = 0
            user_object.tutorial_counter = 0
            db.session.add(user_object)
            db.session.commit()
    #link to tutorials
    def link_tutorials(file_path,incoming_msg,cleaned_number):
        file = urllib.request.urlopen(file_path)
        full_text = [line.decode("utf-8").replace('\n', '') for line in file]
        chall = random.choice(full_text).split('|')
        hyperlink = " {link},  Title:{text}".format(link=chall[0], text=chall[1])
        message = "Hi {}, here is your tutorial: ".format(name_num.get(cleaned_number))
        try:
            msg.body(message+hyperlink)
            user_object = Users()
            user_object.cell_number = int(cleaned_number)
            user_object.request_key = incoming_msg
            user_object.counter = 1
            user_object.tutorial_counter = 1
            db.session.add(user_object)
            db.session.commit()
        except:
            error = 'Sorry, we ran into a mistake somewhere, this will not be added as an attempt. Please try again'
            msg.body(error)
            user_object = Users()
            user_object.cell_number = int(cleaned_number)
            user_object.request_key = incoming_msg
            user_object.counter = 0
            user_object.tutorial_counter = 0
            db.session.add(user_object)
            db.session.commit()
    #when out of attempts
    def action_else(num):
        output = 'Unfortunately, for costing reasons we currently cap the number of requests to {} every 24 hours. We are happy about your enthusiasm in learning how to code. Maybe you should consider enrolling into your Introduction to Data Science course?. Visit our typeform to presign up: https://techmentor.typeform.com/to/PpUG1P'.format(num)
        msg.body(output)
    #when user is not registered
    def not_registered():
        output = 'Your number {} has not been registered to access this. These are keywords currently available for users registered in our Introduction to Data Science class. Email emmanuels@thegradientboost.com if you are incorrectly receiving this message.'.format(cleaned_number)
        msg.body(output)
    if fuzz.ratio(incoming_msg, 'help') >= 90:
        output = "This is a chatbot designed to send statistics and probabiliy, numpy, web scraping, object oriented programming, list comprehension and other programming concepts that will help you further develop your programming and statistical skills. " \
                 "If you are stuck on something feel free to drop a Slack message in the whatsapp channel to get guidance from either a learning peer or one of our mentors. " \
                 "You can type the keywords: 'python easy', 'python intermediate', 'python advanced' or 'stats probability' for coding challenges. Note: you can only send 5 requests per 24 hour period. You can also type in 'attempts' to find out how many attempts you have made, 'help' to re-read this message, 'the gradient boost' to learn more about our bootcamp, 'keywords' to get a list of available keywords, 'site' to get a link to our site, 'blog' to get the url to our blog for interesting articles we have written on our bootcamp , 'twitter' or 'facebook'  to visit our Twitter and Facebook pages for updates. Typing these keywords will not increase your attempts. Remember programming is all about practise, the more you keep trying the better you will develop your skills. You can also type in contact details to get our email address."
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if fuzz.ratio(incoming_msg, 'keywords') >= 90:
        output = "Currently accepted keywords are: 'python easy', 'python intermediate','python advanced' to get programming challenges, 'stats probability' to get stats challenges, 'learn' to get an interesting link to either receive an article, tutorial or podcast on a particular concept in machine learning or data science in general, 'the gradient boost' to learn more about our online data science school, 'blog' to visit our blog, 'linkedin','facebook' or 'twitter' to visit our social media channels, 'signup' to get a link to enroll in our Introduction to Data Science course"
    if fuzz.ratio(incoming_msg, 'number') >= 90:
        output = str(cleaned_number)
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if fuzz.ratio(incoming_msg, 'python easy') >= 90:
        if total_interactions < 5:
            file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/python_test.txt"
            action_control(file_path=file_path, incoming_msg=incoming_msg)
            responded = True
        else:
            action_else(num=5)
            responded = True
    if fuzz.ratio(incoming_msg, 'python intermediate') >= 90:
        if total_interactions < 5:
            file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/python_medium.txt"
            action_control(file_path=file_path, incoming_msg=incoming_msg)
            responded = True
        else:
            action_else(num=5)
            responded = True
    if fuzz.ratio(incoming_msg, 'python advanced') >= 90:
        if total_interactions < 5:
            file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/advanced.txt"
            action_control(file_path=file_path, incoming_msg=incoming_msg)
            responded = True
        else:
            action_else(num=5)
            responded = True
    if fuzz.ratio(incoming_msg, 'stats probability') >= 90:
        if total_interactions < 5:
            file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/statistics_probability.txt"
            action_control(file_path=file_path, incoming_msg=incoming_msg)
            responded = True
        else:
            action_else(num=5)
            responded = True
    if fuzz.ratio(incoming_msg, 'programming data') >= 90:
        if cleaned_number in permitted and tutorial_interactions < 5:
            file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/data-programming.txt"
            action_control(file_path=file_path, incoming_msg=incoming_msg)
            responded = True
        else:
            action_else(num=5)
            responded = True
    if fuzz.ratio(incoming_msg, 'tutorial') >= 90:
        if cleaned_number in permitted:
            if tutorial_interactions < 2:
                file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/automate-tutorials.txt"
                link_tutorials(file_path=file_path,incoming_msg=incoming_msg, cleaned_number=cleaned_number)
                responded = True
            else:
                action_else(num=2)
                responded = True
        else:
            not_registered()
            responded = True
    if fuzz.ratio(incoming_msg, 'learn') >= 90:
        if total_interactions < 5:
            file_path = "https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/reading.txt"
            link_articles(file_path=file_path,incoming_msg=incoming_msg)
            responded = True
        else:
            action_else(num=5)
            responded = True
    if fuzz.ratio(incoming_msg, 'the gradient boost') >= 90:
        url = 'https://raw.githubusercontent.com/EmmS21/GradientBoostIntrotoDS/master/Challenges/welcome.txt'
        file = urllib.request.urlopen(url)
        full_text = [line.decode("utf-8") for line in file]
        file_read = ''.join(map(str, full_text))
        msg.body(file_read)
        user_object = Users()
        user_object.cell_number = int(cleaned_number)
        user_object.request_key = incoming_msg
        user_object.counter = 0
        user_object.tutorial_counter = 0
        db.session.add(user_object)
        db.session.commit()
        responded = True
    if 'site' in incoming_msg:
        output = 'http://thegradientboost.com/'
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if 'signup' in incoming_msg:
        output = 'http://thegradientboost.com/accounts/signup/student/'
        action_control_no_increment(output=output,incoming_msg=incoming_msg)
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
    if 'linkedin' in incoming_msg:
        output = 'https://www.linkedin.com/company/37551624'
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
    if 'attempts' in incoming_msg:
        output = str(total_interactions)
        msg.body(output)
        responded = True
    if fuzz.ratio(incoming_msg, 'contact details') >= 90:
        output = 'emmanuels@thegradientboost.com'
        action_control_no_increment(output=output, incoming_msg=incoming_msg)
        responded = True
    if not responded:
        msg.body("The phrase '{}' is currently not recognised by this app. I currently only know how to respond to the key words: 'the gradient boost', 'python easy', 'python intermediate', 'python advanced', 'stats probability', 'contact details', 'attempts', 'learn', 'signup', 'help' and 'site'. In the near future I will be able to send notifications regarding assignments and projects and Data Science interview tips from recruiters to students enrolled in The Gradient Boost online school.".format(incoming_msg))
        user_object = Users()
        user_object.cell_number = int(cleaned_number)
        user_object.request_key = incoming_msg
        user_object.counter = 0
        user_object.tutorial_counter = 0
        db.session.add(user_object)
        db.session.commit()
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
