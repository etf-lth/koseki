from os import name
from typing import Union

from flask import got_request_exception, render_template, abort, Blueprint, abort, redirect, render_template, request, url_for
from flask_wtf import FlaskForm  # type: ignore
from werkzeug.wrappers import Response
from wtforms import StringField, SubmitField  # type: ignore
from wtforms.validators import DataRequired, Email  # type: ignore

from koseki.db.storage import DEFAULT_GROUPS
from koseki.db.types import Group, Person, PersonGroup
from koseki.view import KosekiView
from koseki.util import KosekiAlert, KosekiAlertType


class GroupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    descr = StringField("Description", validators=[DataRequired()])
    submitUpdate = SubmitField("Update")
    submitDelete = SubmitField("Delete")

class GroupsView(KosekiView):
    def register(self) -> None:
        self.util.nav("/groups", "user-friends", "Groups", 1, ["admin", "board"])
        
        self.app.add_url_rule(
            "/groups",
            None,
            self.auth.require_session(self.list_groups, ["admin", "board"]),
            methods=["GET", "POST"],
        )
        
        self.app.add_url_rule(
            "/group/<int:gid>",
            None,
            self.auth.require_session(self.group_general, ["admin", "board"]),
            methods=["GET", "POST"],
        )

    def list_groups(self) -> Union[str, Response]:
        form = GroupForm()

        if form.validate_on_submit():
            if (
                self.storage.session.query(Group)
                .filter_by(name=form.name.data)
                .scalar()
            ):
                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Error",
                        "The specified group name %s is already in use!" % form.name.data,
                    )
                )
            else:
                group = Group()
                form.populate_obj(group)
                self.storage.add(group)
                self.storage.commit()

                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.SUCCESS,
                        "Success",
                        "%s (%s) was successfully added" % (form.name.data, form.descr.data),
                    )
                )
                # reset form
                form.name.data = ""
                form.descr.data = ""

        return render_template(
            "group_list.html",
            groups=self.storage.session.query(Group)
            .order_by(Group.gid.asc())
            .all(),
            form=form
        )

    def group_general(self, gid: int) -> Union[str, Response]:
        group: Group = self.storage.session.query(
            Group).filter_by(gid=gid).scalar()
        if not group:
            raise abort(404)

        form = GroupForm(obj=group)

        if group.name in DEFAULT_GROUPS and request.method == "POST":
            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.DANGER,
                    "Error",
                    "%s is a default role, cannot be changed!" % (form.name.data),
                )
            )

        elif form.submitDelete.data and form.validate_on_submit():
            self.storage.delete(group)
            self.storage.commit()
            # logging.info(
            #     "Deleted product %s #%d", product_form.name.data, product.pid
            # )
            return redirect(url_for("list_groups"))

        elif form.submitUpdate.data and form.validate_on_submit():
            form.populate_obj(group)
            self.storage.commit()

            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "%s (%s) was successfully updated" % (form.name.data, form.descr.data),
                )
            )

        return render_template(
            "group_general.html", 
                form=form,
                group=group,
                is_default_role=group.name in DEFAULT_GROUPS,
                persons=self.storage.session.query(Person)
                    .join(PersonGroup, PersonGroup.uid == Person.uid)
                    .filter(PersonGroup.gid == gid)
                    .order_by(Person.uid.desc())
                    .all(),
        )

