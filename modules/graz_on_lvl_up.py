from aiogram import F, Router, types

router: Router = Router()

@router.message(
    F.forward_from.id == 408101137,
    F.sticker.set_name.in_({'ChatwarsLevels', 'ChatwarsLevelsF'})
)
async def msg(message: types.Message) -> None:
    """Поздравляет с левел-апом."""
    await message.answer('Грацы!')
