import logging

from flask import render_template
from flask_wtf import FlaskForm
from koseki.db.types import Person
from wtforms import TextField
from wtforms.validators import DataRequired, Email


class EnrollForm(FlaskForm):
    fname = TextField("First name", validators=[DataRequired()])
    lname = TextField("Last name", validators=[DataRequired()])
    email = TextField("Email", validators=[Email()])
    stil = TextField("StiL")


class AddView:
    def __init__(self, app, core, storage, mailer):
        self.app = app
        self.core = core
        self.storage = storage
        self.mailer = mailer

    def register(self):
        self.app.add_url_rule(
            "/enroll",
            None,
            self.core.require_session(self.enroll_member, ["admin", "board", "enroll"]),
            methods=["GET", "POST"],
        )
        self.core.nav(
            "/enroll", "plus-circle", "Enroll", 2, ["admin", "board", "enroll"]
        )

    def enroll_member(self):
        form = EnrollForm()
        alerts = []

        if form.validate_on_submit():
            if (
                self.storage.session.query(Person)
                .filter_by(email=form.email.data)
                .scalar()
            ):
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": "The specified email %s is already in use!"
                        % form.email.data,
                    }
                )
            elif (
                form.stil.data
                and self.storage.session.query(Person)
                .filter_by(stil=form.stil.data)
                .scalar()
            ):
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": "The specified StiL %s is already in use!"
                        % form.stil.data,
                    }
                )
            else:
                person = Person(enrolled_by=self.core.current_user())
                form.populate_obj(person)
                self.storage.add(person)
                self.storage.commit()

                logging.info("Enrolled %s %s" % (person.fname, person.lname))

                self.mailer.send_mail(person, "member_enrolled.mail", member=person)
                self.mailer.send_mail(
                    self.app.config["ORG_EMAIL"],
                    "board_member_enrolled.mail",
                    member=person,
                )

                msg = [
                    {
                        "class": "alert-success",
                        "title": "Success",
                        "message": "%s %s was successfully enrolled"
                        % (form.fname.data, form.lname.data),
                    }
                ]
                return render_template("message.html", messages=msg)

        return render_template("enroll_member.html", form=form, alerts=alerts)
