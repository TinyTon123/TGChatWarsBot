from aiogram import Router, F
from aiogram.types import Message

import re

router: Router = Router()

bottle_codes: dict[str, int] = {
    "фр": 1,
    "рагу": 1,
    "фулраш": 1,
    "фд": 4,
    "деф": 4,
    "пис": 4,
    "фулдеф": 4,
    "грид": 7,
    "натуру": 10,
    "ману": 13,
    "сумрак": 16,
    "морф": 19
}


def text_filter(message: Message) -> bool:
    regex: str = (r"дай (?:ф[рд]|рагу|деф|пис|фул(?:раш|деф)|морф|"
                  r"сумрак|ману|натуру|грид) [123456789]\d?")
    result: list | None= re.fullmatch(regex, message.text, flags=re.IGNORECASE)
    return bool(result)


@router.message(F.text, text_filter)
async def display_trigger(message: Message) -> None:
    command_split: list = message.text.split()
    bottle, amount = command_split[1], command_split[2]
    bottle_code: int = bottle_codes[bottle]
    await message.answer(f"/gw_p{bottle_code:0>2}_{amount}_p{bottle_code+1:0>2}_{amount}_p{bottle_code+2:0>2}_{amount}")
