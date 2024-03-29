import logging
from typing import Union

from flask import render_template
from flask_wtf import FlaskForm  # type: ignore
from werkzeug.wrappers import Response
from wtforms import StringField  # type: ignore
from wtforms.validators import DataRequired, Email  # type: ignore

from koseki.db.types import Person
from koseki.util import KosekiAlert, KosekiAlertType
from koseki.view import KosekiView


class EnrollForm(FlaskForm):
    fname = StringField("First name", validators=[DataRequired()])
    lname = StringField("Last name", validators=[DataRequired()])
    email = StringField("Email", validators=[Email()])
    username = StringField("StiL")


class AddView(KosekiView):
    def register(self) -> None:
        self.app.add_url_rule(
            "/enroll",
            None,
            self.auth.require_session(
                self.enroll_member, ["admin", "board", "enroll"]),
            methods=["GET", "POST"],
        )
        self.util.nav(
            "/enroll", "plus-circle", "Enroll", 2, ["admin", "board", "enroll"]
        )

    def enroll_member(self) -> Union[str, Response]:
        form = EnrollForm()

        if form.validate_on_submit():
            if (
                self.storage.session.query(Person)
                .filter_by(email=form.email.data)
                .scalar()
            ):
                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Error",
                        "The specified email %s is already in use!" % form.email.data,
                    )
                )
            elif (
                form.username.data
                and self.storage.session.query(Person)
                .filter_by(username=form.username.data)
                .scalar()
            ):
                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Error",
                        "The specified StiL %s is already in use!" % form.username.data,
                    )
                )
            else:
                person = Person(enrolled_by=self.util.current_user())
                form.populate_obj(person)
                self.storage.add(person)
                self.storage.commit()

                logging.info("Enrolled %s %s", person.fname, person.lname)

                self.mail.send_mail(
                    person, "mail/member_enrolled.html", member=person)
                self.mail.send_mail(
                    self.app.config["ORG_EMAIL"],
                    "mail/board_member_enrolled.html",
                    member=person,
                )

                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.SUCCESS,
                        "Success",
                        "%s %s was successfully enrolled"
                        % (form.fname.data, form.lname.data),
                    )
                )
                return render_template("message.html")

        return render_template("enroll_member.html", form=form)
