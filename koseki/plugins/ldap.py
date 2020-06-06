from koseki.core import member_of, require_session
from koseki.db.types import Person
from flask import request, abort

from . import ldap
import json

class LDAPPlugin:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule("/ldap/uid/<uid>", None, self.ldap_check_uid)

    @require_session(['admin','board','enroll'])
    def ldap_check_uid(self, uid):
        l = ldap.initialize('ldaps://ldap.lu.se')
        ri = l.search('dc=lu,dc=se', ldap.SCOPE_SUBTREE, '(uid=%s)' % uid, None)
        rt, rd = l.result(ri, 0)
        return json.dumps(rd)
