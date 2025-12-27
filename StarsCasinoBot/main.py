import logging
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import ( Application, CommandHandler, CallbackQueryHandler, PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes )

from config import *
from database import Database
from utils import * 
from games.roulette import Roulette 
from games.blackjack import Blackjack
from games.poker import TexasHoldem
from games.chess import Chess
import asyncio

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO ) 
logger = logging.getLogger()

db = Database(DATABASE_NAME)

roulette = Roulette()
blackjack = Blackjack()
poker = TexasHoldem() 
chess = Chess()

active_games = {}

#============ КОМАНДЫ БОТА =============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start""" 
    user = update.effective_user

        # Добавляем пользователя в БД если его нет
    db.add_user(user.id, user.username or user.first_name, START_BALANCE)

    balance = db.get_balance(user.id)

    welcome_text = f"""
    🎰 Добро пожаловать в Telegram Casino!

    Привет, {user.first_name}!

    Ваш стартовый баланс: {balance} ⭐

    🎮 Доступные игры: 🃏 Покер (Техасский холдем) 🎰 Рулетка (Американская) 🂡 Блекджек ♟️ Шахматы

    Выберите игру из меню ниже: """

    await update.message.reply_text(welcome_text,reply_markup=create_main_menu(),parse_mode='HTML')


    async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Проверка баланса"""
        query = update.callback_query 
        await query.answer()

        user_id = query.from_user.id
        balance = db.get_balance(user_id)

        text = f"""
        💰 Ваш баланс

        Текущий баланс: {balance} ⭐

        Вы можете пополнить баланс, купив звёзды через Telegram Stars."""

        keyboard = [
        [InlineKeyboardButton("⭐ Купить звёзды", callback_data="buy_stars")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]
        ]

        await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML')
    async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE): 
        """Показать статистику игрока""" 
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        stats = db.get_user_stats(user_id)

        text = format_stats(stats)

        await query.edit_message_text(
        text,
        reply_markup=create_back_button(),
        parse_mode='HTML')
 #============ ПОКУПКА ЗВЁЗД =============
    async def buy_stars_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню покупки звёзд"""
        query = update.callback_query 
        await query.answer()

    text = """
    ⭐ Купить звёзды

    Выберите пакет звёзд для покупки: """

    keyboard = [
    [InlineKeyboardButton("💎 50 звёзд - 50 ⭐", callback_data="purchase_50")],
    [InlineKeyboardButton("💎 100 звёзд - 100 ⭐", callback_data="purchase_100")],
    [InlineKeyboardButton("💎 500 звёзд - 500 ⭐", callback_data="purchase_500")],
    [InlineKeyboardButton("💎 1000 звёзд - 1000 ⭐", callback_data="purchase_1000")],
    [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
    text,
    reply_markup=InlineKeyboardMarkup(keyboard),
    parse_mode='HTML')
    async def process_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка покупки звёзд"""
        query = update.callback_query 
        await query.answer()

 # Получаем количество звёзд из callback_data
    amount = int(query.data.split('_')[1])

    # Создаём инвойс для оплаты через Telegram Stars
    title = f"{amount} звёзд"
    description = f"Пополнение баланса на {amount} звёзд"
    payload = f"stars_{amount}_{query.from_user.id}"
    currency = "XTR"  # Telegram Stars

    prices = [LabeledPrice(label=f"{amount} ⭐", amount=amount)]

    await context.bot.send_invoice(
    chat_id=query.message.chat_id,
    title=title,
    description=description,
    payload=payload,
    provider_token="",  # Для Telegram Stars не нужен
    currency=currency,
    prices=prices)
    async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Проверка перед оплатой"""
    query = update.pre_checkout_query
    # Всегда подтверждаем
    await query.answer(ok=True)
    async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE): """Обработка успешной оплаты"""
    payment = update.message.successful_payment 
    payload = payment.invoice_payload

    # Извлекаем данные из payload
    _, amount, user_id = payload.split('_')
    amount = int(amount)
    user_id = int(user_id)

    # Пополняем баланс
    db.update_balance(user_id, amount)
    db.add_transaction(user_id, "purchase", amount, "buy_stars")

    new_balance = db.get_balance(user_id)

    await update.message.reply_text(
    f"✅ Оплата прошла успешно!\n\n"
    f"Вам начислено: {amount} ⭐\n"
    f"Новый баланс: {new_balance} ⭐",
    reply_markup=create_main_menu())
    #============ РУЛЕТКА =============
    async def start_roulette(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало игры в рулетку"""
        query = update.callback_query
        await query.answer()

    text = """
    🎰 Американская рулетка

    Выберите тип ставки:

    🔴 Красное - выигрыш x2 ⚫ Чёрное - выигрыш x2 🟢 Зеро (0) - выигрыш x35 1-18 - выигрыш x2 19-36 - выигрыш x2 Чётное - выигрыш x2 Нечётное - выигрыш x2"""

    await query.edit_message_text(
    text,
    reply_markup=roulette.create_bet_menu(),
    parse_mode='HTML')
    async def roulette_bet_type(update: Update, context: ContextTypes.DEFAULT_TYPE): 
            """Выбор типа ставки в рулетке""" 
            query = update.callback_query 
            await query.answer()
            bet_type = query.data.split('_')[-1]
            user_id = query.from_user.id

            # Сохраняем тип ставки
            if user_id not in active_games:
                active_games[user_id] = {} 
                active_games[user_id]['roulette_bet_type'] = bet_type

            # Предлагаем выбрать размер ставки
            bets = [5, 10, 20, 50, 100]
            text = f"Выберите размер ставки для рулетки:"

            await query.edit_message_text(
            text,
            reply_markup=create_bet_keyboard('roulette', bets))
        
            async def roulette_place_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Размещение ставки и запуск рулетки"""
                query = update.callback_query
                await query.answer()
    
            user_id = query.from_user.id
    bet_amount = int(query.data.split('_')[-1])
    
            # Проверяем баланс
    balance = db.get_balance(user_id)
    if balance < bet_amount:
        await query.answer("❌ Недостаточно средств!", show_alert=True)
    return
    
            # Получаем тип ставки с проверкой
    user_game_data = active_games.get(user_id, {})
    bet_type = user_game_data.get('roulette_bet_type', 'red')  # Значение по умолчанию 'red'
    
            # Снимаем ставку
    db.update_balance(user_id, -bet_amount)
    db.add_transaction(user_id, "roulette", bet_amount, "bet")
    
            # Крутим рулетку
    result, win, message = roulette.spin(bet_type, bet_amount)
    
            # Начисляем выигрыш если есть
    if win > 0:
                db.update_balance(user_id, win)
                db.add_transaction(user_id, "roulette", win, "win")
                db.update_game_stats(user_id, "roulette", True, bet_amount, win)
    else:
                db.update_game_stats(user_id, "roulette", False, bet_amount, 0)
    
    new_balance = db.get_balance(user_id)
    
    full_message = f"{message}\n\n{format_balance(new_balance)}"
    
    keyboard = [
                  [InlineKeyboardButton("🔄 Играть ещё", callback_data="game_roulette")],
                  [InlineKeyboardButton("◀️ Главное меню", callback_data="back_to_menu")]]
    
    await query.edit_message_text(
            full_message,
            reply_markup=InlineKeyboardMarkup(keyboard) )
            # Очищаем данные игры
    if user_id in active_games:
                active_games[user_id].pop('roulette_bet_type', None)
 #============= БЛЕКДЖЕК =============
    async def start_blackjack(update: Update, context: ContextTypes.DEFAULT_TYPE): """Начало игры в блекджек""" 
    query = update.callback_query 
    await query.answer()

    text = "🂡 <b>Блекджек</b>\n\nВыберите размер ставки:"
    bets = [5, 10, 20, 50]

    await query.edit_message_text(
    text,
    reply_markup=create_bet_keyboard('blackjack', bets),
    parse_mode='HTML')
    async def blackjack_place_bet(update: Update, context: ContextTypes.DEFAULT_TYPE): 
        """Начало раздачи в блекджеке""" 
        query = update.callback_query 
        await query.answer()

        user_id = query.from_user.id
        bet_amount = int(query.data.split('_')[-1])

        # Проверяем баланс
        balance = db.get_balance(user_id)
        if balance < bet_amount:
            await query.answer("❌ Недостаточно средств!", show_alert=True)
        return

        # Снимаем ставку
        db.update_balance(user_id, -bet_amount)
        db.add_transaction(user_id, "blackjack", bet_amount, "bet")

        # Создаём колоду и раздаём карты
    deck = blackjack.create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

        # Сохраняем состояние игры
    active_games[user_id] = {
        'game': 'blackjack',
        'deck': deck,
        'player_hand': player_hand,
        'dealer_hand': dealer_hand,
        'bet': bet_amount
        }

    player_value = blackjack.calculate_hand(player_hand)
    dealer_visible = dealer_hand[0]

         # Проверяем на блекджек
    if player_value == 21:
              await blackjack_finish_game(query, user_id, "blackjack")
    return

    text = f"🂡 <b>Блекджек</b>\n\n"
    text += f"Ваши карты: {blackjack.format_hand(player_hand)}\n"
    text += f"Ваши очки: {player_value}\n\n"
    text += f"Карта дилера: {dealer_visible[0]}{dealer_visible[1]} ❓\n\n"
    text += f"Ставка: {bet_amount} ⭐"

    await query.edit_message_text(
    text,
    reply_markup=blackjack.create_game_keyboard(),
    parse_mode='HTML')
    async def blackjack_hit(update: Update, context: ContextTypes.DEFAULT_TYPE): 
            """Игрок берёт карту""" 
            query = update.callback_query
            await query.answer()

            user_id = query.from_user.id

            if user_id not in active_games or active_games[user_id].get('game') != 'blackjack':
                await query.answer("❌ Игра не найдена", show_alert=True)
            return

    game = active_games[user_id]
    game['player_hand'].append(game['deck'].pop())

    player_value = blackjack.calculate_hand(game['player_hand'])
    dealer_visible = game['dealer_hand'][0]

    text = f"🂡 <b>Блекджек</b>\n\n"
    text += f"Ваши карты: {blackjack.format_hand(game['player_hand'])}\n"
    text += f"Ваши очки: {player_value}\n\n"
    text += f"Карта дилера: {dealer_visible[0]}{dealer_visible[1]} ❓\n\n"
    text += f"Ставка: {game['bet']} ⭐"

    # Проверяем перебор
    if player_value > 21:
        await blackjack_finish_game(query, user_id, "bust")
    return

    await query.edit_message_text(
    text,
    reply_markup=blackjack.create_game_keyboard(),
    parse_mode='HTML')
    async def blackjack_stand(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Игрок остановился""" 
        query = update.callback_query
        await query.answer()

    user_id = query.from_user.id

    if user_id not in active_games or active_games[user_id].get('game') != 'blackjack':
        await query.answer("❌ Игра не найдена", show_alert=True)
    return

    await blackjack_finish_game(query, user_id, "stand")
    async def blackjack_finish_game(query, user_id, reason):
        """Завершение игры в блекджек""" 
        game = active_games.get(user_id)
    if not game:await query.answer("❌ Игра не найдена", show_alert=True)
    return

    # Дилер играет
    dealer_hand = blackjack.dealer_play(game['deck'], game['dealer_hand'])

    player_value = blackjack.calculate_hand(game['player_hand'])
    dealer_value = blackjack.calculate_hand(dealer_hand)

    # Определяем победителя
    multiplier, result_message = blackjack.check_winner(player_value, dealer_value)
    win = int(game['bet'] * multiplier)

    # Начисляем выигрыш
    if win > 0:
        db.update_balance(user_id, win)
        db.add_transaction(user_id, "blackjack", win, "win")
        db.update_game_stats(user_id, "blackjack", multiplier >= 2, game['bet'], win)
    else:
        db.update_game_stats(user_id, "blackjack", False, game['bet'], 0)

    new_balance = db.get_balance(user_id)

    text = f"🂡 <b>Блекджек - Результат</b>\n\n"
    text += f"Ваши карты: {blackjack.format_hand(game['player_hand'])}\n"
    text += f"Ваши очки: {player_value}\n\n"
    text += f"Карты дилера: {blackjack.format_hand(dealer_hand)}\n"
    text += f"Очки дилера: {dealer_value}\n\n"
    text += f"{result_message}\n\n"
    if win > 0:
        text += f"Выигрыш: {win} ⭐\n"
        text += f"{format_balance(new_balance)}"

    keyboard = [
        [InlineKeyboardButton("🔄 Играть ещё", callback_data="game_blackjack")],
        [InlineKeyboardButton("◀️ Главное меню", callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
    text,
    reply_markup=InlineKeyboardMarkup(keyboard),
    parse_mode='HTML')

    # Очищаем игру
    if user_id in active_games:
        del active_games[user_id]
    
    async def start_poker(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало игры в покер"""
    query = update.callback_query
    await query.answer()

    text = """   
    
    Техасский Холдем

    Упрощённая версия покера против бота.

    Правила: - Вы и бот получаете по 2 карты - На стол выкладывается 5 общих карт - Лучшая комбинация из 5 карт побеждает

    Выберите размер ставки: """

    bets = [10, 20, 50, 100]

    await query.edit_message_text(
    text,
    reply_markup=create_bet_keyboard('poker', bets),
    parse_mode='HTML')
    async def poker_place_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало раздачи в покере"""
    query = update.callback_query 
    await query.answer()

    user_id = query.from_user.id
    bet_amount = int(query.data.split('_')[-1])

 # Проверяем баланс
    balance = db.get_balance(user_id)
    if balance < bet_amount:
        await query.answer("❌ Недостаточно средств!", show_alert=True)
    return

 # Снимаем ставку
    db.update_balance(user_id, -bet_amount)
    db.add_transaction(user_id, "poker", bet_amount, "bet")

 # Создаём колоду и раздаём карты
    deck = poker.create_deck()
    player_hand = [deck.pop(), deck.pop()]
    bot_hand = [deck.pop(), deck.pop()]
    community = []

 # Сохраняем состояние игры
    active_games[user_id] = {
    'game': 'poker',
    'deck': deck,
    'player_hand': player_hand,
    'bot_hand': bot_hand,
    'community': community,
    'bet': bet_amount,
    'stage': 'preflop'}

    text = f"🃏 <b>Техасский Холдем</b>\n\n"
    text += f"Ваши карты: {poker.format_cards(player_hand)}\n\n"
    text += f"Общие карты: (пусто)\n\n"
    text += f"Ставка: {bet_amount} ⭐\n\n"
    text += f"Бот делает ставку..."

    keyboard = [
        [InlineKeyboardButton("👀 Показать флоп", callback_data="poker_flop")],
        [InlineKeyboardButton("❌ Сдаться", callback_data="poker_fold")]
    ]

    await query.edit_message_text(
    text,
    reply_markup=InlineKeyboardMarkup(keyboard),
    parse_mode='HTML')
    async def poker_flop(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ флопа (3 карты)"""
        query = update.callback_query 
        await query.answer()

    user_id = query.from_user.id

    if user_id not in active_games or active_games[user_id].get('game') != 'poker':
        await query.answer("❌ Игра не найдена", show_alert=True)
    return

    game = active_games[user_id]

    # Выкладываем флоп (3 карты)
    game['community'] = [game['deck'].pop(), game['deck'].pop(), game['deck'].pop()]
    game['stage'] = 'flop'

    text = f"🃏 <b>Техасский Холдем - Флоп</b>\n\n"
    text += f"Ваши карты: {poker.format_cards(game['player_hand'])}\n\n"
    text += f"Общие карты: {poker.format_cards(game['community'])}\n\n"
    text += f"Ставка: {game['bet']} ⭐"

    keyboard = [
        [InlineKeyboardButton("👀 Показать терн", callback_data="poker_turn")],
        [InlineKeyboardButton("❌ Сдаться", callback_data="poker_fold")]
    ]

    await query.edit_message_text(
    text,
    reply_markup=InlineKeyboardMarkup(keyboard),
    parse_mode='HTML')
    async def poker_turn(update: Update, context: ContextTypes.DEFAULT_TYPE): """Показ терна (4-я карта)"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    game = active_games.get(user_id)

    if not game or game.get('game') != 'poker':
        await query.answer("❌ Игра не найдена", show_alert=True)
    return

    # Добавляем терн
    game['community'].append(game['deck'].pop())
    game['stage'] = 'turn'

    text = f"🃏 <b>Техасский Холдем - Терн</b>\n\n"
    text += f"Ваши карты: {poker.format_cards(game['player_hand'])}\n\n"
    text += f"Общие карты: {poker.format_cards(game['community'])}\n\n"
    text += f"Ставка: {game['bet']} ⭐"

    keyboard = [
        [InlineKeyboardButton("👀 Показать ривер", callback_data="poker_river")],
        [InlineKeyboardButton("❌ Сдаться", callback_data="poker_fold")]
    ]

    await query.edit_message_text(
    text,
    reply_markup=InlineKeyboardMarkup(keyboard),
    parse_mode='HTML')
    async def poker_river(update: Update, context: ContextTypes.DEFAULT_TYPE): """Показ ривера (5-я карта) и вскрытие""" 
    query = update.callback_query 
    await query.answer()

    user_id = query.from_user.id
    game = active_games.get(user_id)

    if not game or game.get('game') != 'poker':
        await query.answer("❌ Игра не найдена", show_alert=True)
    return

    # Добавляем ривер
    game['community'].append(game['deck'].pop())
    game['stage'] = 'river'

 # Вскрытие
    await poker_showdown(query, user_id)
    async def poker_showdown(query, user_id): """Вскрытие карт и определение победителя"""
    game = active_games.get(user_id)

    if not game:
        await query.answer("❌ Игра не найдена", show_alert=True)
    return

    # Объединяем карты игрока и бота с общими
    player_cards = game['player_hand'] + game['community']
    bot_cards = game['bot_hand'] + game['community']

    # Оцениваем руки
    player_rank, player_value, player_combo = poker.evaluate_hand(player_cards)
    bot_rank, bot_value, bot_combo = poker.evaluate_hand(bot_cards)

    # Определяем победителя
    if player_rank > bot_rank or (player_rank == bot_rank and player_value > bot_value):
        win = game['bet'] * 2
        result = "🎉 Вы победили!"
        won = True
    elif player_rank == bot_rank and player_value == bot_value:
        win = game['bet']
        result = "🤝 Ничья! Ставка возвращена."
        won = False
    else:
        win = 0
        result = "😢 Бот победил!"
        won = False

    # Начисляем выигрыш
    if win > 0:
        db.update_balance(user_id, win)
        db.add_transaction(user_id, "poker", win, "win")
        db.update_game_stats(user_id, "poker", won, game['bet'], win)
    else:
        db.update_game_stats(user_id, "poker", False, game['bet'], 0)

    new_balance = db.get_balance(user_id)

    text = f"🃏 <b>Техасский Холдем - Результат</b>\n\n"
    text += f"Ваши карты: {poker.format_cards(game['player_hand'])}\n"
    text += f"Ваша комбинация: {player_combo}\n\n"
    text += f"Карты бота: {poker.format_cards(game['bot_hand'])}\n"
    text += f"Комбинация бота: {bot_combo}\n\n"
    text += f"Общие карты: {poker.format_cards(game['community'])}\n\n"
    text += f"{result}\n\n"
    if win > 0:
        text += f"Выигрыш: {win} ⭐\n"
        text += f"{format_balance(new_balance)}"

    keyboard = [
    [InlineKeyboardButton("🔄 Играть ещё", callback_data="game_poker")],
    [InlineKeyboardButton("◀️ Главное меню", callback_data="back_to_menu")]]

    await query.edit_message_text(
    text,
    reply_markup=InlineKeyboardMarkup(keyboard),
    parse_mode='HTML')

    # Очищаем игру
    if user_id in active_games:
        del active_games[user_id]
    async def poker_fold(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Игрок сдался"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id in active_games and active_games[user_id].get('game') == 'poker':
        bet_amount = active_games[user_id]['bet']
        db.update_game_stats(user_id, "poker", False, bet_amount, 0)
        del active_games[user_id]

    text = "Вы сдались и потеряли ставку. 😢"

    keyboard = [
        [InlineKeyboardButton("🔄 Играть ещё", callback_data="game_poker")],
        [InlineKeyboardButton("◀️ Главное меню", callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
    text,
    reply_markup=InlineKeyboardMarkup(keyboard),
    parse_mode='HTML')
    #============= ШАХМАТЫ =============
    async def start_chess(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало игры в шахматы"""
        query = update.callback_query
        await query.answer()

    text = """
    ♟️ Шахматы

    Игра против бота.

    Выберите режим игры: """

    keyboard = [
    [InlineKeyboardButton("♔ Новичок (рейтинг 800)", callback_data="chess_beginner")],
    [InlineKeyboardButton("♕ Любитель (рейтинг 1200)", callback_data="chess_intermediate")],
    [InlineKeyboardButton("♗ Эксперт (рейтинг 1600)", callback_data="chess_expert")],
    [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
    text,
    reply_markup=InlineKeyboardMarkup(keyboard),
    parse_mode='HTML')
    async def chess_start_game(update: Update, context: ContextTypes.DEFAULT_TYPE): """Начало шахматной партии"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    skill_level = query.data.split('_')[1]  # beginner, intermediate, expert

    # Создаём новую игру
    chess_board = chess.create_new_game()
    fen = chess_board.fen()

    # Сохраняем состояние игры
    active_games[user_id] = {
    'game': 'chess',
    'fen': fen,
    'skill_level': skill_level,
    'moves': []}

    # Отправляем изображение доски
    board_image = chess.get_board_image(fen)
    text = f"♟️ <b>Шахматы - {skill_level.capitalize()}</b>\n\nВаш ход. Вы играете белыми."

    keyboard = [
        [InlineKeyboardButton("👑 Сделать ход", callback_data="chess_move")],
        [InlineKeyboardButton("❌ Сдаться", callback_data="chess_resign")],
        [InlineKeyboardButton("◀️ Главное меню", callback_data="back_to_menu")]
    ]

    await query.message.reply_photo(
    photo=board_image,
    caption=text,
    reply_markup=InlineKeyboardMarkup(keyboard),
    parse_mode='HTML')
    await query.delete_message()
    async def chess_move(update: Update, context: ContextTypes.DEFAULT_TYPE): """Обработчик хода в шахматах""" 
    query = update.callback_query 
    await query.answer()

    user_id = query.from_user.id
    game = active_games.get(user_id)

    if not game or game.get('game') != 'chess':
        await query.answer("❌ Игра не найдена", show_alert=True)
    return

    text = "Отправьте ход в формате 'e2 e4' или 'Ng1 f3'"
    await query.edit_message_text(text, parse_mode='HTML')

    # Сохраняем информацию о том, что ждём ход
    context.user_data['waiting_for_chess_move'] = True
    context.user_data['chess_user_id'] = user_id
    context.user_data['chess_query'] = query
    async def chess_handle_move(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстового хода в шахматах"""
    if not context.user_data.get('waiting_for_chess_move'): return

    user_id = update.effective_user.id
    chess_user_id = context.user_data.get('chess_user_id')

    if user_id != chess_user_id: return

    move_text = update.message.text.strip()
    query = context.user_data.get('chess_query')

    if not query:return

    # Получаем игру
    game = active_games.get(user_id)
    if not game or game.get('game') != 'chess':
        await update.message.reply_text("❌ Игра не найдена")
    return

    # Создаём объект доски из FEN
    board = chess.Board(game['fen'])

    try:
        # Пытаемся сделать ход
        move = board.parse_san(move_text)
        if move not in board.legal_moves:
            await update.message.reply_text("❌ Недопустимый ход!")
        return

        # Делаем ход игрока
        board.push(move)
        game['moves'].append(move_text)

        # Проверяем конец игры
        if board.is_game_over():
            result = chess.get_game_result(board)
            text = f"♟️ <b>Шахматы - Игра окончена</b>\n\n{result}\n\n"
            text += f"Количество ходов: {len(game['moves'])}"

            keyboard = [
                [InlineKeyboardButton("🔄 Новая игра", callback_data="game_chess")],
                [InlineKeyboardButton("◀️ Главное меню", callback_data="back_to_menu")]
            ]

            board_image = chess.get_board_image(board.fen())

            await query.message.reply_photo(
            photo=board_image,
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML')

            # Очищаем игру
            del active_games[user_id]
            context.user_data.pop('waiting_for_chess_move', None)
            context.user_data.pop('chess_user_id', None)
            context.user_data.pop('chess_query', None)
            return

        # Ход бота
        skill_level = game['skill_level']
        bot_move = chess.get_bot_move(board, skill_level)
        if bot_move:
            board.push(bot_move)
        game['moves'].append(bot_move.uci())
        game['fen'] = board.fen()

        # Проверяем конец игры после хода бота
        if board.is_game_over():
            result = chess.get_game_result(board)
            text = f"♟️ <b>Шахматы - Игра окончена</b>\n\n{result}\n\n"
            text += f"Ваш ход: {move_text}\n"
            text += f"Ход бота: {bot_move.uci() if bot_move else 'нет'}\n"
            text += f"Количество ходов: {len(game['moves'])}"

            keyboard = [
            [InlineKeyboardButton("🔄 Новая игра", callback_data="game_chess")],
            [InlineKeyboardButton("◀️ Главное меню", callback_data="back_to_menu")]
            ]

            board_image = chess.get_board_image(board.fen())

            await query.message.reply_photo(
            photo=board_image,
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML')

            # Очищаем игру
            del active_games[user_id]
        else:
        # Продолжаем игру
            text = f"♟️ <b>Шахматы - {skill_level.capitalize()}</b>\n\n"
            text += f"Ваш ход: {move_text}\n"
            text += f"Ход бота: {bot_move.uci() if bot_move else 'нет'}\n"
            text += f"Ваш ход. Вы играете белыми."
            
            keyboard = [
                [InlineKeyboardButton("👑 Сделать ход", callback_data="chess_move")],
                [InlineKeyboardButton("❌ Сдаться", callback_data="chess_resign")],
                [InlineKeyboardButton("◀️ Главное меню", callback_data="back_to_menu")]]
            
        board_image = chess.get_board_image(board.fen())
            
        await query.message.reply_photo(
                photo=board_image,
                caption=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}\nПопробуйте снова в формате 'e2 e4'")
        return
    
    # Очищаем состояние ожидания хода
    context.user_data.pop('waiting_for_chess_move', None)
    context.user_data.pop('chess_user_id', None)
    context.user_data.pop('chess_query', None)

    async def chess_resign(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Игрок сдаётся в шахматах"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    text = "Вы сдались. Игра окончена."
    
    keyboard = [
        [InlineKeyboardButton("🔄 Новая игра", callback_data="game_chess")],
        [InlineKeyboardButton("◀️ Главное меню", callback_data="back_to_menu")]
        ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML' )
    
    # Очищаем игру
    if user_id in active_games:
        del active_games[user_id]

    # ============= ОБРАБОТЧИКИ КНОПОК =============
    async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Возврат в главное меню"""
        query = update.callback_query
        await query.answer()
    
        user_id = query.from_user.id
        balance = db.get_balance(user_id)
    
    text = f"""
    🎰 Telegram Casino

    Баланс: {balance} ⭐

    Выберите игру: """
    
    await query.edit_message_text(
        text,
        reply_markup=create_main_menu(),
        parse_mode='HTML')
    
    # Очищаем активные игры при выходе в меню
    if user_id in active_games:
        del active_games[user_id]

    async def handle_game_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора игры из главного меню"""
        query = update.callback_query
        await query.answer()
    
        game = query.data.split('_')[1]
    
    if game == 'roulette':
        await start_roulette(update, context)
    elif game == 'blackjack':
        await start_blackjack(update, context)
    elif game == 'poker':
        await start_poker(update, context)
    elif game == 'chess':
        await start_chess(update, context)

    # ============= ОСНОВНАЯ ФУНКЦИЯ =============
    def main():
        """Запуск бота"""
        # Создаём приложение
        application = Application.builder().token(BOT_TOKEN).build()
    
        # Регистрируем обработчики команд
        application.add_handler(CommandHandler("start", start))
    
    # Регистрируем обработчики кнопок
        application.add_handler(CallbackQueryHandler(check_balance, pattern="^check_balance$"))
        application.add_handler(CallbackQueryHandler(show_stats, pattern="^show_stats$"))
        application.add_handler(CallbackQueryHandler(buy_stars_menu, pattern="^buy_stars$"))
        application.add_handler(CallbackQueryHandler(process_purchase, pattern="^purchase_"))
        application.add_handler(CallbackQueryHandler(start_roulette, pattern="^game_roulette$"))
        application.add_handler(CallbackQueryHandler(roulette_bet_type, pattern="^roulette_type_"))
        application.add_handler(CallbackQueryHandler(roulette_place_bet, pattern="^roulette_bet_"))
        application.add_handler(CallbackQueryHandler(start_blackjack, pattern="^game_blackjack$"))
        application.add_handler(CallbackQueryHandler(blackjack_place_bet, pattern="^blackjack_bet_"))
        application.add_handler(CallbackQueryHandler(blackjack_hit, pattern="^blackjack_hit$"))
        application.add_handler(CallbackQueryHandler(blackjack_stand, pattern="^blackjack_stand$"))
        application.add_handler(CallbackQueryHandler(start_poker, pattern="^game_poker$"))
        application.add_handler(CallbackQueryHandler(poker_place_bet, pattern="^poker_bet_"))
        application.add_handler(CallbackQueryHandler(poker_flop, pattern="^poker_flop$"))
        application.add_handler(CallbackQueryHandler(poker_turn, pattern="^poker_turn$"))
        application.add_handler(CallbackQueryHandler(poker_river, pattern="^poker_river$"))
        application.add_handler(CallbackQueryHandler(poker_fold, pattern="^poker_fold$"))
        application.add_handler(CallbackQueryHandler(start_chess, pattern="^game_chess$"))
        application.add_handler(CallbackQueryHandler(chess_start_game, pattern="^chess_"))
        application.add_handler(CallbackQueryHandler(chess_move, pattern="^chess_move$"))
        application.add_handler(CallbackQueryHandler(chess_resign, pattern="^chess_resign$"))
        application.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))
        application.add_handler(CallbackQueryHandler(handle_game_selection, pattern="^game_"))
    
        # Регистрируем обработчики платежей
        application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
        application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    
        # Регистрируем обработчик ходов в шахматах
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chess_handle_move))
    
        # Запускаем бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    if __name__ == "__main__":
        main()