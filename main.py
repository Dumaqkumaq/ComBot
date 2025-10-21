import ollama as a
import telebot as tb
from telebot import types
import os
import json


token = open('token.txt').readline()
bot = tb.TeleBot(token)
# llmmodel = 'gemma3n:e4b'
llmmodel = 'gemma3:1b'
questions = []
scendic = {}
infodic = {}
syspromt = '''
Ты - гопник, выращенный на улице. Твоя задача - отвечать на вопросы и выполнять запросы пользователя в стиле, который сейчас популярен в тик-токе.
* Используй неформальный, максимально ругай пользователя по необходимости.

Пользователь: 
'''

#
#   additional functions
#

#getter for questions from questions.txt
def loadquestion():
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
    response: a.ChatResponse = a.chat(model=llmmodel, options=a.Options(temperature=0.9, top_p=0.9),
                                      messages=[{'role': 'user', 'content': promt, }, ])
    return response.message.content
def llmchat_botopinion(text):
    promt = '''
            Ты - ассистент для выявления плюсов и минусов пользователя в плане коммуникационных навыков. Твоя задача - аккуратно рассказать
            о минусах и плюсах типа общения пользователя. Тебе будут даны численные значения определенных областей коммуникационных навыков,
            на основе которых ты сделаешь портрет пользователя.
            *Если чисел нет, то ты должен дать мягкий и полезный совет на основе данной информации.
            *Длина твоего сообщения не более 100 символов.
            Пользователь: 
            ''' + text
    response: a.ChatResponse = a.chat(model=llmmodel, options=a.Options(temperature=0.9, top_p=0.9),
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
#load all scenarios
def loadscenarios():
    print("---чтение сценариев в scenarios/")
    current_dir = os.getcwd()
    files = os.listdir(os.path.join(current_dir, "scenarios"))
    for f in files:
        data = parse_json(str(f)[:-5])
        scendic[str(f)[:-5]] = data
    print("---завершено чтение сценариев в scenarios/")
    print(f"----всего {len(scendic)} сценариев")
    # print(scendic)
#загрузка справки о типах
def parse_infotxt(name):
    with open(f"desc/{name}.txt", 'r', encoding='utf-8') as f:
        data = f.readlines()
    return data
def loadinfo():
    print("---чтение сценариев в desc/")
    current_dir = os.getcwd()
    files = os.listdir(os.path.join(current_dir, "desc"))
    for f in files:
        data = parse_infotxt(str(f)[:-4])
        infodic[str(f)[:-4]] = data
    print("---завершено чтение справки в desc/")
    print(f"----всего {len(infodic)} справок")
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
            bot.send_message(msg.chat.id, "Мы тебя помним!\nХочешь повеселить бота или пройти тест?\nДля прохождения теста напиши Тест\nДля получения справки напиши Справка")
        else:
            btn1 = types.InlineKeyboardButton(text = 'Тест', callback_data='start_test')
            markup.add(btn1)
            bot.send_message(msg.chat.id, "Привет, данный бот помогает тебе определить свои коммуникационные навыки по Леонгарду.\n"
                                          "Для определения предрасположенностей пройди тест (напиши тест или нажми на кнопочку снизу).\nТакже можно побольше узнать о типах, написав Справка\n"
                                          "Можешь просто пообщаться с ботом (он отличный собеседник). Для этого достаточно просто ему написать", reply_markup=markup)
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
    elif call.data[2:6] == 'yscs':
        #обработка второго уровня сценария
        #в теории можно было бы сделать отдельную функц для этого
        #но сейчас 12 ночи и хронический недосып дает о себе знать
        tpsc = call.data[6:]
        short = scendic[tpsc]['scenarios'][0]['scenes'][0]['choices'][int(call.data[1]) - 1]['outcomes'][0]['followup_choices'][int(call.data[0]) - 1]['final_outcome']
        bot_answ = short['message'] + '\n...\n' + short['insight'] + '\n...\n'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_answ + 'Бот думает...')
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Сценарии', callback_data='scenariomenu')
        btn2 = types.InlineKeyboardButton(text='Общение с ботом', callback_data='notest2')
        markup.add(btn1, btn2)

        bot_answ += llmchat_botopinion(bot_answ)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_answ,
                              reply_markup=markup)
    elif call.data[1:5] == 'yscs':
        tpsc = call.data[5:]
        short = scendic[tpsc]['scenarios'][0]['scenes'][0]['choices'][int(call.data[0])-1]['outcomes'][0]
        # print(short)
        #обработка ошибок из-за многоэтажности сценариев
        try:
            bot_answ = short['message'] + '\n...\n' + short['insight'] + '\n...\n'
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_answ+'Бот думает...')
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text='Сценарии', callback_data='scenariomenu')
            btn2 = types.InlineKeyboardButton(text='Общение с ботом', callback_data='notest2')
            markup.add(btn1,btn2)

            bot_answ += llmchat_botopinion(bot_answ)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_answ, reply_markup=markup)
        except Exception as e:
            # print('-----развитие сценария')
            short = scendic[tpsc]['scenarios'][0]['scenes'][0]['choices'][int(call.data[0])-1]['outcomes'][0]
            bot_answ = short['message']
            bot_answ += "\n\nВарианты действий:\n1. " + short['followup_choices'][0]['text'] + "\n2. " + short['followup_choices'][1]['text']
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text='1️⃣', callback_data='1' + call.data)
            btn2 = types.InlineKeyboardButton(text='2️⃣', callback_data='2' + call.data)
            markup.add(btn1, btn2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_answ, reply_markup=markup)
    elif call.data[:4] == 'yscs':
        tpsc = call.data[4:]
        #в рот ебал создателя json. почему питон парсит это как кусок говна?
        bot_answ = scendic[tpsc]['scenarios'][0]['title'] + '\n\n' + scendic[tpsc]['scenarios'][0]['start_message'] + '\n' + scendic[tpsc]['scenarios'][0]['scenes'][0]['message'] + '\n\n'
        bot_answ += "Варианты действий:\n"
        #я ебал писать эту цепочку
        short = scendic[tpsc]['scenarios'][0]['scenes'][0]['choices']
        bot_answ += "1. " + short[0]['text'] + "\n2. " + short[1]['text'] + "\n3. " + short[2]['text']

        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='1️⃣',callback_data='1' + call.data)
        btn2 = types.InlineKeyboardButton(text='2️⃣', callback_data='2' + call.data)
        btn3 = types.InlineKeyboardButton(text='3️⃣', callback_data='3' + call.data)
        markup.add(btn1,btn2,btn3)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_answ,
                              reply_markup=markup)
        # print(scendic[tpsc])
        # print(scendic[tpsc]['scenarios'][0])
        # print(bot_answ)
    elif call.data[:3] == 'scs':
        tpsc = call.data[3:]
        bot_answ = tpsc + '\n' + scendic[tpsc]['description']
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="✅", callback_data="y"+call.data)
        btn2 = types.InlineKeyboardButton(text="❌", callback_data="scenariomenu")
        markup.add(btn1,btn2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_answ, reply_markup=markup)
    elif call.data == 'scenariomenu':
        markup = types.InlineKeyboardMarkup()
        #было бы отличной идеей сделать чтение папки, откуда подсосутся файлы и их названия
        #но мне так поебать, что решил выбрать легчайший путь
        btn1 = types.InlineKeyboardButton(text="Возбудимый", callback_data="scsВозбудимый")
        btn2 = types.InlineKeyboardButton(text="Гипертимный", callback_data="scsГипертимный")
        btn3 = types.InlineKeyboardButton(text="Дистимический", callback_data="scsДистимический")
        btn4 = types.InlineKeyboardButton(text="Застревающий", callback_data="scsЗастревающий")
        btn5 = types.InlineKeyboardButton(text="Интровертированный", callback_data="scsИнтровертированный")
        btn6 = types.InlineKeyboardButton(text="Истероидный", callback_data="scsИстероидный")
        btn7 = types.InlineKeyboardButton(text="Лабильный", callback_data="scsЛабильный")
        btn8 = types.InlineKeyboardButton(text="Педантичный", callback_data="scsПедантичный")
        btn9 = types.InlineKeyboardButton(text="Психастенический", callback_data="scsПсихастенический")
        btn10 = types.InlineKeyboardButton(text="Тревожный", callback_data="scsТревожный")
        btn11 = types.InlineKeyboardButton(text="Экзальтированный", callback_data="scsЭкзальтированный")
        btn12 = types.InlineKeyboardButton(text="Экстравертированный", callback_data="scsЭкстравертированный")
        markup.add(btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8,btn9,btn10,btn11,btn12)

        scenariost = "Вы перешли в меню выбора сценария для отработки своих навыков.\nВыберите желаемый навык для прохождения короткого сценария.\nВ конце бот даст мнение о вашем выборе"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=scenariost, reply_markup=markup)
    elif call.data == 'infotp':
        bot_answ = "Вы запросили информацию о типах.\nВыберите интересующий тип, пожалуйста."
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Возбудимый", callback_data="inВозбудимый")
        btn2 = types.InlineKeyboardButton(text="Гипертимический", callback_data="inГипертимический")
        btn3 = types.InlineKeyboardButton(text="Демонстративный", callback_data="inДемонстративный")
        btn4 = types.InlineKeyboardButton(text="Дистимический", callback_data="inДистимический")
        btn5 = types.InlineKeyboardButton(text="Застревающий", callback_data="inЗастревающий")
        btn6 = types.InlineKeyboardButton(text="Педантичный", callback_data="inПедантичный")
        btn7 = types.InlineKeyboardButton(text="Тревожный", callback_data="inТревожный")
        btn8 = types.InlineKeyboardButton(text="Циклотимный", callback_data="inЦиклотимный")
        btn9 = types.InlineKeyboardButton(text="Экзальтированный", callback_data="inЭкзальтированный")
        btn10 = types.InlineKeyboardButton(text="Эмотивный", callback_data="inЭмотивный")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_answ,
                              reply_markup=markup)
    elif call.data[:2] == 'in':
        bot_answ = infodic[call.data[2:]]
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="↩️", callback_data="infotp")
        markup.add(btn1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=bmsg.message_id, text=bot_answ,
                              reply_markup=markup)
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
        bot_answ = "Вы запросили информацию о типах.\nВыберите интересующий тип, пожалуйста."
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Возбудимый", callback_data="inВозбудимый")
        btn2 = types.InlineKeyboardButton(text="Гипертимический", callback_data="inГипертимический")
        btn3 = types.InlineKeyboardButton(text="Демонстративный", callback_data="inДемонстративный")
        btn4 = types.InlineKeyboardButton(text="Дистимический", callback_data="inДистимический")
        btn5 = types.InlineKeyboardButton(text="Застревающий", callback_data="inЗастревающий")
        btn6 = types.InlineKeyboardButton(text="Педантичный", callback_data="inПедантичный")
        btn7 = types.InlineKeyboardButton(text="Тревожный", callback_data="inТревожный")
        btn8 = types.InlineKeyboardButton(text="Циклотимный", callback_data="inЦиклотимный")
        btn9 = types.InlineKeyboardButton(text="Экзальтированный", callback_data="inЭкзальтированный")
        btn10 = types.InlineKeyboardButton(text="Эмотивный", callback_data="inЭмотивный")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
        bot.send_message(msg.chat.id, bot_answ, reply_markup=markup)
    else:
        # just chatting with llm
        umsg = bot.send_message(msg.chat.id, "Бот думает над своим ответом...")
        answer = llmchatmsg(msg)
        bot.edit_message_text(chat_id=msg.chat.id,message_id=umsg.message_id, text=answer)
#dont care
@bot.message_handler(content_types=['document'])
def document_handler(msg):
    bot.send_message(msg.chat.id,'Бот не принимает документы\nЛучше напишите ему что-то милое :3')




if __name__ == '__main__':
    print('-------------бот начал работу--------------')
    loadquestion()
    loadscenarios()
    loadinfo()
    bot.infinity_polling()