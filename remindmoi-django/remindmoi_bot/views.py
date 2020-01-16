import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from remindmoi_bot.models import Reminder
from remindmoi_bot.scheduler import scheduler
from remindmoi_bot.zulip_utils import send_private_zulip, repeat_unit_to_interval


@csrf_exempt
@require_POST
def add_reminder(request):
    # TODO: make it safer. Add CSRF validation. Sanitize/validate post data
    reminder_obj = json.loads(request.body)  # Create and save remninder object
    reminder = Reminder(**reminder_obj)
    reminder.save()
    msg = f"Don't forget: {reminder.title}"
    scheduler.add_job(  # Schedule reminder
        send_private_zulip,
        'date',
        run_date=reminder.deadline,
        args=[reminder.zulip_user_email, msg, reminder.reminder_id],
        # Create job name from title and reminder id
        id=(str(reminder.reminder_id)+reminder.title)
    )
    return JsonResponse({'success': True,
                         'reminder_id': reminder.reminder_id})


@csrf_exempt
@require_POST
def remove_reminder(request):
    reminder_id = json.loads(request.body)['reminder_id']
    reminder = Reminder.objects.get(reminder_id=int(reminder_id))
    scheduler.remove_job((str(reminder.reminder_id)+reminder.title))  # Remove reminder job
    reminder.delete()  # Remove reminder object
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def list_reminders(request):
    response_reminders = []  # List of reminders to be returned to the client

    zulip_user_email = json.loads(request.body)['zulip_user_email']
    user_reminders = Reminder.objects.filter(zulip_user_email=zulip_user_email)
    # Return title and deadline (in unix timestamp) of reminders
    for reminder in user_reminders.values():
        response_reminders.append({'title': reminder['title'],
                                   'deadline': reminder['deadline'].timestamp(),
                                   'reminder_id': reminder['reminder_id']})

    return JsonResponse({'success': True, 'reminders_list': response_reminders})


@csrf_exempt
@require_POST
def repeat_reminder(request):
    repeat_request = json.loads(request.body)
    reminder_id = repeat_request['reminder_id']
    repeat_unit = repeat_request['repeat_unit']
    reminder = Reminder.objects.get(reminder_id=reminder_id)
    msg = f"Don't forget: {reminder.title}"
    job_id = (str(reminder.reminder_id)+reminder.title)
    scheduler.add_job(
                      send_private_zulip,
                      'interval',
                      **repeat_unit_to_interval(repeat_unit),
                      args=[reminder.zulip_user_email, msg, reminder.reminder_id],
                      id=(job_id)
        )
    return JsonResponse({'success': True})