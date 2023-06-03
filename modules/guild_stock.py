
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext

router: Router = Router()

resources: tuple = (
    '01 Thread',
    '02 Stick',
    '03 Pelt',
    '04 Bone',
    '05 Coal',
    '06 Charcoal',
    '07 Powder',
    '08 Iron ore',
    '09 Cloth',
    '10 Silver ore',
    '11 Bauxite',
    '12 Cord',
    '13 Magic stone',
    '14 Wooden shaft',
    '15 Sapphire',
    '16 Solvent',
    '17 Ruby',
    '18 Hardener',
    '19 Steel',
    '20 Leather',
    '21 Bone powder',
    '22 String',
    '23 Coke',
    '24 Purified powder',
    '25 Silver alloy',
    '27 Steel mold',
    '28 Silver mold',
    '29 Blacksmith frame',
    '30 Artisan frame',
    '31 Rope',
    '32 Silver Frame',
    '33 Metal plate',
    '34 Metallic fiber',
    '35 Crafted leather',
    '36 Quality Cloth',
    '37 Blacksmith mold',
    '38 Artisan mold'
    )


# Создаем экземпляры класса State, последовательно
# перечисляя возможные состояния, в которых будет находиться
# бот в разные моменты взаимодейтсвия пользователей с ним
class FSMFillForm(StatesGroup):
    send_new_stock: State = State()  # Состояние ожидания ввода нового списка ресурсов


# функция для преобразования входящего сообщения в словарь названий ресурсов и их количества
def process_stock_into_dict(message: Message) -> dict[str, int]:
    # Обрабатываем полученный список ресурсов:
    # делаем список из строк;
    initial_stock_list: list[str] = message.text.split('\n')
    # создаем словарь с названием и количеством ресурсов.
    initial_stock_dict: dict[str, int] = {i.split(' x ')[0]: int(i.split(' x ')[1]) for i in initial_stock_list[1:]}
    # Возвращаем получившийся словарь в хранилище.
    return initial_stock_dict


@router.message(F.forward_from.id == 408101137, F.text.startswith('Guild Warehouse: '),
                StateFilter(default_state))
async def get_initial_stock(message: Message, state: FSMContext) -> None:
    # Сохраняем в хранилище результат преобразования стока в словарь.
    await state.update_data(initial_stock=process_stock_into_dict(message))
    await message.answer(text='Ресурсы записаны.\n\nНе забудьте скинуть новый сток!')
    # Переводим состояние FSM в ожидание обновленного списка ресурсов
    await state.set_state(FSMFillForm.send_new_stock)


@router.message(F.forward_from.id == 408101137, F.text.startswith('Guild Warehouse: '),
                StateFilter(FSMFillForm.send_new_stock))
async def get_new_stock(message: Message, state: FSMContext):
    await state.update_data(new_stock=process_stock_into_dict(message))
    stocks: dict[str, any] = await state.get_data()

    resulting_resources: dict[str, int] = dict()
    for key in resources:
        resulting_resources[key] = stocks['new_stock'].get(key, 0) - stocks['initial_stock'].get(key, 0)

    if any(resulting_resources.values()):
        plus_resources: list[str] = [f'{k}: +{v}\n' for k, v in resulting_resources.items() if v > 0]
        minus_resources: list[str] = [f'{k}: {v}\n' for k, v in resulting_resources.items() if v < 0]
        text = 'Изменения в стоке:\n\n➕\n\n'
        if plus_resources:
            for i in plus_resources:
                text += i
        else:
            text += 'Гильдия ничего не заработала!\n\n'
        text += '\n➖\n\n'
        if minus_resources:
            for i in minus_resources:
                text += i
        else:
            text += 'Гильдия ничего не потеряла!'
    else:
        text = 'Без изменений'

    await message.answer(text)
    await state.clear()
