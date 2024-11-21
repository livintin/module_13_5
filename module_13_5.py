from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text="Рассчитать")
button2 = KeyboardButton(text="Информация")
kb.row(button, button2)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


@dp.message_handler(text="Привет!")
async def urban_message(message):
    await message.answer('Введите команду /start, чтобы начать общение')


@dp.message_handler(commands=['start'])
async def urban_message(message):
    print("Start")
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text="Информация")
async def set_gender(message):
    await message.answer(f"Бот, который помогает пользователю рассчитывать норму калорий "
                         f"в зависимости от его пола, возраста, роста и веса")


@dp.message_handler(text="Рассчитать")
async def set_gender(message):
    await message.answer(f"Для корректного расчета калорий, укажите свой пол (F/M):")
    await UserState.gender.set()


@dp.message_handler(state=UserState.gender)
async def set_age(message, state):
    gender = message.text.upper()
    if gender not in ['F', 'M']:
        await message.answer("Пожалуйста, укажите корректный пол (F/M):")
        return
    await state.update_data(gender=gender)
    await message.answer("Введите свой возраст:")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    try:
        await state.update_data(age=int(message.text))
        await message.answer(f"Введите свой рост:")
        await UserState.growth.set()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст числом:")


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    try:
        await state.update_data(growth=float(message.text))
        await message.answer(f"Введите свой вес:")
        await UserState.weight.set()
    except ValueError:
        await message.answer(f"Пожалуйста, введите корректный рост числом:")


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    try:
        await state.update_data(weight=float(message.text))
        data = await state.get_data()
        if data['gender'] == 'M':
            await message.answer(
                f"Ваша норма калорий {10 * data['weight'] + 6.25 * data['growth'] + 5 * data['age'] + 5}")
            await state.finish()
        else:
            await message.answer(
                f"Ваша норма калорий {10 * data['weight'] + 6.25 * data['growth'] + 5 * data['age'] - 161}")
            await state.finish()
    except ValueError:
        await message.answer(f"Пожалуйста, введите корректный вес числом:")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
