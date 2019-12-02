import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, filename='koseki.log')
from . import reverse
from .db.storage import Storage
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
    with app.app_context():
        if storage.session.query(Person).count() < 1:
            storage.add(Person(uid=1, fname='Test', lname='Testsson',
                email='test@example.com', password='5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8')) # pass: password
            storage.add(PersonGroup(uid=1, gid=1))
            storage.commit()
        sched.start()
        app.secret_key = os.urandom(24)
        app.wsgi_app = reverse.ReverseProxied(app.wsgi_app)
        app.run()

__all__ = ['run_koseki']
