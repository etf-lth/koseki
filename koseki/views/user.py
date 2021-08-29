from typing import Iterable, Union

from flask import abort, render_template, request
from flask_wtf import FlaskForm  # type: ignore
from werkzeug.wrappers import Response
from wtforms import StringField  # type: ignore
from wtforms.validators import DataRequired, Email  # type: ignore

from koseki.db.types import Group, Person, PersonGroup
from koseki.util import KosekiAlert, KosekiAlertType
from koseki.view import KosekiView


class GeneralForm(FlaskForm):
    fname = StringField("First name", validators=[DataRequired()])
    lname = StringField("Last name", validators=[DataRequired()])
    email = StringField("Email", validators=[Email(), DataRequired()])
    username = StringField("StiL")
    address_line1 = StringField("Address")
    address_line2 = StringField("Address (complement)")
    city = StringField("City")
    postcode = StringField("Zip / Postal code")
    region = StringField("Region / State")
    country = StringField("Country")
    phone_number = StringField("Phone number")


class UserView(KosekiView):
    def register(self) -> None:
        self.app.add_url_rule(
            "/user/<int:uid>",
            None,
            self.auth.require_session(self.member_general, ["admin", "board"]),
            methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            "/user/<int:uid>/groups",
            None,
            self.auth.require_session(self.member_groups, ["admin", "board"]),
            methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            "/user/<int:uid>/fees",
            None,
            self.auth.require_session(self.member_fees, ["admin", "board"]),
        )
        self.app.add_url_rule(
            "/user/<int:uid>/payments",
            None,
            self.auth.require_session(
                self.member_payments, ["admin", "board"]),
        )
        self.app.add_url_rule(
            "/user/<int:uid>/admin",
            None,
            self.auth.require_session(self.member_admin, ["admin"]),
            methods=["GET", "POST"],
        )

    def member_general(self, uid: int) -> Union[str, Response]:
        person: Person = self.storage.session.query(
            Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        form = GeneralForm(obj=person)

        if form.validate_on_submit():
            form.populate_obj(person)
            person.reduce_empty_to_null()
            self.storage.commit()

            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "%s %s was successfully updated"
                    % (form.fname.data, form.lname.data),
                )
            )

        return render_template(
            "user_general.html", form=form, person=person
        )

    def member_groups(self, uid: int) -> Union[str, Response]:
        groups: Iterable[Group] = self.storage.session.query(Group).all()
        person: Person = self.storage.session.query(
            Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        if request.method == "POST":
            # Only enroll can add or remove groups
            if not self.auth.member_of("enroll") and not self.auth.member_of("admin"):
                abort(403)
            for group in groups:
                # Only admin can add or remove admin!
                if not self.auth.member_of("admin") and group.name == "admin":
                    continue

                current_state = self.auth.member_of(group, person)
                if sum(1 for gid in list(request.form.keys()) if gid == str(group.gid)):
                    # Member of the group, add if needed
                    if not current_state:
                        self.storage.add(
                            PersonGroup(uid=person.uid, gid=group.gid)
                        )
                else:
                    # Not a member, remove if needed
                    if current_state:
                        map(
                            self.storage.delete,
                            (g for g in person.groups if g.gid == group.gid),
                        )

            self.storage.commit()

            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "Groups for %s %s was successfully updated"
                    % (person.fname, person.lname),
                )
            )

        return render_template(
            "user_groups.html", person=person, groups=groups
        )

    def member_fees(self, uid: int) -> Union[str, Response]:
        person: Person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        return render_template("user_fees.html", person=person)

    def member_payments(self, uid: int) -> Union[str, Response]:
        person: Person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        return render_template("user_payments.html", person=person)

    def member_admin(self, uid: int) -> Union[str, Response]:
        person: Person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        return render_template("user_admin.html", person=person)
