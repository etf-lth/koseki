import os
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask import Flask
from koseki.db.types import Person, Group, PersonGroup
from koseki.db.storage import Storage
from . import reverse
import logging

logging.basicConfig(format='%(asctime)s %(message)s',
                    level=logging.DEBUG, filename='koseki.log')
app = Flask(__name__)
app.config.from_pyfile('../koseki.cfg')
storage = Storage('mysql://%s:%s@%s/%s' %
                  (app.config['DB_USER'], app.config['DB_PASSWORD'], app.config['DB_HOST'], app.config['DB_DATABASE']))
babel = Babel(app)
boostrap = Bootstrap(app)

import koseki.update
import koseki.core
from koseki.update import Updater

from koseki.plugins import *
from koseki.views import *

updater = Updater(app, storage)

def run_koseki():
    with app.app_context():
        if storage.session.query(Person).count() < 1:
            storage.add(Person(uid=1, fname='Test', lname='Testsson',
                               email='test@example.com', password='5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8'))  # pass: password
            storage.add(PersonGroup(uid=1, gid=1))
            storage.commit()
        updater.start()
        app.secret_key = os.urandom(24)
        app.debug = app.config['DEBUG']
        app.wsgi_app = reverse.ReverseProxied(app.wsgi_app)
        app.run()


__all__ = ['run_koseki']
