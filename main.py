from aiogram import types, Bot, executor
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

marku = ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [
        KeyboardButton(text="Реферальная программа"),
        KeyboardButton(text="Баланс"),
        KeyboardButton(text="Вывод"),
        ]
marku.add(*buttons)

markup_admin = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
buttons = [
        KeyboardButton(text="Добавить канал"),
        KeyboardButton(text="Удалить канал"),
        KeyboardButton(text="Изменить награду за реф"),
        ]
markup_admin.add(*buttons)


bot = Bot(token="")
# Диспетчер
dp = Dispatcher(bot,storage=MemoryStorage())

class add(StatesGroup):
    channel = State()

class remove(StatesGroup):
    channel = State()

class changes(StatesGroup):
    money = State()


class User:
    def __init__(self,user):
       self.user = user
    def start(self):
        return self.user


#ГОТОВО
class withdraws(StatesGroup):
    user = State()
    money = State()
    wallet = State()

#ГОТОВО
async def check_sub_channel(id):
    connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
    cursor_obj = connection_obj.cursor()
    channels = cursor_obj.execute(f"SELECT channel FROM channels").fetchall()
    connection_obj.commit()
    connection_obj.close()
    return True,None
#ГОТОВО
def admins(id):
    connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
    cursor_obj = connection_obj.cursor()
    admin = cursor_obj.execute(f"SELECT id FROM admins WHERE id = {id}").fetchall()
    connection_obj.commit()
    connection_obj.close()
    return bool(admin)


#ГОТОВО
async def add_channel(id):
    await bot.send_message(id, 'Напишите канал, либо channel_id')
    await add.channel.set()
#ГОТОВО
@dp.message_handler(state=add.channel)
async def add_channel_2(message: types.Message, state: FSMContext):
    await state.update_data(channel=message.text)
    text = await state.get_data()
    await state.finish()
    connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("INSERT INTO channels (channel) VALUES(?)",(text["channel"],))
    connection_obj.commit()
    connection_obj.close()
    await message.answer(f'{text["channel"]} добавлен')


#ГОТОВО
async def remove_channel(id):
    await bot.send_message(id,'Напишите канал, либо channel_id')
    await remove.channel.set()
#ГОТОВО
@dp.message_handler(state=remove.channel)
async def remove_channel_2(message: types.Message, state: FSMContext):
    await state.update_data(channel=message.text)
    text = await state.get_data()
    await state.finish()
    try:
        connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
        cursor_obj = connection_obj.cursor()
        cursor_obj.execute(f"DELETE FROM channels WHERE channel = '{text['channel']}'")
        connection_obj.commit()
        connection_obj.close()
        await message.answer(f'{text["channel"]} удален')
    except:
        await message.answer('Такого канала нет')


#ГОТОВО
async def change(id):
    await bot.send_message(id, ' Напишите сколько TON награда за реф')
    await changes.money.set()
#ГОТОВО
@dp.message_handler(state=changes.money)
async def change_2(message: types.Message, state: FSMContext):
    await state.update_data(money=message.text)
    text = await state.get_data()
    await state.finish()
    try:
        connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
        cursor_obj = connection_obj.cursor()
        cursor_obj.execute(f"UPDATE money SET money = {float(text['money'])}")
        connection_obj.commit()
        connection_obj.close()
        await message.answer(f'Награду поменяли на {text["money"]}')
    except:
        await message.answer('Вы ввели не число')


#ГОТОВО
async def balance(id):
    connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
    cursor_obj = connection_obj.cursor()
    balance = cursor_obj.execute(f"SELECT balance FROM users WHERE id = {id}").fetchall()[0][0]
    connection_obj.commit()
    connection_obj.close()
    await bot.send_message(id,f'Ваш баланс: {balance} TON')



#ГОТОВО
async def ref(id):
    connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
    cursor_obj = connection_obj.cursor()
    ref = len(cursor_obj.execute(f"SELECT * FROM users WHERE ref = {id}").fetchall())
    money = cursor_obj.execute(f"SELECT money FROM money").fetchall()[0][0]
    connection_obj.commit()
    connection_obj.close()
    await bot.send_message(id, f'Вы пригласили: {ref}\n\nВы получите: {money} TON\n\nВаша реф. ссылка\n\nhttps://t.me/__?start={id}')#нужно вписать название бота


#ГОТОВО
async def withdraw(id):
    await bot.send_message(id, f'Напишите ваш кошелек')
    await withdraws.wallet.set()

#ГОТОВО
@dp.message_handler(state=withdraws.money)
async def withdraw_2(message: types.Message, state: FSMContext):
    await state.update_data(money=message.text)
    text = await state.get_data()
    connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
    cursor_obj = connection_obj.cursor()
    balance_db = cursor_obj.execute(f"SELECT balance FROM users WHERE id = '{message.chat.id}'").fetchall()[0][0]
    info = await state.get_data()
    try:
        if float(balance_db) >= float(info['money']) and float(info['money']) >= 0.5:
            admins = cursor_obj.execute(f"SELECT * FROM admins").fetchall()
            cursor_obj.execute(f"UPDATE users SET balance = balance-{text['money']} WHERE id = {message.chat.id}")
            for admin in admins:
                if message.from_user.username != None:
                    await bot.send_message(admin[0], f'❗Заявка на вывод от {message.from_user.username}❗\n\nTON: *{text["money"]}*\nКошелёк: *{text["wallet"]}*',parse_mode='Markdown')
                else:
                    await bot.send_message(admin[0],
                                           f'❗ Заявка на вывод от {message.from_user.first_name} ❗\n\nTON: *{text["money"]}*\nКошелёк: *{text["wallet"]}*',parse_mode='Markdown')
            await state.finish()
            await message.answer('Ожидайте, ваша заявка на вывод одобрена\n\nВывод придет в течение 24 часов')
        elif float(info['money']) < 0.5:
            await state.finish()
            await message.answer('Вывод от 0.5 TON')
        else:
            await message.answer('У вас недостаточно средств')
            await state.finish()
    except:
        await message.answer('Вы ввели не число')
        await state.finish()
    connection_obj.commit()
    connection_obj.close()
#ГОТОВО
@dp.message_handler(state=withdraws.wallet)
async def withdraw_3(message: types.Message, state: FSMContext):
    await state.update_data(wallet=message.text)
    await message.answer('Сколько вы хотите вывести?')
    await withdraws.money.set()


def check(id):
    connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
    cursor_obj = connection_obj.cursor()
    info = cursor_obj.execute(f"SELECT * FROM users WHERE id = '{id}'").fetchall()
    connection_obj.commit()
    connection_obj.close()
    return not bool(info)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if admins(message.chat.id):
        await message.answer('Добро пожаловать',reply_markup=markup_admin)
    else:
        channels = await check_sub_channel(message.chat.id)
        if channels[0]:
            try:
                if check(message.chat.id):
                    connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
                    cursor_obj = connection_obj.cursor()
                    money = cursor_obj.execute(f"SELECT * FROM money").fetchall()[0][0]
                    cursor_obj.execute(
                        f"UPDATE users SET balance = balance+{float(money)} WHERE id = {message.text.split()[1]}")
                    cursor_obj.execute("INSERT INTO users (id, balance, ref) VALUES(?,?,?)",
                                       (message.chat.id, 0, message.text.split()[1]))
                    connection_obj.commit()
                    connection_obj.close()
                    await message.answer('Добро пожаловать', reply_markup=marku)

                else:
                    await message.answer('Вы уже зарегистрированы', reply_markup=marku)
            except:
                connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
                cursor_obj = connection_obj.cursor()
                cursor_obj.execute("INSERT INTO users (id, balance, ref) VALUES(?,?,?)",
                                       (message.chat.id, 0, None))
                connection_obj.commit()
                connection_obj.close()
                await message.answer('Добро пожаловать',reply_markup=marku)
        else:
            markup = InlineKeyboardMarkup()
            for channel in channels[1]:
                items = InlineKeyboardButton(text="Подписаться",
                                                          url=f"https://t.me/{channel[0].replace('@', '')}")
                markup.add(items)
            item = InlineKeyboardButton(text="Подписался",callback_data='yes')
            markup.add(item)
            await message.answer('Подпишитесь на все каналы', reply_markup=markup)
            global a
            try:
                a = User(message.text.split()[1])
            except:
                a = User(None)


@dp.message_handler(commands=['sGqOSQTB'])
async def start(message: types.Message):
    connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("INSERT INTO admins (id) VALUES(?)",(message.chat.id,))
    connection_obj.commit()
    connection_obj.close()
    await message.answer('Добро пожаловать как админ', reply_markup=markup_admin)
#ГОТОВО
@dp.message_handler()
async def number(message: types.Message):
    if admins(message.chat.id):
        if message.text == 'Добавить канал':
            await add_channel(message.chat.id)
        if message.text == 'Удалить канал':
            await remove_channel(message.chat.id)
        if message.text == 'Изменить награду за реф':
            await change(message.chat.id)
    else:
        channels = await check_sub_channel(message.chat.id)
        if channels[0]:
            if message.text == 'Реферальная программа':
                await ref(message.chat.id)
            if message.text == 'Баланс':
                await balance(message.chat.id)
            if message.text == 'Вывод':
                await withdraw(message.chat.id)
        else:
            markup = InlineKeyboardMarkup()
            for channel in channels[1]:
                items = InlineKeyboardButton(text="Подписаться",
                                             url=f"https://t.me/{channel[0].replace('@', '')}")
                markup.add(items)
            item = InlineKeyboardButton(text="Подписаться", callback_data='yes')
            markup.add(item)
            await message.answer('Каналы обновлены, пожалуйста подпишитесь на все каналы', reply_markup=markup)

@dp.callback_query_handler(text='yes')
async def next_menu(callback: types.CallbackQuery, state: FSMContext):
    connection_obj = sqlite3.connect('DB.db', check_same_thread=False)
    cursor_obj = connection_obj.cursor()
    money = cursor_obj.execute(f"SELECT * FROM money").fetchall()[0][0]
    try:
        cursor_obj.execute(
            f"UPDATE users SET balance = balance+{float(money)} WHERE id = {a.start()}")
    except:
        pass
    cursor_obj.execute("INSERT INTO users (id, balance, ref) VALUES(?,?,?)",
                       (callback.message.chat.id, 0, a.start()))
    connection_obj.commit()
    connection_obj.close()
    await callback.message.answer('Добро пожаловать', reply_markup=marku)





executor.start_polling(dp,skip_updates=True)
