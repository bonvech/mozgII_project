import os
import traceback
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll,VkBotEventType
from dotenv import load_dotenv
from tool_handle import handle


load_dotenv()
group_id = os.getenv('GROUP_ID')
group_token = os.getenv('GROUP_TOKEN')

def send_message(vk, peer_id: int, text: str, picture: str | None = None) -> int:
    params = {
        "peer_id": peer_id,
        "message": text,
        "random_id": 0,
    }

    if picture != None:
        params["attachment"] = picture

    return vk.messages.send(**params)

def edit_message(vk, peer_id: int, message_id: int, text: str, picture: str | None = None) -> None:
    params = {
        "peer_id": peer_id,
        "message_id": message_id,
        "message": text,
    }

    if picture != None:
        params["attachment"] = picture

    return vk.messages.edit(**params)


def run_bot() -> None:
    vk_session = VkApi(token=group_token)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id, 25)
    for event in longpoll.listen():
        if event.type != VkBotEventType.MESSAGE_NEW:
            continue
        try:
            res = handle(event.message['text'], event.message.peer_id)
            if res is None:
                print("Ошибка: handle вернул None")
                send_message(vk, event.message.peer_id, "Произошла ошибка")
            else:
                send_message(vk, event.message.peer_id, res[0], res[1])
        except Exception as e:
            traceback.print_exc()
            send_message(vk, event.message.peer_id, f"Ошибка: {e}")


run_bot()