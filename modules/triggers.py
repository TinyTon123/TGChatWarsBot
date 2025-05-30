import redis
from aiogram import F, html, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from utils.utils import content_type_filter, convert_command_to_cw_hyperlink

redis_db: redis = redis.Redis(db=1)
router: Router = Router()


# хендлер для сохранения триггера
@router.message(Command(commands=["add_trigger"]), content_type_filter)
async def save_trigger(message: Message, content: any, command: CommandObject) -> None:
    if command.args:
        trigger_name = command.args.lower().replace('ё', 'е')
        # Если тип запоминаемого сообщения — текст, то в БД вносится пара ключ-значение
        # по шаблону <id чата>_<имя триггера>: <текст сообщения, в ответ на которое дана команда>
        if isinstance(content, str):
            entities = message.reply_to_message.entities
            # Если есть сущности, то с помощью функции ищем среди них тип "bot_command" и
            # заменяем на гиперссылки
            if entities:
                content = convert_command_to_cw_hyperlink(entities, content)
            redis_db.set(f"{message.chat.id}_{trigger_name}", f"{content}")

        # Если тип запоминаемого сообщения — фотография или картинка, то в переменную content
        # будет записан список из трех элементов, каждый из которых содержит поле file_id.
        # Вносим в БД пару ключ-значение по шаблону
        # <id чата>_<имя триггера>: <photo> _|_ <значение file_id> _|_ <подпись к фото/картинке>
        elif isinstance(content, list):
            redis_db.set(f"{message.chat.id}_{trigger_name}",
                  f"photo _|_ {content[-1].file_id} _|_ {message.reply_to_message.caption}")

        # Если тип сообщения любой другой из допустимых, то в БД добавляем запись по шаблону
        # <id чата>_<имя триггера>: <тип сообщения> _|_ <значение file_id> _|_ <подпись к фото/картинке>
        else:
                                                                    # костыль для перевода
                                                                    # 'VideoNote' в 'video_note'
            content_type_str = str(type(content)).split('.')[-1][:-2].replace('N', '_n').lower()
            redis_db.set(f"{message.chat.id}_{trigger_name}",
                  f"{content_type_str} _|_ {content.file_id} _|_ {message.reply_to_message.caption}")

        # Отправляем сообщение, что новый триггер успешно добавлен
        await message.answer(f'Триггер <code>{html.quote(f"{trigger_name}")}</code> добавлен')

    else:
        await message.answer(f"После команды необходимо указать название триггера")


# Хендлер для удаления триггера
@router.message(Command(commands=["del_trigger"]))
async def delete_trigger(message: Message, command: CommandObject) -> None:
    # Если после команды /del_tigger есть имя триггера, то БД пытается удалить
    # соответствующую строку
    if command.args:
        trigger_name = command.args.lower().replace('ё', 'е')
        deleted: int = redis_db.delete(f"{message.chat.id}_{trigger_name}")

        # В случае, если такой ключ в БД был, в переменную deleted будет записана единица,
        # в ином случае — ноль
        if deleted:
            # Отправляем сообщение, что триггер успешно удален
            await message.answer(f'Триггер <code>{html.quote(f"{trigger_name}")}</code> удален')
        else:
            # Отправляем сообщение, что такого триггера не было
            await message.answer(f'Такого триггера не было, но я его на всякий случай удалил {html.quote(">.<")}')

    # Если пользователь не указал имя триггера, бот не поймет, что именно нужно удалить
    else:
        await message.answer('Что удаляем? Укажите название триггера')


# Хендлер для отображения списка триггеров
@router.message(Command(commands=["show_triggers"]))
async def show_triggers(message: Message) -> None:
    # Создаем кортеж со всеми ключами, которые соответствуют шаблону
    # <id чата, в котором вызывают команду_*>.
    # Метод scan возвращает количество найденных ключей и их список.
    triggers: set = {i.decode("utf-8") for i in redis_db.scan(match=f'{message.chat.id}_*', count=1000)[1]}

    # Выстраиваем ключи построчно и отвечаем пользователю
    text: str = 'Список триггеров:\n\n'
    for trigger in triggers:
        text += f'<code>{trigger[trigger.find("_")+1:]}</code>\n'

    await message.answer(text)


# Хендлер для отображения триггера
@router.message(F.text)
async def display_trigger(message: Message) -> None:
    # Переводим текст в байтовую строку и ищем в БД соответствующий ключ
    # по шаблону <id чата>_<имя триггера>
    chat_trigger: bytes = f'{message.chat.id}_{message.text.lower().replace("ё", "е").strip(".")}'.encode("utf-8")
    if chat_trigger in redis_db.scan(match=f'{message.chat.id}_*', count=1000)[1]:

        # Если ключ найден, то вытаскиваем его значение и делим строку по комбинации символов ' _|_ '
        trigger_text: str = redis_db.get(chat_trigger).decode("utf-8")
        trigger_text: list[str] = trigger_text.split(' _|_ ')

        # Если значение ключа не текст, то вернется список по шаблону
        # ['<тип сообщения>', '<file_id контента>', '<caption> (или None, если подписи к контенту не было)']
        if len(trigger_text) > 1:
            # Из списка формируем метод ответа по шаблону message.answer_<тип сообщения>,
            # и передаем ему file_id, а также caption, если он неравен None
            await (getattr(message, f"answer_{trigger_text[0]}")
                   (trigger_text[1], caption=trigger_text[2] if trigger_text[2] != 'None' else ''))

        # Если значение ключа — это текст, то им и отвечаем, предварительно распаковав список,
        # образовавшийся после метода .split(' _|_ ') выше
        else:
            await message.answer(*trigger_text, disable_web_page_preview=True)
