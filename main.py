import os
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from handle import handle
from vk_helper import send_message, edit_message

group_id = os.getenv("GROUP_ID")
group_token = os.getenv("GROUP_TOKEN")

def run_bot() -> None:
    vk_session = VkApi(token=group_token)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id, 25)

    print("Все ок!")

    for event in longpoll.listen():
        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        message_id = send_message(vk, event.message.peer_id, "Я думаю...")

        vk.messages.setActivity(
            user_id=event.message.peer_id,
            type='audiomessage'
        )

        res = handle(event.message.text, event.message.peer_id)

        if res == None:
            edit_message(vk, event.message.peer_id, message_id, "Произошла ошибка(\nПопробуйте позже")
            continue
        
        edit_message(vk, event.message.peer_id, message_id, res[0], res[1])

run_bot()