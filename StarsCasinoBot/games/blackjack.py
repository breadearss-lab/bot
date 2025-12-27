import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Blackjack:
    def __init__(self):
        self.suits = ['♠️', '♥️', '♦️', '♣️']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }
    
    def create_deck(self):
        """Создаём колоду карт с честной тасовкой"""
        deck = []
        for suit in self.suits:
            for rank in self.ranks:
                deck.append((rank, suit))
        
        # Используем криптографически стойкий генератор
        random.SystemRandom().shuffle(deck)
        return deck
    
    def calculate_hand(self, hand):
        """Подсчёт очков руки с учётом тузов"""
        if not hand or not isinstance(hand, list):
            return 0
        
        value = 0
        aces = 0
        
        for card in hand:
            if not isinstance(card, tuple) or len(card) != 2:
                continue
            
            rank = card[0]
            if rank in self.values:
                value += self.values[rank]
                if rank == 'A':
                    aces += 1
        
        # Корректируем значение тузов если перебор
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def format_hand(self, hand):
        """Форматирование карт для отображения"""
        if not hand:
            return ""
        
        formatted = []
        for card in hand:
            if isinstance(card, tuple) and len(card) == 2:
                formatted.append(f"{card[0]}{card[1]}")
        
        return ' '.join(formatted)
    
    def create_game_keyboard(self):
        """Клавиатура для игры"""
        keyboard = [
            [
                InlineKeyboardButton("🎴 Взять карту", callback_data="bj_hit"),
                InlineKeyboardButton("✋ Остановиться", callback_data="bj_stand")
            ],
            [InlineKeyboardButton("◀️ Выход", callback_data="back_to_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def dealer_play(self, deck, dealer_hand):
        """Дилер берёт карты по правилам (до 17)"""
        if not deck or not dealer_hand:
            return dealer_hand
        
        # Защита от бесконечного цикла
        max_iterations = 10
        iterations = 0
        
        while self.calculate_hand(dealer_hand) < 17 and iterations < max_iterations:
            if len(deck) == 0:
                break
            dealer_hand.append(deck.pop())
            iterations += 1
        
        return dealer_hand
    
    def check_winner(self, player_value, dealer_value):
        """
        Определяем победителя
        Возвращает: (множитель выигрыша, сообщение)
        """
        # Валидация значений
        if not isinstance(player_value, int) or not isinstance(dealer_value, int):
            return 0, "Ошибка в подсчёте очков"
        
        if player_value > 21:
            return 0, "💥 Перебор! Вы проиграли."
        elif dealer_value > 21:
            return 2, "🎉 Дилер перебрал! Вы выиграли!"
        elif player_value > dealer_value:
            return 2, "🎉 Вы победили!"
        elif player_value == dealer_value:
            return 1, "🤝 Ничья! Ставка возвращена."
        else:
            return 0, "😢 Дилер победил."
    
    def is_blackjack(self, hand):
        """Проверка на блекджек (21 из двух карт)"""
        return len(hand) == 2 and self.calculate_hand(hand) == 21