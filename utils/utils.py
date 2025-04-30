from aiogram.types import Message


# Функция для фильтра, который определяет, правильный ли тип запоминаемого сообщения:
# текст, фото, гифка, видео, кружочек, аудиозапись, голос или стикер
def content_type_filter(message: Message) -> bool | dict[str, any]:
    reply: Message | None = message.reply_to_message
    if reply:
        # если тип сообщения соответствует одному из указанных,
        # то в content будет записано содержимое соответствующего поля сообщения
        content = (reply.text or reply.photo or reply.animation or reply.voice or
                   reply.video or reply.sticker or reply.video_note or reply.audio)
        # если content не пустой, то функция вернет его содержимое,
        # которое нужно будет использовать в хендлере
        if content:
            return {'content': content}
        return False
    else:
        return False


def convert_command_to_cw_hyperlink(entities: list, content: str) -> str:
    """Заменяет команды на гиперссылки на CW."""
    new_content: str = content
    cw_link_template = "https://t.me/chtwrsbot?text="
    for entity in entities:
        start: int = entity.offset
        end: int = entity.offset + entity.length
        command: str = content[start:end]
        if entity.type == 'bot_command':
            cw_link: str = f"<a href='{cw_link_template + command}'>{command}</a>"
            new_content = new_content.replace(command, cw_link)

    return new_content
