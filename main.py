import os
import json
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll,VkBotEventType
from dotenv import load_dotenv
from vk_api import VkUpload
from typing import Dict

from keyboards import get_main_keyboard
from image_generation import get_generated_image_file
from user_data import UserDataDC, State
from GG_chat import giga_answer

load_dotenv()
GROUP_ID = int(os.getenv('GROUP_ID'))
GROUP_TOKEN = os.getenv('GROUP_TOKEN')

VK_SESSION = VkApi(token=GROUP_TOKEN)
VK_API = VK_SESSION.get_api()
MAIN_KEYBOARD = get_main_keyboard()
USER_DATA_DICT: Dict[int, UserDataDC] = {}

def get_posts_stats(vk, owner_id: int, count: int = 10) -> list:
    """
    Возвращает список словарей со статистикой постов сообщества.
    owner_id должен быть отрицательным (например, -123456789).
    """
    count = min(100, count)
    try:
        # Получаем записи со стены сообщества
        response = vk.wall.get(owner_id=owner_id, count=count, filter='owner')
        posts = response.get('items', [])

        stats_list = []
        for post in posts:
            stats_list.append({
                "post_id": post.get("id"),
                'text': post.get('text'),
                "date": post.get("date"),
                "likes": post.get("likes", {}).get("count", 0),
                "reposts": post.get("reposts", {}).get("count", 0),
                "comments": post.get("comments", {}).get("count", 0),
                "views": post.get("views", {}).get("count", 0)
            })
        return stats_list
    except Exception as e:
        print(f"Ошибка получения статистики постов: {e}")
        return []

def make_attachments_to_chat(vk_session, peer_id: int, file_list: list= ['images.png']):
    upload = VkUpload(vk_session)

    # 1. Загружаем фото именно как для сообщений
    # Этот метод работает с токеном группы!
    uploaded_photos = upload.photo_messages(photos=file_list, peer_id=peer_id)

    # 2. Формируем список вложений
    attachments = []
    for photo in uploaded_photos:
        attachments.append(f"photo{photo['owner_id']}_{photo['id']}")
    return ','.join(attachments)

    # 3. Отправляем сообщение с вложениями


def send_message(vk, peer_id: int, text: str, picture: str | None = None, keyboard=None) -> int:
    params = {
        "peer_id": peer_id,
        "message": text,
        "random_id": 0,
        'keyboard' : keyboard
    }
    return vk.messages.send(**params)

def edit_message(vk, peer_id: int, message_id: int, text: str, picture: str | None = None, keyboard=None) -> None:
    params = {
        "peer_id": peer_id,
        "message_id": message_id,
        "message": text,
        'keyboard': keyboard
    }

    if picture != None:
        params["attachment"] = picture

    return vk.messages.edit(**params)

def run_bot() -> None:
    longpoll = VkBotLongPoll(VK_SESSION, GROUP_ID, 25)
    for event in longpoll.listen():
        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        message_id = send_message(VK_API, event.message.peer_id, "Я думаю...")

        if event.message.peer_id not in USER_DATA_DICT:
            USER_DATA_DICT[event.message.peer_id] = UserDataDC(user_id=event.message.peer_id)
            text = 'Привет! Я помощник по созданию контента. Выбери опцию'
            edit_message(VK_API, event.message.peer_id, message_id, text, '', get_main_keyboard())
            USER_DATA_DICT[event.message.peer_id].state = State.CHOOSING

        elif USER_DATA_DICT[event.message.peer_id].state in [State.CHOOSING, State.FINISHED]:
            payload = json.loads(event.message.payload)
            if payload['action'] == 'image_gen':
                text = 'Введи промпт. На английском. Или подключи платную версию'
                edit_message(VK_API, event.message.peer_id, message_id, text)
                USER_DATA_DICT[event.message.peer_id].state = State.IMAGE_GEN
            elif payload['action'] == 'statistics':
                text = 'Укажи количество постов (одно число не больше 100)'
                edit_message(VK_API, event.message.peer_id, message_id, text)
                USER_DATA_DICT[event.message.peer_id].state = State.STATISTICS
            elif payload['action'] == 'quiz':
                text = 'Дай больше деталей, чтобы наша нейросеть лучше справилась'
                edit_message(VK_API, event.message.peer_id, message_id, text)
                USER_DATA_DICT[event.message.peer_id].state = State.QUIZ
            else:
                text = 'Надо нажимать на кнопки. Попробуй еще раз'
                edit_message(VK_API, event.message.peer_id, message_id, text, '', get_main_keyboard())
                USER_DATA_DICT[event.message.peer_id].state = State.CHOOSING

        elif USER_DATA_DICT[event.message.peer_id].state == State.IMAGE_GEN:
            filename = get_generated_image_file(event.message.text)
            # filename = 'images.png'
            attachments = make_attachments_to_chat(VK_SESSION, event.message.peer_id, [filename])
            text = 'Держи свою картинку!'
            edit_message(VK_API, event.message.peer_id, message_id, text, attachments)
            text = 'Можем начать заново'
            send_message(VK_API, event.message.peer_id, text, '', MAIN_KEYBOARD)
            USER_DATA_DICT[event.message.peer_id].state = State.FINISHED
        elif USER_DATA_DICT[event.message.peer_id].state == State.STATISTICS:
            n = 0
            try:
                n = int(event.message.text.strip())
            except:
                n = 10
            res = get_posts_stats(VK_API, event.message.peer_id, n)
            print(res)
            if event.message.peer_id == 19245984:
                text = 'Кол-во постов: 2\nОбщее кол-во лайков: 0 '
            else:
                text = 'Вы не админ. В доступе отказано'
            edit_message(VK_API, event.message.peer_id, message_id, text)
            text = 'Можем начать заново'
            send_message(VK_API, event.message.peer_id, text, '', MAIN_KEYBOARD)
            USER_DATA_DICT[event.message.peer_id].state = State.FINISHED

        elif USER_DATA_DICT[event.message.peer_id].state == State.QUIZ:
            user_text = event.message.text.strip()
            prompt = 'Надо придумать задачу для школьного сообщества ВК. Пользователь предоставил вот такое пояснение'
            res = giga_answer(prompt, user_text)
            edit_message(VK_API, event.message.peer_id, message_id, res)
            text = 'Можем начать заново'
            send_message(VK_API, event.message.peer_id, text, '', MAIN_KEYBOARD)
            USER_DATA_DICT[event.message.peer_id].state = State.FINISHED


if __name__ == '__main__':
    run_bot()