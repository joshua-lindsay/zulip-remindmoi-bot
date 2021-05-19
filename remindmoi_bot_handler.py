import json
import requests

from typing import Any, Dict

from bot_helpers import (
    ADD_ENDPOINT,
    REMOVE_ENDPOINT,
    LIST_ENDPOINT,
    REPEAT_ENDPOINT,
    MULTI_REMIND_ENDPOINT,
    is_add_command,
    is_remove_command,
    is_list_command,
    is_repeat_reminder_command,
    is_multi_remind_command,
    parse_add_command_content,
    parse_remove_command_content,
    generate_reminders_list,
    parse_repeat_command_content,
    parse_multi_remind_command_content,
)


USAGE = """
A bot that schedules reminders for users.

To store a reminder, mention or send a message to the bot in the following format:

`add in <number> <time unit> <content_of_reminder>`
ie. `add in 1 day complete timesheets`
(Avaliable time units: minutes, hours, days, weeks)

or

`add at <date and time> <content_of_reminder>`
ie. `add at 13/05/2021 16:00 complete timesheets`
(Date and time must be in the format: DD/MM/YYYY HH:MM)

These reminders will be sent to your private messages from the Reminder Bot

To add a repeat reminder:
`add in <number> <time unit> repeat every <number> <time unit> <content_of_reminder>`
ie. `add in 1 day repeat every 1 week complete timesheets`
(Avaliable time units: minutes, hours, days, weeks)

or

`add at <date and time> repeat every <number> <time unit> <content_of_reminder>`
ie. `add at 13/05/2021 16:00 repeat every 7 days complete timesheets`
(Date and time must be in the format: DD/MM/YYYY HH:MM)

To add a reminder to a stream/topic:
`add stream: <stream name> topic: <topic name> in <number> <time unit> (optional: repeat every <number> <time unit>) <content_of_reminder>`
ie. `add stream: Timesheets topic: Please remember your timesheets in 1 day repeat every 1 week complete timesheets`
(Avaliable time units: minutes, hours, days, weeks)

or

`add stream: <stream name> topic: <topic name> at <date and time> (optional: repeat every <number> <time unit>) <content_of_reminder>`
ie. `add stream: Timesheets topic: Please remember your timesheets at 13/05/2021 16:00 repeat every 7 days complete timesheets`
(Date and time must be in the format: DD/MM/YYYY HH:MM)

To remove a reminder:
`remove <reminder id>`

To list reminders:
`list`

To repeat an existing reminder: 
`repeat <reminder id> every <number> <time unit>`
ie. `repeat 23 every 2 weeks`
(Avaliable time units: minutes, hours, days, weeks)

To add a reminder to a stream
`add-stream stream topic 
int <UNIT> <title_of_reminder>`

`add-stream stream topic 
1 minutes dont forget`


To add a reminder to a stream and repeat:
`add-stream stream topic 
int <UNIT> every int <UNIT> <title_of_reminder>`

`add-stream stream topic 
1 minutes every 1 minutes dont forget`

"""


class RemindMoiHandler(object):
    """
    A docstring documenting this bot.
    the reminder bot reminds people of its reminders
    """

    def usage(self) -> str:
        return USAGE

    def handle_message(self, message: Dict[str, Any], bot_handler: Any) -> None:
        bot_response = get_bot_response(message, bot_handler)
        bot_handler.send_reply(message, bot_response)


def get_bot_response(message: Dict[str, Any], bot_handler: Any) -> str:
    if message["content"].startswith(("help", "?", "halp")):
        return USAGE

    try:
        if is_add_command(message["content"]):
            reminder_object = parse_add_command_content(message)
            response = requests.post(url=ADD_ENDPOINT, json=reminder_object)
            response = response.json()
            assert response["success"]

            reminder_id = response["reminder_id"]
            stream_details = ""
            if reminder_object['stream'] != '' and reminder_object['topic'] != '':
                stream_details = f" Your reminder will be display in Stream: {reminder_object['stream']} - Topic: {reminder_object['topic']}."

            if reminder_object["repeat_value"] is None or reminder_object["repeat_unit"] is None:
                return f"Reminder stored.{stream_details} Your reminder id is: {reminder_id}"
                
            reminder_object["reminder_id"] = str(reminder_id)
            response = requests.post(url=REPEAT_ENDPOINT, json=reminder_object)
            response = response.json()
            assert response["success"]
            return f"Repeat reminder stored.{stream_details} Your reminder id is: {reminder_id}"

        if is_remove_command(message["content"]):
            reminder_id = parse_remove_command_content(message["content"])
            response = requests.post(url=REMOVE_ENDPOINT, json=reminder_id)
            response = response.json()
            assert response["success"]
            return "Reminder deleted."

        if is_list_command(message["content"]):
            zulip_user_email = {"zulip_user_email": message["sender_email"]}
            response = requests.post(url=LIST_ENDPOINT, json=zulip_user_email)
            response = response.json()
            assert response["success"]
            return generate_reminders_list(response)

        if is_repeat_reminder_command(message["content"]):
            repeat_request = parse_repeat_command_content(message["content"])
            response = requests.post(url=REPEAT_ENDPOINT, json=repeat_request)
            response = response.json()
            assert response["success"]
            return f"Reminder will be repeated every {repeat_request['repeat_value']} {repeat_request['repeat_unit']}."

        if is_multi_remind_command(message["content"]):
            multi_remind_request = parse_multi_remind_command_content(
                message["content"]
            )
            response = requests.post(
                url=MULTI_REMIND_ENDPOINT, json=multi_remind_request
            )
            response = response.json()
            assert response["success"]
            return f"Reminder will be sent to the specified recepients."  # Todo: add list of recepients
        return f"""Invalid input.
        
        {USAGE}"""
    except requests.exceptions.ConnectionError:
        return "Server not running, call Karim"
    except (json.JSONDecodeError, AssertionError):
        return "Something went wrong"
    except OverflowError:
        return "What's wrong with you?"


handler_class = RemindMoiHandler
