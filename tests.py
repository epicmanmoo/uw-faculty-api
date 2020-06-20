import requests
import random

'''
THE API FOLLOWS THIS ORDER FOR GET REQUESTS:
DESCRIPTION, EMAIL(S), NAME, PHONES(S)
'''


def get_phone(name):
    r = requests.get('http://www.uwfaculty-lmao.tk/faculty/api/v1/' + name)
    faculty = r.json()
    bad_req = False
    phone = ''
    error = ''
    try:
        error = faculty['error']
        bad_req = True
    except Exception:
        phone = faculty['teacher'][0]['phone']  # returns first teacher's phone number.
        # there could be multiple in the request however
    if bad_req:
        return error
    else:
        return phone


def get_random(page):
    details = []
    r = requests.get('http://www.uwfaculty-lmao.tk/faculty/api/v1/allfaculty/' + str(page))
    everyone = r.json()
    try:
        int(page)
    except ValueError:
        return 'Bad Request'
    if int(page) <= 0 or int(page) > 8:
        return 'Bad Request'
    else:
        rand_faculty = everyone['db'][random.randint(0, len(everyone['db']) - 1)]
        for attributes in rand_faculty:
            details.append(rand_faculty[attributes])
        return details


def get_complete_random():
    details = []
    r = requests.get('http://www.uwfaculty-lmao.tk/faculty/api/v1/allfaculty/' + str(random.randint(1, 8)))
    everyone = r.json()
    rand_faculty = everyone['db'][random.randint(0, len(everyone['db']) - 1)]
    for attributes in rand_faculty:
        details.append(rand_faculty[attributes])
    return details


def exists(name):
    r = requests.get('http://www.uwfaculty-lmao.tk/faculty/api/v1/' + name)
    faculty = r.json()
    bad_req = False
    exist = False
    try:
        error = faculty['error']
        bad_req = True
    except Exception:
        exist = True  # there could be multiple people with the same name but the point is that they exist
        # (that's the purpose of this function.) Of course, you could check each faculty member in here as well
        # if your request is not so specific. I.E. if your request is http://www.uwfaculty-lmao.tk/faculty/api/v1/tea
        # then all faculty whose name starts with tea is returned. They exist, sure, but maybe you wanted different
        # results. Implement this as desired.
    if bad_req:
        return exist
    else:
        return exist


def get_uw_school_email(name):
    r = requests.get('http://www.uwfaculty-lmao.tk/faculty/api/v1/' + name)
    faculty = r.json()
    school_email = ''
    try:
        error = faculty['error']
        bad_req = True
    except Exception:
        school_email = faculty['teacher'][0]['email']
        if isinstance(school_email[0], list):
            return school_email[0][0]  # we know that this is a list. It returns first faculty's first email.
        # First email is always the uw email (by default). Need to specify to get the list's first index
        # since other index's may hold other email such as 'gmail' for the specific faculty.
        else:
            return school_email[0]  # simply return first index since we know only one index exists
    if bad_req:
        return error
    else:
        return school_email


print(get_phone('Dong Si'))
print(get_phone('Ana Mari Cauce'))
print(get_phone('Ben Aaronson'))
print(get_phone('Woof woof'))
print(get_random('a'))
print(get_random(2))
print(get_random(5))
print(get_random(1))
print(get_random(9))
print(get_random(0))
print(get_complete_random())
print(get_complete_random())
print(get_complete_random())
print(exists('Frederick R. Appelbaum'))
print(exists('Jared Baeten'))
print(exists('Cats are cute'))
print(get_uw_school_email('Nikolaos Pappas'))
print(get_uw_school_email('Bunnies are cool too'))
print(get_uw_school_email('Michael W Passer'))



