from aiogram.types import Message


def content_type_filter(message: Message) -> bool | dict[str, any]:
    """
    Проверяет, правильный ли тип запоминаемого сообщения:
    текст, фото, гифка, видео, кружочек, аудиозапись, голос или стикер.
    """
    message_to_reply: Message | None = message.reply_to_message
    # если тип сообщения соответствует одному из указанных,
    # то в content будет записано содержимое соответствующего поля сообщения
    content = (
            message_to_reply.text
            or message_to_reply.photo
            or message_to_reply.animation
            or message_to_reply.voice
            or message_to_reply.video
            or message_to_reply.sticker
            or message_to_reply.video_note
            or message_to_reply.audio
    )
    # если content не пустой, то функция вернет его содержимое,
    # которое нужно будет использовать в хендлере
    if content:
        return {'content': content}
    return False


def convert_command_to_cw_hyperlink(entities: list, content: str) -> str:
    """Заменяет команды на гиперссылки на CW."""
    new_content: str = content
    cw_link_template = "https://t.me/chtwrsbot?text="
    for entity in entities:
        command = entity.extract_from(content)
        if entity.type == 'bot_command':
            cw_link: str = f"<a href='{cw_link_template + command}'>{command}</a>"
            new_content = new_content.replace(command, cw_link)
        # на случай, если сообщение уже содержит гиперссылку на CW
        elif entity.type == 'text_link' and cw_link_template in entity.url:
            cw_link: str = f"<a href='{entity.url}'>{command}</a>"
            new_content = new_content.replace(command, cw_link)

    return new_content
