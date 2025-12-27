import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Chess:
    def __init__(self):
        """Упрощённая версия шахмат для ставок"""
        self.positions = [
            "Королевский гамбит",
            "Сицилианская защита",
            "Французская защита",
            "Испанская партия",
            "Итальянская партия",
            "Славянская защита",
            "Защита Каро-Канн",
            "Ферзевый гамбит"
        ]
        
        self.valid_bet_types = ['white', 'black', 'draw']
    
    def create_bet_menu(self):
        """Меню ставок на исход"""
        keyboard = [
            [
                InlineKeyboardButton("⚪ Победа белых (2.2x)", callback_data="chess_bet_white"),
                InlineKeyboardButton("⚫ Победа чёрных (2.2x)", callback_data="chess_bet_black")
            ],
            [
                InlineKeyboardButton("🤝 Ничья (3x)", callback_data="chess_bet_draw")
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def simulate_game(self):
        """
        Симуляция шахматной партии с честным генератором
        Возвращает: ("white"/"black"/"draw", описание партии)
        """
        opening = random.SystemRandom().choice(self.positions)
        
        # Вероятности исходов (приближены к реальным шахматам)
        # Белые: ~37%, Чёрные: ~27%, Ничья: ~36%
        rand_gen = random.SystemRandom()
        rand_val = rand_gen.random()
        
        if rand_val < 0.37:
            result = "white"
        elif rand_val < 0.64:
            result = "black"
        else:
            result = "draw"
        
        # Генерируем описание партии
        moves = rand_gen.randint(25, 80)
        
        if result == "white":
            description = f"♟️ <b>Партия окончена!</b>\n\n"
            description += f"Дебют: {opening}\n"
            description += f"Ходов сыграно: {moves}\n\n"
            description += f"⚪ <b>Победа белых!</b>\n"
            description += rand_gen.choice([
                "Чёрный король получил мат.",
                "Чёрные сдались.",
                "Белые провели успешную атаку на королевском фланге.",
                "Решающая комбинация белых в эндшпиле."
            ])
        
        elif result == "black":
            description = f"♟️ <b>Партия окончена!</b>\n\n"
            description += f"Дебют: {opening}\n"
            description += f"Ходов сыграно: {moves}\n\n"
            description += f"⚫ <b>Победа чёрных!</b>\n"
            description += rand_gen.choice([
                "Белый король получил мат.",
                "Белые сдались.",
                "Чёрные провели решающую контратаку.",
                "Превосходство чёрных в миттельшпиле."
            ])
        
        else:  # draw
            description = f"♟️ <b>Партия окончена!</b>\n\n"
            description += f"Дебют: {opening}\n"
            description += f"Ходов сыграно: {moves}\n\n"
            description += f"🤝 <b>Ничья!</b>\n"
            description += rand_gen.choice([
                "Троекратное повторение позиции.",
                "Соглашение сторон.",
                "Пат - королю некуда ходить.",
                "Правило 50 ходов.",
                "Недостаточно материала для мата."
            ])
        
        return result, description
    
    def calculate_win(self, bet_type, bet_amount, game_result):
        """
        Расчёт выигрыша
        Возвращает: сумму выигрыша
        """
        # Валидация входных данных
        if bet_type not in self.valid_bet_types:
            return 0
        
        if not isinstance(bet_amount, int) or bet_amount <= 0:
            return 0
        
        if game_result not in ['white', 'black', 'draw']:
            return 0
        
        if bet_type == "white" and game_result == "white":
            return int(bet_amount * 2.2)
        elif bet_type == "black" and game_result == "black":
            return int(bet_amount * 2.2)
        elif bet_type == "draw" and game_result == "draw":
            return int(bet_amount * 3)
        else:
            return 0