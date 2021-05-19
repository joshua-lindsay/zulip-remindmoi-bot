import re
from typing import Any, Dict
from datetime import timedelta, datetime

SINGULAR_UNITS = ['minute', 'hour', 'day', 'week']

UNITS_REGEX = '(\d+) (minute|hour|day|week)s?'
DATETIME_REGEX = '(\d{1,2}/\d{1,2}/\d{4} (?:2[0-3]|[01][0-9]):[0-5][0-9])'
TIMESTAMP_REGEX = f'(in {UNITS_REGEX}|at {DATETIME_REGEX})'

ADD_REGEX = re.compile(f'^add\s+(stream:\s*(.+)\s+topic:\s*(.+)\s+)?{TIMESTAMP_REGEX}\s+(repeat every\s+{UNITS_REGEX}\s+)?(.+)$', flags=re.MULTILINE|re.DOTALL|re.IGNORECASE)
REPEAT_REGEX = re.compile(f'^repeat\s+(\d+)\s+every\s+{UNITS_REGEX}$', flags=re.MULTILINE|re.DOTALL|re.IGNORECASE)
REMOVE_REGEX = re.compile('^remove\s+(\d+)$', flags=re.MULTILINE|re.DOTALL|re.IGNORECASE)
LIST_REGEX = re.compile('^list$', flags=re.MULTILINE|re.DOTALL|re.IGNORECASE)

ENDPOINT_URL = 'http://localhost:8789'
ADD_ENDPOINT = f'{ENDPOINT_URL}/add_reminder'
REMOVE_ENDPOINT = f'{ENDPOINT_URL}/remove_reminder'
LIST_ENDPOINT = f'{ENDPOINT_URL}/list_reminders'
REPEAT_ENDPOINT = f'{ENDPOINT_URL}/repeat_reminder'
MULTI_REMIND_ENDPOINT = f'{ENDPOINT_URL}/multi_remind'


def is_add_command(content: str) -> bool:
    """
    Ensure message is in form add-stream <str> <str> <int> UNIT every <int> UNIT <str>
    example: add-stream stream topic 1 minutes every 1 minutes message
    """
    match = ADD_REGEX.search(content)
    return match is not None and len(match.groups()) == 11


def is_remove_command(content: str) -> bool:
    match = REMOVE_REGEX.search(content)
    return match is not None and len(match.groups()) == 1


def is_list_command(content: str) -> bool:
    match = LIST_REGEX.search(content)
    return match is not None


def is_repeat_reminder_command(content: str) -> bool:
    match = REPEAT_REGEX.search(content)
    return match is not None and len(match.groups()) == 3


def is_multi_remind_command(content: str) -> bool:
    try:
        command = content.split(' ', maxsplit=2)
        assert command[0] == 'multiremind'
        assert type(int(command[1])) == int
        return True
    except (AssertionError, IndexError, ValueError):
        return False


def parse_add_command_content(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a message object with reminder details,
    construct a JSON/dict.
    """
    # add-stream stream topic 
    # 1 minutes every 5 minutes message
    match = ADD_REGEX.search(message['content'])
    content = match.groups()
    print(content)
    return {
        'zulip_user_email': message['sender_email'],
        'title': content[10],
        'created': message['timestamp'],
        'deadline': compute_deadline_timestamp(
            message['timestamp'], content[4], content[5], content[6]
        ),
        'stream': content[1] or '',
        'topic': content[2] or '',
        'active': True,
        'repeat_unit': content[9],
        'repeat_value': content[8],
    }


def parse_remove_command_content(content: str) -> Dict[str, Any]:
    match = REMOVE_REGEX.search(content)
    groups = match.groups()
    return {
        'reminder_id': groups[0],
    }


def parse_repeat_command_content(content: str) -> Dict[str, Any]:
    match = REPEAT_REGEX.search(content)
    groups = match.groups()
    return {
        'reminder_id': groups[0],
        'repeat_value': groups[1],
        'repeat_unit': groups[2],
        }


def parse_multi_remind_command_content(content: str) -> Dict[str, Any]:
    """
    multiremind 23 @**Jose** @**Max** ->
    {'reminder_id': 23, 'users_to_remind': ['Jose', Max]}
    """
    command = content.split(' ', maxsplit=2)
    users_to_remind = command[2].replace('*', '').replace('@', '').split(' ')
    return {'reminder_id': command[1],
            'users_to_remind': users_to_remind}


def generate_reminders_list(response: Dict[str, Any]) -> str:
    bot_response = ''
    reminders_list = response['reminders_list']
    if not reminders_list:
        return 'No reminders avaliable.'
    for reminder in reminders_list:
        stream = f", stream: {reminder['stream']} topic: {reminder['topic']}" if reminder['stream'] else ""
        bot_response += f"""
        \nReminder id {reminder['reminder_id']}, titled {reminder['title']}{stream}, is scheduled on {datetime.fromtimestamp(reminder['deadline']).strftime('%Y-%m-%d %H:%M')} {reminder['interval']}
        """
    return bot_response


def compute_deadline_timestamp(timestamp_submitted: str, time_value: int, time_unit: str, datetime_text: str) -> str:
    """
    Given a submitted stamp and an interval,
    return deadline timestamp.
    """
    datetime_submitted = datetime.fromtimestamp(timestamp_submitted)
    if time_value is not None and time_unit is not None:
        if time_unit in SINGULAR_UNITS:  # Convert singular units to plural
            time_unit = f"{time_unit}s"

        interval = timedelta(**{time_unit: int(time_value)})
        return (datetime_submitted + interval).timestamp()
    elif datetime_text is not None:
        datetime_value = datetime.strptime(datetime_text, '%d/%m/%Y %H:%M')
        return datetime_value.timestamp()
    return timestamp_submitted
