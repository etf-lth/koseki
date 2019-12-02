from koseki import app, storage, babel
from flask import url_for, render_template, session, redirect, escape, request, abort, jsonify
from flask.ext.babel import format_datetime
from koseki.db.types import Person, Group
import re
import hashlib
from sqlalchemy import or_
import logging
import time
import datetime

@app.context_processor
def make_nav_processor():
    def make_nav():
        return session['nav']
    return dict(make_nav=make_nav)

@app.context_processor
def now_processor():
    def now():
        return datetime.datetime(2000,1,1).fromtimestamp(time.time())
    return dict(now=now)

navigation = []

def nav(uri, icon, title, weight = 0, groups=None):
    navigation.append({
        'uri': uri,
        'icon': icon,
        'title': title,
        'groups': groups,
        'weight': weight
        })

    def nop(f):
        return f
    return nop

def calc_nav():
    nav = []
    
    for n in navigation:
        if n['groups'] is None or sum(1 for group in n['groups'] if member_of(group)):
            nav.append(n)

    session['nav'] = sorted(nav, key=lambda x: x['weight'])

@app.context_processor
def gravatar_processor():
    def gravatar(mail):
        return '//gravatar.com/avatar/' + hashlib.md5(mail.encode('utf-8')).hexdigest()
    return dict(gravatar=gravatar)

@app.template_filter('date')
def format_date(value, format='y-MM-dd'):
    return format_datetime(value, format)

@app.context_processor
def uid_to_name():
    def uid_to_name_inner(uid):
        person = storage.session.query(Person).filter_by(uid=uid).scalar()
        return "%s %s" % (person.fname, person.lname) if person else "Nobody"
    return dict(uid_to_name=uid_to_name_inner)

def member_of(group, person = None):
    if person is None:
        person = current_user()
    if type(person) in (int, int):
        person = storage.session.query(Person).filter_by(uid=person).scalar()
    if type(group) == int:
        group = storage.session.query(Group).filter_by(gid=group).scalar()
    elif type(group) == str:
        group = storage.session.query(Group).filter_by(name=group).scalar()
    return sum(1 for x in person.groups if x.gid == group.gid)

def current_user():
    return session['uid']

def start_session(uid):
    session['uid'] = int(uid)
    calc_nav()

def destroy_session():
    session.pop('uid', None)

@app.context_processor
def member_of_processor():
    return dict(member_of=member_of)

class require_session(object):

    def __init__(self, groups=None):
        #print 'init', f
        #self.f = f
        #self.__name__ = f.__name__
        self.groups = groups

    def __call__(self, f):
        def wrap(*args, **kwargs):
            if not 'uid' in session:
                return redirect(url_for('login', redir=request.base_url))
            else:
                if self.groups is None or sum(1 for group in self.groups if member_of(group)):
                    return f(*args, **kwargs)
                else:
                    abort(403)
        wrap.__name__ = f.__name__
        return wrap

    #def __call__(self, *args, **kwargs):

#def require_session(groups=None):
#    def wrap(f):
#        def wrapped_f(*args, **kwargs):
#            print 'call', self.f, args, self.groups
#            if not 'username' in session:
#                print 'no session'
#                return redirect(url_for('login', redir=request.path))
#            else:
#                print 'username is', session['username']
#                return f(*args, **kwargs)
#        return wrapped_f
#    return wrap

global alt_login; alt_login = None

def get_alternate_login():
    global alt_login
    return alt_login

def alternate_login(alt):
    global alt_login
    alt_login = alt()
    logging.info('Registered alternate login provider: %s' %alt_login)

@app.route('/api/ac/members')
@require_session(['admin','accounter','board'])
def api_ac_members():
    term = request.args.get('term','')
    members = storage.session.query(Person).filter(or_(Person.fname.like(term+'%%'), Person.lname.like(term+'%%'))).all()
    return jsonify(data=[{'label':'%s %s' % (p.fname, p.lname), 'value': p.uid} for p in members])
