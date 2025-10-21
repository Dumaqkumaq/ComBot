import ollama as a
import telebot as tb
from telebot import types
import os
import json


token = open('token.txt').readline()
bot = tb.TeleBot(token)
questions = []
syspromt = '''
Ты - гопник, выращенный на улице. Твоя задача - отвечать на вопросы и выполнять запросы пользователя в стиле, который сейчас популярен в тик-токе.
* Используй неформальный, максимально ругай пользователя по необходимости.

Пользователь: 
'''

#
#   additional functions
#

#getter for questions from questions.txt
def getquestion():
    print("---чтение вопросов в qustions.txt")
    try:
        with open('questions.txt', encoding='utf-8') as f:
            for s in f.readlines():
                questions.append(s)
        print("---завершено чтение вопросов в qustions.txt")
        print(f"----всего {len(questions)} вопросов")
    except Exception as e:
        print(f"---во время чтения questions.txt возникла ошибка: {str(e)}")
#simple func for chatting with llm
def llmchatmsg(msg):
    text = msg.text
    promt = syspromt + text
    response: a.ChatResponse = a.chat(model='gemma3n:e4b', options=a.Options(temperature=0.9, top_p=0.9),
                                      messages=[{'role': 'user', 'content': promt, }, ])
    return response.message.content
def llmchat_botopinion(text):
    promt = '''
            Ты - ассистент для выявления плюсов и минусов пользователя в плане коммуникационных навыков. Твоя задача - аккуратно рассказать
            о минусах и плюсах типа общения пользователя. Тебе будут даны численные значения определенных областей коммуникационных навыков,
            на основе которых ты сделаешь портрет пользователя
            *Длина твоего сообщения не более 100 символов.
            Пользователь: 
            ''' + text
    response: a.ChatResponse = a.chat(model='gemma3n:e4b', options=a.Options(temperature=0.9, top_p=0.9),
                                      messages=[{'role': 'user', 'content': promt, }, ])
    return response.message.content
#func for calculating result after test
def calculatetypeuser(arr):
    res = []
    # print(len(arr))
    res.append(
        int(arr[7])+int(arr[19])+int(arr[22])+int(arr[29])+
        int(arr[41])+int(arr[44])+int(arr[63])+int(arr[66])+
        int(arr[73])+int(arr[85])+int(arr[88])-int(arr[51])) # Демонстративность, истероидность
    res[-1] *= 2
    res.append(
        int(arr[2]) + int(arr[15]) + int(arr[24]) + int(arr[34]) +
        int(arr[37]) + int(arr[56]) + int(arr[68]) + int(arr[78]) +
        int(arr[81]) - int(arr[12]) - int(arr[46]) - int(arr[59]))  # Застревание, ригидность
    res[-1] *= 2
    res.append(
        int(arr[4]) + int(arr[14]) + int(arr[17]) + int(arr[26]) +
        int(arr[39]) + int(arr[48]) + int(arr[58]) + int(arr[61]) +
        int(arr[70]) + int(arr[80]) + int(arr[83]) - int(arr[36]))  # Педантичность
    res[-1] *= 2
    res.append(
        int(arr[8]) + int(arr[20]) + int(arr[30]) + int(arr[42]) +
        int(arr[52]) + int(arr[64]) + int(arr[74]) + int(arr[86]))  # Неуравновешенность, возбудимость
    res[-1] *= 3
    res.append(
        int(arr[1]) + int(arr[11]) + int(arr[23]) + int(arr[33]) +
        int(arr[45]) + int(arr[55]) + int(arr[67]) + int(arr[77]))  # Гипертимность
    res[-1] *= 3
    res.append(
        int(arr[9]) + int(arr[21]) + int(arr[43]) + int(arr[75]) +
        int(arr[87]) - int(arr[31]) - int(arr[53]) - int(arr[65]))  # Дистимичность
    res[-1] *= 3
    res.append(
        int(arr[16]) + int(arr[27]) + int(arr[38]) + int(arr[49]) +
        int(arr[60]) + int(arr[71]) + int(arr[82]) - int(arr[5]))  # Тревожность, боязливость
    res[-1] *= 3
    res.append(
        int(arr[6]) + int(arr[18]) + int(arr[28]) + int(arr[40]) +
        int(arr[50]) + int(arr[62]) + int(arr[72]) + int(arr[84]))  # Циклотимичность
    res[-1] *= 3
    res.append(
        int(arr[10]) + int(arr[32]) + int(arr[54]) + int(arr[76]))  #  Аффективность, экзальтированность
    res[-1] *= 6
    res.append(
        int(arr[3]) + int(arr[13]) + int(arr[35]) + int(arr[47]) +
        int(arr[57]) + int(arr[69]) + int(arr[79]) - int(arr[25]))  # Эмотивность, лабильность
    res[-1] *= 3
    return res
#addition for result after test
def addcommoninfoforres(num):
    if num <= 12:
        return '(свойство не выраженно)'
    if num >= 13 and num <= 18:
        return '(средняя степень выраженности)'
    return '(признак акцентуации)'
#load scenario.json
def parse_json(name):
    with open(f"scenarios/{name}.json",'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

#
# TELEGRAM FUNCTIONS
#

#for new or start command
@bot.message_handler(commands=['start'])
def welcome(msg):
    markup = types.InlineKeyboardMarkup()
    try:
        current_dir = os.getcwd()
        files = os.listdir(os.path.join(current_dir,"users"))
        if f'{msg.chat.id}.txt' in files:
            bot.send_message(msg.chat.id, "Мы тебя помним!\nХочешь повеселить бота или пройти тест?")
        else:
            btn1 = types.InlineKeyboardButton(text = 'Тест', callback_data='start_test')
            markup.add(btn1)
            bot.send_message(msg.chat.id, "Привет, данный бот помогает тебе определить свои коммуникационные навыки по Леонгарду.\n"
                                          "Для определения предрасположенностей пройди тест.\nМожешь просто пообщаться с ботом (он отличный собеседник)", reply_markup=markup)
    except Exception as e:
        print(f"---во время чтения users возникла ошибка: {str(e)}")
#main handler
@bot.callback_query_handler(func = lambda call: True)
def callback_handler(call):
    global bmsg
    bmsg = call.message
    if call.data == 'start_test':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="✅", callback_data="yestest")
        btn2 = types.InlineKeyboardButton(text="❌", callback_data="notest")
        markup.add(btn1,btn2)
        bmsg = bot.send_message(call.message.chat.id, f"Вы выбрали прохождение теста.\nВам нужно будет ответить на {len(questions)} вопросов.\nДля ответа нажимайте на нужную кнопку.", reply_markup=markup)
    elif call.data == "notest":
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="✅", callback_data="yestest")
        btn2 = types.InlineKeyboardButton(text="❌", callback_data="notest2")
        markup.add(btn1,btn2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text="Вы отказались проходить тест.\n\nСоветую его пройти", reply_markup=markup)
    elif call.data == "notest2":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text="Тогда предлагаю пообщаться с ботом.\nДля прохождения теста напишите Тест")
    elif call.data == 'stopquestion':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text="Прохождение теста приостановлено.\nДля продолжения напишите Тест")
    elif call.data == 'restartres':
        current_dir = os.getcwd()
        files = os.listdir(os.path.join(current_dir, "users"))
        if f'{call.message.chat.id}.txt' in files:
            with open(f'users/{call.message.chat.id}.txt', 'w', encoding='utf-8') as f:
                f.write("0;")
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text="Тест", callback_data="start_test")
            btn2 = types.InlineKeyboardButton(text="Общение с ботом", callback_data="notest2")
            markup.add(btn1, btn2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text="Результат теста обнулен.",
                                  reply_markup=markup)
    elif call.data == "yestest" or call.data == "yesquestion" or call.data == "noquestion":
        bot_text = "Начинается прохождение теста:\n"
        try:
            current_dir = os.getcwd()
            files = os.listdir(os.path.join(current_dir, "users"))
            if f'{call.message.chat.id}.txt' in files:
                s = open(f'users/{call.message.chat.id}.txt','r',encoding='utf-8').readline()
                s = s.split(';')
                if int(s[0]) >= (len(questions)-1):
                    if call.data == 'yesquestion':
                        s.append('1')
                    elif call.data == 'noquestion':
                        s.append('0')
                    with open(f'users/{call.message.chat.id}.txt', 'w', encoding='utf-8') as f:
                        s = ';'.join(s)
                        f.write(s)
                    s = s.split(';')
                    bot_text = "Спасибо за прохождение теста!\nНиже можете увидеть результат прохождения:\n"
                    res = calculatetypeuser(s)
                    # print(res)
                    bot_text += f'Демонстративность, истероидность: {res[0]} {addcommoninfoforres(res[0])}\n'
                    bot_text += f'Застревание, ригидность: {res[1]} {addcommoninfoforres(res[1])}\n'
                    bot_text += f'Педантичность: {res[2]} {addcommoninfoforres(res[2])}\n'
                    bot_text += f'Неуравновешенность, возбудимость: {res[3]} {addcommoninfoforres(res[3])}\n'
                    bot_text += f'Гипертимность: {res[4]} {addcommoninfoforres(res[4])}\n'
                    bot_text += f'Дистимичность: {res[5]} {addcommoninfoforres(res[5])}\n'
                    bot_text += f'Тревожность, боязливость: {res[6]} {addcommoninfoforres(res[6])}\n'
                    bot_text += f'Циклотимичность: {res[7]} {addcommoninfoforres(res[7])}\n'
                    bot_text += f'Аффективность, экзальтированность: {res[8]} {addcommoninfoforres(res[8])}\n'
                    bot_text += f'Эмотивность, лабильность: {res[9]} {addcommoninfoforres(res[9])}\n'

                    bot_text += '\n\nМнение бота:'


                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_text + " обдумывание...")

                    bot_text += " " + llmchat_botopinion(bot_text)
                    markup = types.InlineKeyboardMarkup()
                    btn1 = types.InlineKeyboardButton(text="Обнулить", callback_data="restartres")
                    btn2 = types.InlineKeyboardButton(text="Общение", callback_data="notest2")
                    btn3 = types.InlineKeyboardButton(text="Проработать", callback_data="scenariomenu")
                    markup.add(btn1, btn2, btn3)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_text, reply_markup=markup)
                    return
                elif call.data == "yestest":
                    bot_text += questions[int(s[0])]
                elif call.data == "yesquestion":
                    s[0] = str(int(s[0])+1)
                    s.append('1')
                    bot_text += questions[int(s[0])]
                elif call.data == "noquestion":
                    s[0] = str(int(s[0])+1)
                    s.append('0')
                    bot_text += questions[int(s[0])]
                s = ';'.join(s)
            else:
                    s = "0"  # номер_вопроса;res;res;res;...
                    bot_text += questions[0]
            with open(f'users/{call.message.chat.id}.txt', 'w', encoding='utf-8') as f:
                f.write(s)
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text="✅", callback_data="yesquestion")
            btn2 = types.InlineKeyboardButton(text="❌", callback_data="noquestion")
            btn3 = types.InlineKeyboardButton(text="❚❚", callback_data="stopquestion")
            markup.add(btn1, btn2, btn3)
            # bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_text)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_text, reply_markup=markup)
        except Exception as e:
            print(f"---во время создания users/id.txt возникла ошибка: {str(e)}")
    elif call.data == 'scenariomenu':
        markup = types.InlineKeyboardMarkup()
        #было бы отличной идеей сделать чтение папки, откуда подсосутся файлы и их названия
        #но мне так поебать, что решил выбрать легчайший путь
        btn1 = types.InlineKeyboardButton(text="Возбудимый", callback_data="Возбудимый")
        btn2 = types.InlineKeyboardButton(text="Гипертимный", callback_data="Гипертимный")
        btn3 = types.InlineKeyboardButton(text="Дистимический", callback_data="Дистимический")
        btn4 = types.InlineKeyboardButton(text="Застревающий", callback_data="Застревающий")
        btn5 = types.InlineKeyboardButton(text="Интровертированный", callback_data="Интровертированный")
        btn6 = types.InlineKeyboardButton(text="Истероидный", callback_data="Истероидный")
        btn7 = types.InlineKeyboardButton(text="Лабильный", callback_data="Лабильный")
        btn8 = types.InlineKeyboardButton(text="Педантичный", callback_data="Педантичный")
        btn9 = types.InlineKeyboardButton(text="Психастенический", callback_data="Психастенический")
        btn10 = types.InlineKeyboardButton(text="Тревожный", callback_data="Тревожный")
        btn11 = types.InlineKeyboardButton(text="Экзальтированный", callback_data="Экзальтированный")
        btn12 = types.InlineKeyboardButton(text="Экстравертированный", callback_data="Экстравертированный")
        markup.add(btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8,btn9,btn10,btn11,btn12)

        scenariost = "Вы перешли в меню выбора сценария для отработки своих навыков.\nВыберите желаемый навык для прохождения короткого сценария.\nВ конце бот даст мнение о вашем выборе"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=scenariost, reply_markup=markup)
#text
@bot.message_handler(content_types=['text'])
def chat(msg):
    if msg.text.lower() == 'тест':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="✅", callback_data="yestest")
        btn2 = types.InlineKeyboardButton(text="❌", callback_data="notest")
        markup.add(btn1,btn2)
        bot.send_message(msg.chat.id,"Вы хотите пройти тест?",reply_markup=markup)
    elif msg.text.lower() == 'справка':
        with open('desc.txt','r') as f:
            s = f.readlines();
        desc = ''
        for st in s:
            desc += st
        bot.send_message(msg.chat.id, desc)
    else:
        # just chatting with llm
        umsg = bot.send_message(msg.chat.id, "Бот думает над своим ответом...")
        answer = llmchatmsg(msg)
        bot.edit_message_text(chat_id=msg.chat.id,message_id=umsg.message_id, text=answer)
#in progress
@bot.message_handler(content_types=['document'])
def document_handler(msg):
    if msg.document.file_name == "adcreatescenario.txt":
        strcheck = "Проверка файла на качество:"
        strcheck += "\nСкачивание файла: "
        bmsg = bot.send_message(msg.chat.id, strcheck+'◌')
        try:
            file_info = bot.get_file(msg.document.file_name)
            file = bot.download_file(file_info.file_path)
            strcheck += '✅'
            bot.edit_message_text(chat_id=msg.chat.id, message_id=bmsg.message_id, text=strcheck)
        except Exception as e:
            strcheck += '❌'
            strcheck += f'\nОшибка: {str(e)}'
            print(f'бот начал думать над ошибкой: {str(e)}')
            bot.edit_message_text(chat_id=msg.chat.id, message_id=bmsg.message_id, text=strcheck+'\n\nБот думает над ошибкой...')

            # добавить обработку в функц + перегруз функц
            text = str(e)
            promt = syspromt + text
            response: a.ChatResponse = a.chat(model='gemma3n:e4b', options=a.Options(temperature=0.9, top_p=0.9),
                                              messages=[{'role': 'user', 'content': promt, }, ])
            bot.edit_message_text(chat_id=msg.chat.id, message_id=bmsg.message_id,
                                  text=strcheck + f'\n\n{response.message.content}')
    else:
        bot.send_message(msg.chat.id,'Бот не принимает документы')




if __name__ == '__main__':
    parse_json()
    print('-------------бот начал работу--------------')
    getquestion()
    bot.infinity_polling()