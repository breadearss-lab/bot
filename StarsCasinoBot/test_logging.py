import logging
import sys

# Минимальная настройка
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

logger.info("✅ Логирование работает!")







# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

async def check_flood(user_id):
    """Проверка на флуд"""
    current_time = datetime.now()
    
    if user_id in user_last_action:
        time_diff = (current_time - user_last_action[user_id]).total_seconds()
        if time_diff < FLOOD_TIMEOUT:
            return False
    
    user_last_action[user_id] = current_time
    return True


def clean_old_games():
    """Очистка старых игр"""
    current_time = datetime.now()
    to_remove = []
    
    for user_id, timeout_time in game_timeouts.items():
        if current_time > timeout_time:
            to_remove.append(user_id)
    
    for user_id in to_remove:
        if user_id in active_games:
            del active_games[user_id]
        del game_timeouts[user_id]


def set_game_timeout(user_id):
    """Установить таймаут для игры"""
    game_timeouts[user_id] = datetime.now() + timedelta(seconds=GAME_TIMEOUT)


async def safe_edit_message(query, text, reply_markup=None, parse_mode='HTML'):
    """Безопасное редактирование сообщения"""
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        return True
    except BadRequest as e:
        if "Message is not modified" in str(e):
            return True
        logger.error(f"Error editing message: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in safe_edit_message: {e}")
        return False
    




    async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):"""Проверка баланса"""
    query = update.callback_query
    
    if not query:
        return
    
    await query.answer()
    
    user_id = query.from_user.id
    
    if not await check_flood(user_id):
        await query.answer("⏳ Подождите немного", show_alert=True)
        return
    
    balance = db.get_balance(user_id)
    
    text = f"""
💰 <b>Ваш баланс</b>

Текущий баланс: {balance:,} ⭐

Вы можете пополнить баланс, купив звёзды через Telegram Stars.
    """.replace(',', ' ')
    
    keyboard = [
        [InlineKeyboardButton("⭐ Купить звёзды", callback_data="buy_stars")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]
    ]
    
    await safe_edit_message(
        query,
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    




    async def chess_place_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):"""Размещение ставки и симуляция партии"""
    query = update.callback_query
    
    if not query:
        return
    
    await query.answer()
    
    user_id = query.from_user.id
    
    if not await check_flood(user_id):
        await query.answer("⏳ Подождите немного", show_alert=True)
        return
    
    try:
        bet_amount = int(query.data.split('_')[-1])
    except (ValueError, IndexError):
        await query.answer("❌ Ошибка ставки", show_alert=True)
        return
    
    # Проверяем баланс
    balance = db.get_balance(user_id)
    
    # Валидация ставки
    is_valid, error_msg = validate_bet(bet_amount, 'chess', balance)
    if not is_valid:
        await query.answer(f"❌ {error_msg}", show_alert=True)
        return
    
    # Получаем тип ставки
    bet_type = active_games.get(user_id, {}).get('chess_bet_type', 'white')
    
    # Снимаем ставку
    if not db.update_balance(user_id, -bet_amount):
        await query.answer("❌ Ошибка списания средств", show_alert=True)
        return
    
    db.add_transaction(user_id, "chess", bet_amount, "bet")
    
    # Показываем процесс игры
    await safe_edit_message(query, "♟️ Партия началась...\n\n⏳ Идёт игра...")
    
    # Небольшая задержка для эффекта
    await asyncio.sleep(2)
    
    # Симулируем партию
    game_result, description = chess.simulate_game()
    
    # Рассчитываем выигрыш
    win = chess.calculate_win(bet_type, bet_amount, game_result)
    
    # Начисляем выигрыш если есть
    if win > 0:
        db.update_balance(user_id, win)
        db.add_transaction(user_id, "chess", win, "win")
        db.update_game_stats(user_id, "chess", True, bet_amount, win)
    else:
        db.update_game_stats(user_id, "chess", False, bet_amount, 0)
    
    new_balance = db.get_balance(user_id)
    
    # Формируем итоговое сообщение
    bet_names = {
        'white': '⚪ Победа белых',
        'black': '⚫ Победа чёрных',
        'draw': '🤝 Ничья'
    }
    
    text = f"{description}\n\n"
    text += f"Ваша ставка: {bet_names.get(bet_type, bet_type)} ({bet_amount} ⭐)\n\n"
    
    if win > 0:
        text += f"🎉 <b>Вы выиграли {win} ⭐!</b>\n\n"
    else:
        text += f"😢 Вы проиграли {bet_amount} ⭐\n\n"
    
    text += f"{format_balance(new_balance)}"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Играть ещё", callback_data="game_chess")],
        [InlineKeyboardButton("◀️ Главное меню", callback_data="back_to_menu")]
    ]
    
    await safe_edit_message(
        query,
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    # Очищаем данные игры
    if user_id in active_games:
        active_games[user_id].pop('chess_bet_type', None)
        if not active_games[user_id]:
            del active_games[user_id]
    
    if user_id in game_timeouts:
        del game_timeouts[user_id]















