from koseki import app, storage
from koseki.core import member_of, require_session
from koseki.db.types import Person
from flask import request, abort

import ldap
import json

@app.route('/ldap/uid/<uid>')
@require_session(['admin','board','enroll'])
def ldap_check_uid(uid):
    l = ldap.initialize('ldaps://ldap.lu.se')
    ri = l.search('dc=lu,dc=se', ldap.SCOPE_SUBTREE, '(uid=%s)' % uid, None)
    rt, rd = l.result(ri, 0)
    return json.dumps(rd)
