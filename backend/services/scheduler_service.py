import eventlet
from datetime import datetime, date, timedelta
from extensions import db, socketio
from models import Task, User, Notification
from services.email_service import send_notification_email

_scheduler_running = False

def check_task_deadlines(app):
    with app.app_context():
        try:
            today = datetime.utcnow().date()
            active_tasks = Task.query.filter(
                Task.status.in_(['assigned', 'in_progress', 'pending', 'rejected']),
                Task.deadline.isnot(None),
                Task.assigned_to.isnot(None)
            ).all()

            for task in active_tasks:
                task_deadline_date = task.deadline.date() if isinstance(task.deadline, datetime) else task.deadline
                delta_days = (task_deadline_date - today).days

                msg = None
                subject = None

                if delta_days == 2:
                    msg = f"Reminder: Your task '{task.title}' is due in 2 days ({task_deadline_date})."
                    subject = f"Task Due in 2 Days: {task.title}"
                elif delta_days == 1:
                    msg = f"Urgent: Your task '{task.title}' is due tomorrow ({task_deadline_date})!"
                    subject = f"Task Due Tomorrow: {task.title}"
                elif delta_days == 0:
                    msg = f"Action Required: Your task '{task.title}' is due TODAY ({task_deadline_date})!"
                    subject = f"Task Due Today: {task.title}"
                elif delta_days < 0:
                    days_overdue = abs(delta_days)
                    msg = f"OVERDUE: Your task '{task.title}' is {days_overdue} day(s) overdue (was due {task_deadline_date})!"
                    subject = f"Overdue Task: {task.title}"

                if msg:
                    existing_notif = Notification.query.filter_by(
                        user_id=task.assigned_to,
                        task_id=task.id,
                        message=msg
                    ).first()

                    if not existing_notif:
                        notif = Notification(
                            user_id=task.assigned_to,
                            task_id=task.id,
                            meeting_id=task.meeting_id,
                            message=msg,
                            type='task'
                        )
                        db.session.add(notif)
                        db.session.commit()
                        print(f">> [Scheduler] Generated deadline reminder for user {task.assigned_to}: {msg}")

                        assignee = User.query.get(task.assigned_to)
                        if assignee and assignee.email:
                            send_notification_email(assignee.email, subject, msg)

        except Exception as e:
            print(f">> [Scheduler Error during deadline check]: {e}")

def _scheduler_loop(app):
    eventlet.sleep(5)
    while True:
        try:
            check_task_deadlines(app)
        except Exception as e:
            print(f">> [Scheduler Loop Error]: {e}")
        eventlet.sleep(3600)

def init_scheduler(app):
    global _scheduler_running
    if not _scheduler_running:
        _scheduler_running = True
        eventlet.spawn(_scheduler_loop, app)
        print(">> [Eventlet Scheduler] Task deadline reminder greenlet loop initialized.")
