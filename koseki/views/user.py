from flask import abort, render_template, request
from flask_wtf import FlaskForm  # type: ignore
from koseki.db.types import Group, Person, PersonGroup
from koseki.util import KosekiAlert, KosekiAlertType
from koseki.view import KosekiView
from wtforms import TextField  # type: ignore
from wtforms.validators import DataRequired, Email  # type: ignore


class GeneralForm(FlaskForm):
    fname = TextField("First name", validators=[DataRequired()])
    lname = TextField("Last name", validators=[DataRequired()])
    email = TextField("Email", validators=[Email()])
    stil = TextField("StiL")


class UserView(KosekiView):
    def register(self):
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

    def member_general(self, uid):
        person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        form = GeneralForm(obj=person)

        if form.validate_on_submit():
            form.populate_obj(person)
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

    def member_groups(self, uid):
        groups = self.storage.session.query(Group).all()
        person: Person = self.storage.session.query(
            Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        if request.method == "POST":
            for group in groups:
                # Only admin can add or remove admin!
                if not self.util.member_of("admin") and group.name == "admin":
                    continue

                current_state = self.util.member_of(group, person)
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
                            (g for g in person.groups if g.gid ==  # type: ignore
                             group.gid),  # type: ignore
                        )
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

    def member_fees(self, uid):
        person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        return render_template("user_fees.html", person=person)

    def member_payments(self, uid):
        person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        return render_template("user_payments.html", person=person)

    def member_admin(self, uid):
        person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
        if not person:
            raise abort(404)

        return render_template("user_admin.html", person=person)
