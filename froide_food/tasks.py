from froide.celery import app as celery_app


@celery_app.task
def depublish_old_reports_task():
    from .utils import depublish_old_reports

    depublish_old_reports()
