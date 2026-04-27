from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def get_main_keyboard():
    keyboard = VkKeyboard(one_time=True)
    # Payload - это словарь, который бот получит при клике
    keyboard.add_button("Генерация картинки", color=VkKeyboardColor.PRIMARY, payload={"action": "image_gen"})
    keyboard.add_button("Статистика сообщества", color=VkKeyboardColor.PRIMARY, payload={"action": "statistics"})
    keyboard.add_button("Загадка дня", color=VkKeyboardColor.PRIMARY, payload={"action": "quiz"})
    return keyboard.get_keyboard()