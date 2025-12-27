import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Roulette:
    def __init__(self):
        # Американская рулетка: 0, 00, 1-36
        self.numbers = list(range(0, 37)) + [37]  # 37 = 00
        
        # Красные числа в рулетке
        self.red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        
        # Чёрные числа
        self.black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        
        # Допустимые типы ставок
        self.valid_bet_types = ['red', 'black', 'zero', 'low', 'high', 'even', 'odd']
    
    def create_bet_menu(self):
        """Меню выбора типа ставки"""
        keyboard = [
            [
                InlineKeyboardButton("🔴 Красное (2x)", callback_data="roulette_bet_red"),
                InlineKeyboardButton("⚫ Чёрное (2x)", callback_data="roulette_bet_black")
            ],
            [
                InlineKeyboardButton("🟢 Зеро (35x)", callback_data="roulette_bet_zero"),
                InlineKeyboardButton("1-18 (2x)", callback_data="roulette_bet_low")
            ],
            [
                InlineKeyboardButton("19-36 (2x)", callback_data="roulette_bet_high"),
                InlineKeyboardButton("Чётное (2x)", callback_data="roulette_bet_even")
            ],
            [
                InlineKeyboardButton("Нечётное (2x)", callback_data="roulette_bet_odd"),
                InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def spin(self, bet_type, bet_amount):
        """
        Крутим рулетку
        Возвращает: (результат_номер, выигрыш, сообщение)
        """
        # Валидация типа ставки
        if bet_type not in self.valid_bet_types:
            return 0, 0, "Ошибка: неверный тип ставки"
        
        # Валидация суммы ставки
        if not isinstance(bet_amount, int) or bet_amount <= 0:
            return 0, 0, "Ошибка: неверная сумма ставки"
        
        # Честная генерация результата
        result = random.SystemRandom().choice(self.numbers)
        win = 0
        
        # Определяем цвет выпавшего номера
        if result in self.red_numbers:
            result_color = "🔴"
        elif result in self.black_numbers:
            result_color = "⚫"
        else:
            result_color = "🟢"
        
        result_display = "00" if result == 37 else str(result)
        
        # Определяем результат в зависимости от типа ставки
        if bet_type == "red":
            if result in self.red_numbers:
                win = bet_amount * 2
                message = f"🎰 Выпало: {result_display} {result_color}\n\n🎉 Вы выиграли {win} ⭐!"
            else:
                message = f"🎰 Выпало: {result_display} {result_color}\n\n😢 Вы проиграли {bet_amount} ⭐"
        
        elif bet_type == "black":
            if result in self.black_numbers:
                win = bet_amount * 2
                message = f"🎰 Выпало: {result_display} {result_color}\n\n🎉 Вы выиграли {win} ⭐!"
            else:
                message = f"🎰 Выпало: {result_display} {result_color}\n\n😢 Вы проиграли {bet_amount} ⭐"
        
        elif bet_type == "zero":
            if result == 0:
                win = bet_amount * 35
                message = f"🎰 Выпало: {result_display} {result_color}\n\n💰 ДЖЕКПОТ! Вы выиграли {win} ⭐!"
            else:
                message = f"🎰 Выпало: {result_display} {result_color}\n\n😢 Вы проиграли {bet_amount} ⭐"
        
        elif bet_type == "low":
            if 1 <= result <= 18:
                win = bet_amount * 2
                message = f"🎰 Выпало: {result_display} {result_color}\n\n🎉 Вы выиграли {win} ⭐!"
            else:
                message = f"🎰 Выпало: {result_display} {result_color}\n\n😢 Вы проиграли {bet_amount} ⭐"
        
        elif bet_type == "high":
            if 19 <= result <= 36:
                win = bet_amount * 2
                message = f"🎰 Выпало: {result_display} {result_color}\n\n🎉 Вы выиграли {win} ⭐!"
            else:
                message = f"🎰 Выпало: {result_display} {result_color}\n\n😢 Вы проиграли {bet_amount} ⭐"
        
        elif bet_type == "even":
            if result > 0 and result < 37 and result % 2 == 0:
                win = bet_amount * 2
                message = f"🎰 Выпало: {result_display} {result_color}\n\n🎉 Вы выиграли {win} ⭐!"
            else:
                message = f"🎰 Выпало: {result_display} {result_color}\n\n😢 Вы проиграли {bet_amount} ⭐"
        
        elif bet_type == "odd":
            if result > 0 and result < 37 and result % 2 == 1:
                win = bet_amount * 2
                message = f"🎰 Выпало: {result_display} {result_color}\n\n🎉 Вы выиграли {win} ⭐!"
            else:
                message = f"🎰 Выпало: {result_display} {result_color}\n\n😢 Вы проиграли {bet_amount} ⭐"
        
        return result, win, message