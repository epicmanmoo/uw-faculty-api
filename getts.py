from tinydb import TinyDB
from bs4 import BeautifulSoup
import urllib.parse
import requests

t_db = TinyDB('teachers.json')


def insert(the_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
    }
    url = requests.get(the_url, headers=headers)
    bs = BeautifulSoup(url.content, 'html.parser')
    num_ts = bs.find('div', {'class': 'rsummary'}).text
    index = num_ts.find("Last name begins with")
    index += 26
    pos = 0
    num_ts = num_ts[index:].strip()
    for ch in num_ts:
        try:
            int(ch)
            pos += 1
        except ValueError:
            break
    final_num = int(num_ts[:pos])

    table = bs.findAll('table')[1]
    count = 0
    found = False
    for tr in table.findAll('tr'):
        for td in tr.findAll('td'):
            if "Last name begins with" in td.text.strip():
                found = True
                break
        if found:
            break
        count += 1
    count += 1
    name = ""
    phone = ""
    email = ""
    for tr in table.findAll('tr')[count:final_num]:
        pos = 0
        emails = []
        for td in tr.findAll('td'):
            if pos == 0:
                name = td.text
            elif pos == 1:
                phone = td.text
            elif pos == 2:
                two = False
                if '<br/>' in str(td):
                    the_emails = str(td).replace("<td>", "").replace("</td>", "").split('<br/>')
                    two = True
                email = td.text
                if two:
                    emails.append(the_emails)
                else:
                    emails.append(email)
            pos += 1
            if pos == 3:
                phones = []
                if len(phone) > 12:
                    c = len(phone) / 12
                    if c.is_integer():
                        c = int(c)
                        start = 0
                        end = 12
                        for ph in range(0, c):
                            phones.append(phone[start:end])
                            start += 12
                            end += 12
                if len(phones) == 0:
                    phones.append(phone)
                appropriate_name = urllib.parse.quote(name)
                desc_url = 'https://www.washington.edu/home/peopledir/?method=name&term=' + appropriate_name + '&length=full'
                url.close()
                try:
                    url2 = requests.get(desc_url, headers=headers)
                except Exception:
                    continue
                bs2 = BeautifulSoup(url2.content, 'html.parser')
                try:
                    desc = bs2.find('ul', {'class': 'multiaddr'}).find('li').text
                except AttributeError:
                    try:
                        desc = bs2.find('li', {'class': 'title_1'}).text
                    except Exception:
                        desc = ""
                url2.close()
                t_db.insert({'name': name, 'phone': phones, 'email': emails, 'description': desc})


for alpha in range(0, 26):
    insert('https://www.washington.edu/home/peopledir/?method=name&term=' + chr(alpha + 65) + '&length=summary')
