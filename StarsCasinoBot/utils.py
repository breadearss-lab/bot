from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import html

def sanitize_text(text):
    """Защита от XSS в HTML режиме"""
    return html.escape(str(text))


def create_main_menu():
    """Главное меню с выбором игр"""
    keyboard = [
        [
            InlineKeyboardButton("🃏 Покер", callback_data="game_poker"),
            InlineKeyboardButton("🎰 Рулетка", callback_data="game_roulette")
        ],
        [
            InlineKeyboardButton("🂡 Блекджек", callback_data="game_blackjack"),
            InlineKeyboardButton("♟️ Шахматы", callback_data="game_chess")
        ],
        [
            InlineKeyboardButton("💰 Баланс", callback_data="check_balance"),
            InlineKeyboardButton("📊 Статистика", callback_data="stats")
        ],
        [
            InlineKeyboardButton("⭐ Купить звёзды", callback_data="buy_stars")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_back_button():
    """Кнопка возврата в главное меню"""
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]]
    return InlineKeyboardMarkup(keyboard)


def create_bet_keyboard(game_type, bets):
    """Клавиатура для выбора ставки"""
    keyboard = []
    row = []
    
    for bet in bets:
        if not isinstance(bet, int) or bet <= 0:
            continue
        
        row.append(InlineKeyboardButton(
            f"{bet} ⭐", 
            callback_data=f"bet_{game_type}_{bet}"
        ))
        
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def format_balance(balance):
    """Форматирование баланса"""
    balance = int(balance) if isinstance(balance, (int, float)) else 0
    return f"💰 Ваш баланс: {balance:,} ⭐".replace(',', ' ')


def format_stats(stats):
    """Форматирование статистики"""
    if not stats:
        return "📊 У вас пока нет игровой статистики"
    
    text = "📊 <b>Ваша статистика:</b>\n\n"
    
    game_names = {
        "poker": "🃏 Покер",
        "roulette": "🎰 Рулетка",
        "blackjack": "🂡 Блекджек",
        "chess": "♟️ Шахматы"
    }
    
    for stat in stats:
        game_type, played, won, total_bet, total_won = stat
        win_rate = (won / played * 100) if played > 0 else 0
        profit = total_won - total_bet
        
        game_name = sanitize_text(game_names.get(game_type, game_type))
        
        text += f"{game_name}:\n"
        text += f"  Игр сыграно: {played}\n"
        text += f"  Побед: {won} ({win_rate:.1f}%)\n"
        text += f"  Поставлено: {total_bet:,} ⭐\n".replace(',', ' ')
        text += f"  Выиграно: {total_won:,} ⭐\n".replace(',', ' ')
        text += f"  Прибыль: {profit:+,} ⭐\n\n".replace(',', ' ')
    
    return text


def validate_bet(bet_amount, game_type, balance):
    """
    Валидация ставки
    Возвращает: (is_valid, error_message)
    """
    from config import MIN_BET, MAX_BET
    
    # Проверка типа
    if not isinstance(bet_amount, int):
        return False, "Неверный формат ставки"
    
    # Проверка минимума
    min_bet = MIN_BET.get(game_type, 1)
    if bet_amount < min_bet:
        return False, f"Минимальная ставка: {min_bet} ⭐"
    
    # Проверка максимума
    max_bet = MAX_BET.get(game_type, 1000)
    if bet_amount > max_bet:
        return False, f"Максимальная ставка: {max_bet} ⭐"
    
    # Проверка баланса
    if bet_amount > balance:
        return False, "Недостаточно средств"
    
    return True, None


def is_valid_user_id(user_id):
    """Проверка валидности ID пользователя"""
    return isinstance(user_id, int) and user_id > 0


def clamp_value(value, min_val, max_val):
    """Ограничение значения в диапазоне"""
    return max(min_val, min(value, max_val))