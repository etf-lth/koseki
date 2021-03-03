from datetime import datetime, timedelta
from typing import List, Union

from flask import Blueprint
from werkzeug.wrappers import Response

from koseki.db.types import Metric, Payment
from koseki.plugin import KosekiPlugin


class MetricPlugin(KosekiPlugin):
    def config(self) -> dict:
        return {}

    def plugin_enable(self) -> None:
        # register clock
        self.scheduler.add_job(self.calc_metric, "cron", minute=0, second=0)
        self.calc_metric()

    def calc_metric(self) -> None:
        with self.app.app_context():
            self.__calc_metric_payment()

    def __calc_metric_payment(self) -> None:
        if self.storage.session.query(Payment).count() == 0:
            return

        payments: List[Payment] = (
            self.storage.session.query(Payment)
            .order_by(Payment.pid.asc())
            .all()
        )
        time: datetime
        last_metric: Union[Metric, None] = (
            self.storage.query(Metric)
            .order_by(Metric.time.desc())
            .first()
        )
        if last_metric is None:
            time = datetime.combine(payments[0].registered.date(), datetime.min.time())
        else:
            time = last_metric.time
        while time <= datetime.now():
            total: float = 0.0
            for payment in payments:
                if payment.registered < time:
                    total += float(payment.amount)
            # Only insert the metric row if it doesn't already exist.
            if (self.storage.query(Metric)
                .filter_by(type="payment-running-total", value=total, time=time)
                .count()) == 0:
                self.storage.add(Metric(
                    type="payment-running-total",
                    value=total,
                    time=time
                ))
            time += timedelta(hours=1)

        self.storage.commit()
        return

    def create_blueprint(self) -> Blueprint:
        blueprint: Blueprint = Blueprint("cas", __name__)
        blueprint.add_url_rule("/metric", None, self.metric)
        return blueprint

    def metric(self) -> Union[str, Response]:
        return "metric on"
