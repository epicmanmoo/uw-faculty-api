from flask import Flask, jsonify, render_template, request
from tinydb import TinyDB, Query
import re
import smtplib
from wtforms import Form, StringField, validators
from validate_email import validate_email

credentials = open('creds.txt', 'r')
sec_key = credentials.readline()
email_username = credentials.readline()
email_password = credentials.readline()


app = Flask(__name__)
app.config['SECRET_KEY'] = sec_key
t_db = TinyDB('teachers.json')
Teachers = Query()


class RequestFormToAddFaculty(Form):
    your_name = StringField('Your full name', {validators.DataRequired()})
    your_email = StringField('Your email address', [validators.DataRequired()])
    first_name = StringField('First Name of Faculty', [validators.DataRequired()])
    middle_name = StringField('Middle Name of Faculty (optional)')
    last_name = StringField('Last Name of Faculty', [validators.DataRequired()])


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/addfaculty/', methods=['GET', 'POST'])
def add_faculty():
    form = RequestFormToAddFaculty(request.form)
    if request.method == 'POST' and form.validate():
        e = form.your_email.data.strip()
        email_valid = validate_email(email=e)
        if not email_valid:
            error = 'Invalid Email'
            return render_template('addfaculty.html', form=form, error=error)
        y_n = form.your_name.data.strip()
        f_n = form.first_name.data.strip()
        m_n = form.middle_name.data.strip()
        l_n = form.last_name.data.strip()
        content = 'Their Email = ' + e + '\n' + 'Their Name = ' + y_n + '\n' + \
                  'Faculty First name = ' + f_n + '\n' + 'Faculty Middle name = ' + \
                  (m_n if m_n != "" else "N/A") \
                  + '\n' + 'Faculty Last name = ' + l_n + '\n'
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(email_username, email_password)
        mail.sendmail(email_username, email_username, content)
        mail.close()
        return '<h1> Thanks for the request. </h1>'
    return render_template('addfaculty.html', form=form)


@app.route('/faculty/api/v1/<the_name>/', methods=['GET'])
def faculty(the_name):
    req = t_db.search(Teachers.name.matches(the_name, flags=re.IGNORECASE))
    if len(req) == 0:
        return jsonify(error='Bad request')
    else:
        return jsonify(teacher=req)


@app.route('/faculty/api/v1/allfaculty/<page>/', methods=['GET'])
def all_faculty(page):
    try:
        int(page)
    except ValueError:
        return jsonify(error='Bad request')
    if int(page) > 8 or int(page) <= 0:
        return jsonify(error='Bad request')
    else:
        return jsonify(db=t_db.all()[(int(page) * 5000) - 5000:5000 * int(page)])


@app.errorhandler(404)
def page_not_found(e):
    return '<h1> What are you trying to do bro? </h1>'


if __name__ == '__main__':
    app.run()
