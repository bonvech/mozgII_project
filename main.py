import os
import traceback
import requests
import tempfile
import base64
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll,VkBotEventType
from dotenv import load_dotenv
from tool_handle import handle


load_dotenv()
group_id = os.getenv('GROUP_ID')
group_token = os.getenv('GROUP_TOKEN')

def upload_photo_to_vk(vk, image_url: str, peer_id: int) -> str | None:
    try:
        if image_url.startswith("data:"):
            header, data = image_url.split(",", 1)
            image_data = base64.b64decode(data)
            ext = "png" if "png" in header else "jpg"
        else:
            resp = requests.get(image_url, timeout=30)
            if resp.status_code != 200:
                return None
            image_data = resp.content
            ext = "jpg"

        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            tmp.write(image_data)
            tmp_path = tmp.name

        upload_url = vk.photos.getMessagesUploadServer(peer_id=peer_id)["upload_url"]

        with open(tmp_path, "rb") as f:
            files = {"photo": f}
            resp = requests.post(upload_url, files=files, timeout=30)

        os.remove(tmp_path)
        result = resp.json()

        if "photo" not in result:
            return None

        saved = vk.photos.saveMessagesPhoto(
            photo=result["photo"],
            server=result["server"],
            hash=result["hash"]
        )[0]

        return f"photo{saved['owner_id']}_{saved['id']}"
    except Exception as e:
        print(f"Ошибка загрузки фото: {e}")
        return None


def send_message(vk, peer_id: int, text: str, picture: str | None = None) -> int:
    params = {
        "peer_id": peer_id,
        "message": text,
        "random_id": 0,
    }

    if picture:
        if picture.startswith("http") or picture.startswith("data:"):
            attachment = upload_photo_to_vk(vk, picture, peer_id)
            if attachment:
                params["attachment"] = attachment
            else:
                text += "\n(Не удалось загрузить изображение)"
        else:
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