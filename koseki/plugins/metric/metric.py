from datetime import datetime, timedelta
from typing import List

from logging_prometheus import export_stats_on_root_logger # type: ignore
from prometheus_flask_exporter import PrometheusMetrics  # type: ignore

from koseki.db.types import Fee, Metric, Payment
from koseki.plugin import KosekiPlugin


class MetricPlugin(KosekiPlugin):
    def config(self) -> dict:
        return {}

    def plugin_enable(self) -> None:
        PrometheusMetrics(self.app)
        export_stats_on_root_logger()
        # Register clock
        self.scheduler.add_job(self.calc_metric, "cron", minute=0, second=0)
        self.calc_metric()

    def calc_metric(self) -> None:
        with self.app.app_context():
            self.__calc_metric_active_fees()
            self.__calc_metric_payment()

    def __calc_metric_active_fees(self) -> None:
        if self.storage.session.query(Fee).count() == 0:
            return

        fees: List[Fee] = (
            self.storage.session.query(Fee)
            .order_by(Fee.fid.asc())
            .all()
        )
        time: datetime
        metrics: List[Metric] = (
            self.storage.query(Metric)
            .filter_by(type="fee-current-active")
            .order_by(Metric.time.asc())
            .all()
        )
        if len(metrics) == 0:
            time = datetime.combine(
                fees[0].start.date(), datetime.min.time())
        else:
            time = metrics[0].time
        while time <= datetime.now():
            # Only insert the metric row if it doesn't already exist.
            if sum(1 for metric in metrics if metric.time == time) == 0:
                total: float = 0.0
                for fee in fees:
                    if fee.start < time < fee.end:
                        total += 1
                self.storage.add(Metric(
                    type="fee-current-active",
                    value=total,
                    time=time
                ))
            time += timedelta(days=1)

        self.storage.commit()
        return

    def __calc_metric_payment(self) -> None:
        if self.storage.session.query(Payment).count() == 0:
            return

        payments: List[Payment] = (
            self.storage.session.query(Payment)
            .order_by(Payment.pid.asc())
            .all()
        )
        time: datetime
        metrics: List[Metric] = (
            self.storage.query(Metric)
            .filter_by(type="payment-running-total")
            .order_by(Metric.time.asc())
            .all()
        )
        if len(metrics) == 0:
            time = datetime.combine(
                payments[0].registered.date(), datetime.min.time())
        else:
            time = metrics[0].time
        while time <= datetime.now():
            # Only insert the metric row if it doesn't already exist.
            if sum(1 for metric in metrics if metric.time == time) == 0:
                total: float = 0.0
                for payment in payments:
                    if payment.registered < time:
                        total += float(payment.amount)
                self.storage.add(Metric(
                    type="payment-running-total",
                    value=total,
                    time=time
                ))
            time += timedelta(hours=1)

        self.storage.commit()
        return
