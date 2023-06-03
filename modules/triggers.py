
from aiogram.filters import Command, CommandObject
from aiogram import Router, F, html
from aiogram.types import Message

import redis

r: redis = redis.Redis(db=1)
router: Router = Router()


# фильтр для определения того, правильный ли тип запоминаемого сообщения:
# текст, фото, гифка, видео, кружочек, аудиозапись, голос или стикер
def content_type_filter(message: Message) -> bool | dict[str, any]:
    reply: Message | None = message.reply_to_message
    if reply:
        content = (reply.text or reply.photo or reply.animation or reply.voice or
                   reply.video or reply.sticker or reply.video_note or reply.audio)
        if content:
            return {'content': content}
        return False
    else:
        return False


@router.message(Command(commands=["add_trigger"]), content_type_filter)
async def display_trigger(message: Message, content: any, command: CommandObject) -> None:
    if command.args:
        r.delete(f"{message.chat.id}_{command.args}")

        if isinstance(content, str):
            r.set(f"{message.chat.id}_{command.args}", f"{content}")

        elif isinstance(content, list):
            r.set(f"{message.chat.id}_{command.args}",
                  f"photo _|_ {content[-1].file_id} _|_ {message.reply_to_message.caption}")

        else:
            content_type_str = str(type(content)).split('.')[-1][:-2].replace('N', '_n').lower()  # костыль для перевода 'VideoNote' в 'video_note'
            r.set(f"{message.chat.id}_{command.args}",
                  f"{content_type_str} _|_ {content.file_id} _|_ {message.reply_to_message.caption}")

        await message.answer(f'Триггер <code>{html.quote(f"{command.args}")}</code> добавлен')

    else:
        await message.answer(f"После команды необходимо указать название триггера")


@router.message(Command(commands=["del_trigger"]))
async def delete_trigger(message: Message, command: CommandObject) -> None:
    if command.args:
        deleted: int = r.delete(f"{message.chat.id}_{command.args}")

        if deleted:
            await message.answer(f'Триггер {html.quote(f"{command.args}")} удален')
        else:
            await message.answer(f'Такого триггера не было, но я его на всякий случай удалил {html.quote(">.<")}')

    else:
        await message.answer('Что удаляем? Укажите название триггера')


@router.message(Command(commands=["show_triggers"]))
async def show_triggers(message: Message) -> None:
    triggers: set = {i.decode("utf-8") for i in r.scan(match=f'{message.chat.id}_*')[1]}

    text: str = 'Список триггеров:\n\n'
    for trigger in triggers:
        text += f'{trigger[trigger.find("_")+1:]}\n'

    await message.answer(text)


@router.message(F.text)
async def display_trigger(message: Message) -> None:
    chat_trigger: bytes = f'{message.chat.id}_{message.text}'.encode("utf-8")
    if chat_trigger in r.scan(match=f'{message.chat.id}_*')[1]:

        trigger_text = r.get(chat_trigger).decode("utf-8")
        trigger_text = trigger_text.split(' _|_ ')

        if len(trigger_text) > 1:
            await (getattr(message, f"answer_{trigger_text[0]}")
                   (trigger_text[1], caption=trigger_text[2] if trigger_text[2] != 'None' else ''))

        else:
            await message.answer(*trigger_text)
