import random
from collections import Counter
from itertools import combinations
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class TexasHoldem:
    def __init__(self):  # ← ИСПРАВЛЕНО: было init, должно быть __init__
        self.suits = ['♠️', '♥️', '♦️', '♣️']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.rank_values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }
    
    def create_deck(self):
        """Создаём колоду с честной тасовкой"""
        deck = []
        for suit in self.suits:
            for rank in self.ranks:
                deck.append((rank, suit))
        
        random.SystemRandom().shuffle(deck)
        return deck
    
    def format_cards(self, cards):
        """Форматирование карт"""
        if not cards:
            return ""
        
        formatted = []
        for card in cards:
            if isinstance(card, tuple) and len(card) == 2:
                formatted.append(f"{card[0]}{card[1]}")
        
        return ' '.join(formatted)
    
    def evaluate_hand(self, cards):
        """
        Оценка покерной руки (комбинация из 7 карт: 2 карманные + 5 общих)
        Возвращает: (ранг комбинации, значение для сравнения, название)
        """
        if not cards or len(cards) < 5:
            return (0, 0, "Недостаточно карт")
        
        # Валидация карт
        valid_cards = []
        for card in cards:
            if isinstance(card, tuple) and len(card) == 2 and card[0] in self.ranks:
                valid_cards.append(card)
        
        if len(valid_cards) < 5:
            return (0, 0, "Недостаточно карт")
        
        best_hand = (0, 0, "Старшая карта")
        
        # Ограничиваем количество комбинаций для защиты от DoS
        try:
            for hand in combinations(valid_cards[:7], 5):
                rank, value, name = self._evaluate_5_cards(list(hand))
                if rank > best_hand[0] or (rank == best_hand[0] and value > best_hand[1]):
                    best_hand = (rank, value, name)
        except Exception as e:
            print(f"Error in evaluate_hand: {e}")
            return (0, 0, "Ошибка оценки")
        
        return best_hand
    
    def _evaluate_5_cards(self, hand):
        """Оценка конкретной комбинации из 5 карт"""
        if not hand or len(hand) != 5:
            return (0, 0, "Неверная рука")
        
        try:
            ranks = [card[0] for card in hand]
            suits = [card[1] for card in hand]
            rank_counts = Counter(ranks)
            suit_counts = Counter(suits)
            
            # Получаем числовые значения
            values = sorted([self.rank_values.get(r, 0) for r in ranks], reverse=True)
            
            # Проверка на флеш
            is_flush = len(suit_counts) == 1
            
            # Проверка на стрит
            is_straight = False
            if values == list(range(values[0], values[0] - 5, -1)):
                is_straight = True
            # Стрит от туза до пятёрки (A-2-3-4-5)
            elif sorted(values) == [2, 3, 4, 5, 14]:
                is_straight = True
                values = [5, 4, 3, 2, 1]  # Туз становится единицей
            
            # Считаем пары, тройки и т.д.
            counts = sorted(rank_counts.values(), reverse=True)
            
            # Роял флеш
            if is_flush and is_straight and max(values) == 14 and min(values) == 10:
                return (10, sum(values), "Роял-флеш")
            
            # Стрит флеш
            if is_flush and is_straight:
                return (9, sum(values), "Стрит-флеш")
            
            # Каре
            if counts == [4, 1]:
                return (8, sum(values), "Каре")
            
            # Фулл-хаус
            if counts == [3, 2]:
                return (7, sum(values), "Фулл-хаус")
            
            # Флеш
            if is_flush:
                return (6, sum(values), "Флеш")
            
            # Стрит
            if is_straight:
                return (5, sum(values), "Стрит")
            
            # Сет (тройка)
            if counts == [3, 1, 1]:
                return (4, sum(values), "Тройка")
            
            # Две пары
            if counts == [2, 2, 1]:
                return (3, sum(values), "Две пары")
            
            # Пара
            if counts == [2, 1, 1, 1]:
                return (2, sum(values), "Пара")
            
            # Старшая карта
            return (1, sum(values), "Старшая карта")
        
        except Exception as e:
            print(f"Error in _evaluate_5_cards: {e}")
            return (0, 0, "Ошибка")
    
    def create_game_keyboard(self, stage):
        """Клавиатура для разных этапов игры"""
        if stage == "preflop":
            keyboard = [
                [
                    InlineKeyboardButton("💰 Колл", callback_data="poker_call"),
                    InlineKeyboardButton("📈 Рейз", callback_data="poker_raise")
                ],
                [
                    InlineKeyboardButton("❌ Фолд", callback_data="poker_fold")
                ]
            ]
        else:
            keyboard = [
                [
                    InlineKeyboardButton("✅ Чек", callback_data="poker_check"),
                    InlineKeyboardButton("💰 Бет", callback_data="poker_bet")
                ],
                [
                    InlineKeyboardButton("❌ Фолд", callback_data="poker_fold")
                ]
            ]
        
        return InlineKeyboardMarkup(keyboard)