from re import U
from sys import prefix
from flask import Blueprint
from sqlalchemy.sql.operators import endswith_op
from koseki.db.types import Person
from koseki.plugin import KosekiPlugin
from flask import render_template_string
import secrets

from typing import Union
from flask import Response
from flask import (Blueprint, redirect, render_template, request, session, abort,
                   url_for)
from flask_wtf import FlaskForm  # type: ignore
from werkzeug.wrappers import Response
from wtforms import HiddenField, PasswordField, SubmitField  # type: ignore
from wtforms.validators import DataRequired  # type: ignore
from koseki.db.types import Group, Person, PersonGroup

from koseki.db.types import Payment, Person, Product
from koseki.plugin import KosekiPlugin
from koseki.plugins.access.db import AccessRule, Accesskey
from koseki.util import KosekiAlert, KosekiAlertType


from flask import render_template, abort
from flask_wtf import FlaskForm  # type: ignore
from werkzeug.wrappers import Response
from wtforms import StringField, SelectField  # type: ignore
from wtforms.validators import DataRequired, Email  # type: ignore

from koseki.db.types import Group, Person, PersonGroup
from koseki.view import KosekiView
from koseki.util import KosekiAlert, KosekiAlertType
from koseki.plugins.access.db import AccessRule 

class KeyForm(FlaskForm):
    descr = StringField("Description", validators=[DataRequired()])
    submitUpdate = SubmitField("Update")
    submitDelete = SubmitField("Delete")

class AccessRuleForm(FlaskForm):
    endpoint = StringField("Endpoint", validators=[DataRequired()])
    attribute = SelectField("Attribute", validators=[DataRequired()])
    descr = StringField("Description", validators=[DataRequired()])
    submit = SubmitField("Add Access Rule")

class AccessRuleDeleteForm(FlaskForm):
    submitDelete = SubmitField("Delete")

class AccessPlugin(KosekiPlugin):
    def config(self) -> dict:
        return {}
    
    def allowed_attributes(self) -> dict:
        return {
            "id":       lambda m: str(m.uid),
            "email":    lambda m: m.email,
            **( {"username": lambda m: m.username} if self.app.config.get("USER_USERNAME_ENABLED") else {} ),
        }

    def create_blueprint(self) -> Blueprint:
        blueprint: Blueprint = Blueprint("access", __name__, template_folder="./templates")
        self.app.add_url_rule(
            "/access",
            None,
            self.auth.require_session(self.access_list, ["admin"]),
            methods=["GET", "POST"],
        )

        self.app.add_url_rule(
            "/access/<int:key_id>",
            None,
            self.auth.require_session(self.access_general, ["admin"]),
            methods=["GET", "POST"],
        )

        self.app.add_url_rule(
            "/access/<key>/<endpoint>",
            None,
            self.access_by_rule,
            methods=["GET", "POST"],
        )

        self.util.nav(
            "/access", "key", "Access", 4, ["admin"]
        )

        return blueprint
    
    def register_models(self) -> None:
        from .db import AccessRuleGroup, Accesskey, AccessRule

    def access_by_rule(self, key: str, endpoint: str) -> Union[str, Response]:
        rule: AccessRule = (
            self.storage.session.query(AccessRule)
            .join(Accesskey, Accesskey.id == AccessRule.kid)
            .filter(Accesskey.key == key, AccessRule.endpoint == endpoint)
            .scalar()
        )
        if not rule:
            raise abort(404)

        get_attr = self.allowed_attributes().get(rule.attribute)
        if not get_attr:
            raise abort(400)

        allowed_gids = {g.gid for g in rule.groups}

        out: str = ""
        for member in self.storage.session.query(Person).filter_by(state="active").all():
            value = get_attr(member)
            if value is None or len(value) < 1:
                continue
            if len(rule.groups) == 0 or any(pg.gid in allowed_gids for pg in member.groups):
                out += value + "\r\n"

        return Response(out, mimetype="text/plain")

    def access_list(self) -> Union[str, Response]:
        form = KeyForm()

        if form.validate_on_submit():
            key = Accesskey(key=secrets.token_urlsafe(32))
            form.populate_obj(key)
            self.storage.add(key)
            self.storage.commit()

            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "A new key was successfully added",
                )
            )
            # reset form
            form.descr.data = ""

        return render_template('access_list.html',
            form=form,
            keys=self.storage.session.query(Accesskey)
            .order_by(Accesskey.id.asc())
            .all())

    def access_general(self, key_id: int) -> Union[str, Response]:
        key: Accesskey = self.storage.session.query(Accesskey).filter_by(id=key_id).scalar()
        if not key:
            raise abort(404)

        groups = self.storage.session.query(Group).order_by(Group.gid.asc()).all()

        keyform = KeyForm(obj=key, prefix="key")
        access_rule_form = AccessRuleForm(prefix="access_rule")
        access_rule_form.attribute.choices = [(k, k) for k in self.allowed_attributes().keys()]
        access_rule_delete_form = AccessRuleDeleteForm(prefix="access_rule_delete")

        if keyform.submitUpdate.data and keyform.validate_on_submit():
            keyform.populate_obj(key)
            self.storage.commit()
            self.util.alert(
                KosekiAlert(KosekiAlertType.SUCCESS, "Success", "Key was successfully updated")
            )
        
        elif keyform.submitDelete.data and keyform.validate_on_submit():
            self.storage.delete(key)
            self.storage.commit()
            # logging.info(
            #     "Deleted product %s #%d", product_form.name.data, product.pid
            # )
            return redirect(url_for("access_list"))

        elif access_rule_form.submit.data and access_rule_form.validate_on_submit():
            if (
                self.storage.session.query(AccessRule)
                .filter_by(kid=key_id, endpoint=access_rule_form.endpoint.data)
                .scalar()
            ):
                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Error",
                        "The endpoint /%s is already in use on this key!" % access_rule_form.endpoint.data,
                    )
                )
                return render_template("message.html")

            rule = AccessRule(kid=key_id)
            access_rule_form.populate_obj(rule)

            # Mirror member_groups: add each group whose checkbox was checked
            for g in groups:
                if sum(1 for form_gid in request.form.keys() if form_gid == str(g.gid)):
                    # logging.info(
                    #     "Adding group %s to access rule %s", g.name, rule.endpoint
                    # )
                    rule.groups.append(g)

            self.storage.add(rule)
            self.storage.commit()
            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "Access rule for %s was successfully added" % rule.endpoint,
                )
            )
        elif access_rule_delete_form.submitDelete.data and access_rule_delete_form.validate_on_submit():
            rule: AccessRule = self.storage.session.query(AccessRule).filter_by(
                id=int(request.form["delete_rule_id"]), kid=key_id
            ).scalar()
            if not rule:
                raise abort(404)
            # logging.info("Deleting access rule %s from key %d", rule.endpoint, key_id)
            self.storage.delete(rule)
            self.storage.commit()
            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "Access rule for %s was successfully deleted" % rule.endpoint,
                )
            )

        return render_template(
            'access_general.html',
            key=key,
            access_rule_form=access_rule_form,
            access_rule_delete_form=access_rule_delete_form,
            keyform=keyform,
            keys=self.storage.session.query(Accesskey).order_by(Accesskey.id.asc()).all(),
            groups=groups,
            rules=self.storage.session.query(AccessRule).filter_by(kid=key_id).order_by(AccessRule.id.asc()).all(),
        )
