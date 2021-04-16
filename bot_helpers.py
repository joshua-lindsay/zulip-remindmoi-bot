from typing import Any, Dict
from datetime import timedelta, datetime


UNITS = ['minutes', 'hours', 'days', 'weeks']
SINGULAR_UNITS = ['minute', 'hour', 'day', 'week']
REPEAT_UNITS = ['weekly', 'daily', 'monthly'] + ['minutely']  # Remove after testing 

ENDPOINT_URL = 'http://localhost:8789'
ADD_ENDPOINT = ENDPOINT_URL + '/add_reminder'
REMOVE_ENDPOINT = ENDPOINT_URL + '/remove_reminder'
LIST_ENDPOINT = ENDPOINT_URL + '/list_reminders'
REPEAT_ENDPOINT = ENDPOINT_URL + '/repeat_reminder'
MULTI_REMIND_ENDPOINT = ENDPOINT_URL + '/multi_remind'


def is_add_command(content: str, units=UNITS + SINGULAR_UNITS) -> bool:
    """
    Ensure message is in form add <int> UNIT <str>
    example: add 1 minutes message
    """
    try:
        command = content.split(' ', maxsplit=3)  # Ensure the last element is str
        assert command[0] == 'add'
        assert type(int(command[1])) == int
        assert command[2] in units
        assert type(command[3]) == str
        return True
    except (IndexError, AssertionError, ValueError):
        return False


def is_add_stream_command(content: str, units=UNITS + SINGULAR_UNITS) -> bool:
    """
    Ensure message is in form add-stream <str> <str> <int> UNIT <str>
    example: add-stream stream topic 1 minutes message
    """
    try:
        command = content.split(' ', maxsplit=5)  # Ensure the last element is str
        assert command[0] == 'add-stream'
        assert type(command[1]) == str
        assert type(command[2]) == str
        assert type(int(command[3])) == int
        assert command[4] in units
        assert type(command[5]) == str
        return True
    except (IndexError, AssertionError, ValueError):
        return False


def is_add_repeat_stream_command(content: str, units=UNITS + SINGULAR_UNITS) -> bool:
    """
    Ensure message is in form add-stream <str> <str> <int> UNIT every <int> UNIT <str>
    example: add-stream stream topic 1 minutes every 1 minutes message
    """
    try:
        command = content.split(' ', maxsplit=8)  # Ensure the last element is str
        assert command[0] == 'add-stream'
        assert type(command[1]) == str
        assert type(command[2]) == str
        assert type(int(command[3])) == int
        assert command[4] in units
        assert command[5] == 'every'
        assert type(int(command[6])) == int
        assert command[7] in units
        assert type(command[8]) == str
        return True
    except (IndexError, AssertionError, ValueError):
        return False


def is_add_repeat_reminder_command(content: str, units=UNITS + SINGULAR_UNITS) -> bool:
    """
    Ensure message is in form ADD <int> UNIT every <int> UNIT <str>
    add 1 minutes every 1 minutes message
    """
    try:
        command = content.split(' ', maxsplit=6)  # Ensure the last element is str
        assert command[0] == 'add'
        assert type(int(command[1])) == int
        assert command[2] in units
        assert command[3] == 'every'
        assert type(int(command[4])) == int
        assert command[5] in units
        assert type(command[6]) == str
        return True
    except (IndexError, AssertionError, ValueError):
        return False


def is_remove_command(content: str) -> bool:
    try:
        command = content.split(' ')
        assert command[0] == 'remove'
        assert type(int(command[1])) == int
        return True
    except (AssertionError, IndexError, ValueError):
        return False


def is_list_command(content: str) -> bool:
    try:
        command = content.split(' ')
        assert command[0] == 'list'
        return True
    except (AssertionError, IndexError, ValueError):
        return False


def is_repeat_reminder_command(content: str, units=UNITS + SINGULAR_UNITS) -> bool:
    try:
        command = content.split(' ')
        assert command[0] == 'repeat'
        assert type(int(command[1])) == int
        assert command[2] == 'every'
        assert type(int(command[3])) == int
        assert command[4] in units
        return True
    except (AssertionError, IndexError, ValueError):
        return False


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
    content = message['content'].split(
        ' ', maxsplit=3
    )  # Ensure the last element is str
    return {
        'zulip_user_email': message['sender_email'],
        'title': content[3],
        'created': message['timestamp'],
        'deadline': compute_deadline_timestamp(
            message['timestamp'], content[1], content[2]
        ),
        'stream': '',
        'topic': '',
        'active': True,
    }


def parse_add_stream_command_content(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a message object with reminder details,
    construct a JSON/dict.
    """
    # add-stream stream topic 1 minutes message
    content = message['content'].split(' ', maxsplit=5)
    return {
        'zulip_user_email': message['sender_email'],
        'title': content[5],
        'created': message['timestamp'],
        'deadline': compute_deadline_timestamp(
            message['timestamp'], content[3], content[4]
        ),
        'stream': content[1],
        'topic': content[2],
        'active': True,
    }


def parse_add_repeat_stream_command_content(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a message object with reminder details,
    construct a JSON/dict.
    """
    # add-stream stream topic 1 minutes message
    content = message['content'].split(' ', maxsplit=8)
    return {
        'zulip_user_email': message['sender_email'],
        'title': content[8],
        'created': message['timestamp'],
        'deadline': compute_deadline_timestamp(
            message['timestamp'], content[3], content[4]
        ),
        'stream': content[1],
        'topic': content[2],
        'active': True,
        'repeat_value': content[6],
        'repeat_unit': content[7],
    }


def parse_add_reminder_command_content(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a message object with reminder details,
    construct a JSON/dict.
    """
    content = message['content'].split(
        ' ', maxsplit=6
    )  # Ensure the last element is str
    return {
        'zulip_user_email': message['sender_email'],
        'title': content[6],
        'created': message['timestamp'],
        'deadline': compute_deadline_timestamp(
            message['timestamp'], content[1], content[2]
        ),
        'stream': '',
        'topic': '',
        'active': True,
        'repeat_unit': content[5],
        'repeat_value': content[4],
    }


def parse_remove_command_content(content: str) -> Dict[str, Any]:
    command = content.split(' ')
    return {'reminder_id': command[1]}


def parse_repeat_command_content(content: str) -> Dict[str, Any]:
    command = content.split(' ')
    return {'reminder_id': command[1],
            'repeat_unit': command[4],
            'repeat_value': command[3]}


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
        print('stream',stream)
        bot_response += f"""
        \nReminder id {reminder['reminder_id']}, titled {reminder['title']}{stream}, is scheduled on {datetime.fromtimestamp(reminder['deadline']).strftime('%Y-%m-%d %H:%M')} {reminder['interval']}
        """
    return bot_response


def compute_deadline_timestamp(timestamp_submitted: str, time_value: int, time_unit: str) -> str:
    """
    Given a submitted stamp and an interval,
    return deadline timestamp.
    """
    if time_unit in SINGULAR_UNITS:  # Convert singular units to plural
        time_unit = f"{time_unit}s"

    interval = timedelta(**{time_unit: int(time_value)})
    datetime_submitted = datetime.fromtimestamp(timestamp_submitted)
    return (datetime_submitted + interval).timestamp()