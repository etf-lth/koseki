import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, filename='koseki.log')
import reverse
from db.storage import Storage
from koseki.db.types import Person, Group, PersonGroup
from flask import Flask
from flask.ext.babel import Babel
app = Flask(__name__)
app.config.from_pyfile('../koseki.cfg')
storage = Storage('mysql://%s:%s@%s/%s' % (app.config['DB_USER'], app.config['DB_PASSWORD'], app.config['DB_HOST'], app.config['DB_DATABASE']))
babel = Babel(app)

import koseki.core
from koseki.views import *
from koseki.plugins import *
import os

from apscheduler.scheduler import Scheduler
sched = Scheduler()

import koseki.update

def run_koseki():
    #if storage.session.query(Person).count() < 1:
    #    storage.add(Person(fname='Fredrik', lname='Ahlberg',
    #        email='fredrik@z80.se', password='10e21d1b794002ca4113540e3605a8c461d61474'))
    #    storage.add(Group(name='admin', descr='System Administrator'))
    #    storage.add(Group(name='enroll', descr='Allow enrolling new members'))
    #    storage.add(Group(name='accounter', descr='Allow registering fees'))
    #    storage.add(Group(name='board', descr='Allow enrolling and browsing'))
    #    storage.add(PersonGroup(uid=1, gid=1))
    #    storage.commit()

    sched.start()
    app.secret_key = os.urandom(24)
    app.wsgi_app = reverse.ReverseProxied(app.wsgi_app)
    app.run()

__all__ = ['run_koseki']
