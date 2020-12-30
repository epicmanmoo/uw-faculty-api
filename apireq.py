from flask import Flask, jsonify, render_template, request, redirect, url_for
from tinydb import TinyDB, Query
import re
import smtplib
from wtforms import Form, StringField, validators, PasswordField
from validate_email import validate_email
import secrets
import time

f = open('sec_id.txt', 'w')
f.write(secrets.token_urlsafe(256))
f.close()
credentials = open('creds.txt', 'r')
sec_key = credentials.readline()
email_username = credentials.readline()
email_password = credentials.readline()
correct_password = credentials.readline()
credentials.close()

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


class Secret(Form):
    the_password = PasswordField('Yes?', {validators.DataRequired()})


class SelfAdd(Form):
    fac_name = StringField('Faculty Name. First, Middle (if possible), Last. This field is required.', [validators.DataRequired()])
    fac_phone = StringField('Faculty Phone Number(s). Separate each by A SINGLE SPACE. Leave field empty if needed.')
    fac_email = StringField('Faculty Email(s). Separate each by A SINGLE SPACE. Leave field empty if needed.')
    fac_description = StringField('Faculty Description. Leave field empty if needed.')


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


@app.route('/secret/omg/bruh/', methods=['GET', 'POST'])
def secret_page():
    form = Secret(request.form)
    if request.method == 'POST' and form.validate():
        password = form.the_password.data.strip()
        if password != correct_password:
            return '<h1> Nice try. </h1>'
        id_file = open('sec_id.txt', 'r')
        the_id = id_file.readline()
        id_file.close()
        return redirect(url_for('top_secret', good_id=the_id))
    return render_template('secret.html', form=form)


@app.route('/secret/omg/bruh/top_secret/<good_id>/', methods=['GET', 'POST'])
def top_secret(good_id):
    id_file = open('sec_id.txt', 'r')
    the_id = id_file.readline()
    id_file.close()
    if good_id == the_id:
        form = SelfAdd(request.form)
        if request.method == 'POST' and form.validate():
            fac_name = form.fac_name.data
            fac_phone_pre = form.fac_phone.data
            fac_phone = fac_phone_pre.split()
            fac_phone = list(filter(None, fac_phone))
            fac_email_pre = form.fac_email.data
            fac_email = fac_email_pre.split()
            fac_email = list(filter(None, fac_email))
            fac_desc = form.fac_description.data
            req = t_db.search(Teachers.name.matches(fac_name, flags=re.IGNORECASE))

            if len(req) == 0:
                t_db.insert({'name': fac_name, 'phone': fac_phone, 'email': fac_email, 'description': fac_desc})
                return '<h1> Successfully inserted ' + fac_name + '</h1>'
            else:
                t_db.update({'phone': fac_phone}, Teachers.name == fac_name)
                t_db.update({'email': fac_email}, Teachers.name == fac_name)
                t_db.update({'description': fac_desc}, Teachers.name == fac_name)
                return '<h1> Successfully Updated ' + fac_name + '</h1>'
        return render_template('selfadd.html', form=form, id=good_id)
    else:
        return '<h1> Goodbye. </h1>'


@app.errorhandler(404)
def page_not_found(e):
    return '<h1> What are you trying to do bro? </h1>'


if __name__ == '__main__':
    app.run()
