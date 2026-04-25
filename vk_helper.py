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
