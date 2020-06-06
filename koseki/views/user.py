from flask import url_for, render_template, session, redirect, escape, request, abort
from koseki.core import require_session, member_of
from koseki.db.types import Person, Group, PersonGroup

from flask_wtf import FlaskForm
from wtforms import TextField, SelectMultipleField
from wtforms.validators import DataRequired, Email


class GeneralForm(FlaskForm):

    fname = TextField("First name", validators=[DataRequired()])
    lname = TextField("Last name", validators=[DataRequired()])
    email = TextField("Email", validators=[Email()])
    stil = TextField("StiL")


class UserView:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule(
            "/user/<int:uid>", None, self.member_general, methods=["GET", "POST"]
        )
        self.app.add_url_rule(
            "/user/<int:uid>/groups", None, self.member_groups, methods=["GET", "POST"]
        )
        self.app.add_url_rule("/user/<int:uid>/fees", None, self.member_fees)
        self.app.add_url_rule(
            "/user/<int:uid>/admin", None, self.member_admin, methods=["GET", "POST"]
        )
        self.core.nav("/logout", "power-off", "Sign out", 999)

    @require_session(["admin", "board"])
    def member_general(self, uid):
        person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        alerts = []
        form = GeneralForm(obj=person)

        if form.validate_on_submit():
            form.populate_obj(person)
            self.storage.commit()

            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "%s %s was successfully updated"
                    % (form.fname.data, form.lname.data),
                }
            )

        return render_template(
            "member_general.html", form=form, person=person, alerts=alerts
        )

    @require_session(["admin", "board"])
    def member_groups(self, uid):
        groups = self.storage.session.query(Group).all()
        person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        alerts = []

        if request.method == "POST":
            for group in groups:
                # Only admin can add or remove admin!
                if not member_of("admin") and group.name == "admin":
                    continue

                current_state = member_of(group, person)
                if sum(1 for gid in list(request.form.keys()) if gid == str(group.gid)):
                    # Member of the group, add if needed
                    not current_state and self.storage.add(
                        PersonGroup(uid=person.uid, gid=group.gid)
                    )
                else:
                    # Not a member, remove if needed
                    current_state and list(
                        map(
                            self.storage.delete,
                            (g for g in person.groups if g.gid == group.gid),
                        )
                    )

            self.storage.commit()

            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "Groups for %s %s was successfully updated"
                    % (person.fname, person.lname),
                }
            )

        return render_template(
            "member_groups.html", person=person, groups=groups, alerts=alerts
        )

    @require_session(["admin", "board"])
    def member_fees(self, uid):
        person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        return render_template("member_fees.html", person=person)

    @require_session(["admin"])
    def member_admin(self, uid):
        person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        return render_template("member_admin.html", person=person)
