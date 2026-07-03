from datetime import datetime
from typing import Union
from flask import render_template
from werkzeug.wrappers import Response
from sqlalchemy import func
from koseki.db.types import Person, Fee, Payment
from koseki.view import KosekiView


class IndexView(KosekiView):
    def register(self) -> None:
        self.app.add_url_rule("/", None, self.auth.require_session(self.index))
        self.util.nav("/", "home", "Home", -999)

    def index(self) -> Union[str, Response]:
        if self.auth.member_of("admin") or self.auth.member_of("board"):
            active = (
                self.storage.session.query(Person)
                .filter_by(state="active")
                .count()
            )
            pending = (
                self.storage.session.query(Person)
                .filter_by(state="pending")
                .count()
            )
            year_start = datetime.now().replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            enrolled = (
                self.storage.session.query(Person)
                .filter(Person.enrolled >= year_start)
                .count()
            )
            income = (
                self.storage.session.query(func.sum(Fee.amount))
                .filter(Fee.registered >= year_start)
                .scalar()
            ) or 0

            top_spender = (
                self.storage.session.query(
                    Person,
                    func.sum(Payment.amount).label("total_spent"),
                )
                .join(Payment, Payment.uid == Person.uid)
                .filter(Payment.registered >= year_start)
                .filter(Payment.amount > 0)
                .group_by(Person.uid)
                .order_by(func.sum(Payment.amount).desc())
                .first()
            )

            return render_template(
                "overview.html",
                active=active,
                pending=pending,
                enrolled=enrolled,
                income=income,
                top_spender=top_spender,
            )
        else:
            return render_template("home.html")