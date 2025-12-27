import re
from pathlib import Path

def fix_async_errors(filename):
    """Исправляет async/await ошибки в файле"""
    
    print(f"🔧 Обработка файла: {filename}\n")
    
    # Создаём бэкап
    backup = filename + '.backup'
    Path(filename).replace(backup) if Path(backup).exists() else None
    with open(filename, 'r', encoding='UTF-16') as f:
        content = f.read()
    
    # Счётчик исправлений
    fixes = 0
    
    # 1. Исправляем функции без async но с await внутри
    pattern_func = r'^(def\s+\w+\s*\([^)]*\)\s*:)'
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # Проверяем есть ли в последующих строках await
        if re.match(pattern_func, line.strip()):
            # Ищем тело функции (следующие отступленные строки)
            j = i + 1
            has_await = False
            indent = len(line) - len(line.lstrip())
            
            while j < len(lines):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Если отступ меньше или равен - функция закончилась
                if next_line.strip() and next_indent <= indent:
                    break
                
                # Проверяем наличие await
                if 'await ' in next_line:
                    has_await = True
                    break
                
                j += 1
            
            # Если есть await, но нет async - добавляем
            if has_await and not line.strip().startswith('async def'):
                line = line.replace('def ', 'async def ', 1)
                fixes += 1
                print(f"  ✅ Добавлен async в функцию на строке {i+1}")
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # 2. Исправляем вызовы async функций без await
    # Список известных async функций
    async_functions = [
        'check_flood',
        'safe_edit_message',
        'start',
        'check_balance',
        'show_stats',
        'buy_stars_menu',
        'process_purchase',
        'precheckout_callback',
        'successful_payment',
        'start_roulette',
        'roulette_bet_type',
        'roulette_place_bet',
        'start_blackjack',
        'blackjack_place_bet',
        'blackjack_hit',
        'blackjack_stand',
        'blackjack_finish_game',
        'start_poker',
        'poker_place_bet',
        'poker_flop',
        'poker_turn',
        'poker_river',
        'poker_showdown',
        'poker_fold',
        'start_chess',
        'chess_bet_type',
        'chess_place_bet',
        'back_to_menu',
        'button_handler',
        'error_handler',
        'periodic_cleanup'
    ]
    
    for func in async_functions:
        # Ищем вызовы без await
        pattern = rf'(?<!await\s)(?<!async\s)(?<!\.)({func}\s*\()'
        
        def add_await(match):
            nonlocal fixes
            # Проверяем что это не определение функции
            line_start = content[:match.start()].rfind('\n')
            line = content[line_start:match.start()]
            
            if 'def ' in line or 'async def' in line:
                return match.group(0)
            
            fixes += 1
            return f'await {match.group(0)}'
        
        old_content = content
        content = re.sub(pattern, add_await, content)
        
        if old_content != content:
            print(f"  ✅ Добавлен await для {func}()")
    
    # 3. Убираем лишние await перед не-async функциями
    non_async_functions = [
        'print',
        'len',
        'str',
        'int',
        'float',
        'dict',
        'list',
        'set',
        'tuple',
        'range',
        'enumerate',
        'zip',
        'map',
        'filter',
        'isinstance',
        'hasattr',
        'getattr',
        'setattr',
        'datetime.now',
        'timedelta',
        'Path',
        'sanitize_text',
        'validate_bet',
        'format_balance',
        'format_stats',
        'create_main_menu',
        'create_back_button',
        'create_bet_keyboard',
        'clean_old_games',
        'set_game_timeout'
    ]
    
    for func in non_async_functions:
        pattern = rf'await\s+({re.escape(func)}\s*\()'
        old_content = content
        content = re.sub(pattern, r'\1', content)
        
        if old_content != content:
            fixes += 1
            print(f"  ✅ Убран лишний await перед {func}()")
    
    # 4. Проверяем правильность отступов
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Заменяем табы на пробелы
        if '\t' in line:
            line = line.replace('\t', '    ')
            fixes += 1
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Сохраняем исправленный файл
    with open(filename, 'w', encoding='Unicode') as f:
        f.write(content)
    
    print(f"\n{'='*50}")
    print(f"✅ Файл исправлен!")
    print(f"📊 Всего исправлений: {fixes}")
    print(f"💾 Бэкап сохранён: {backup}")
    print(f"{'='*50}\n")
    
    return fixes


def validate_python_syntax(filename):
    """Проверяет синтаксис Python файла"""
    import py_compile
    import tempfile
    
    try:
        # Компилируем во временный файл
        with tempfile.NamedTemporaryFile(suffix='.pyc', delete=True) as tmp:
            py_compile.compile(filename, cfile=tmp.name, doraise=True)
        
        print(f"✅ Синтаксис корректен!")
        return True
    
    except py_compile.PyCompileError as e:
        print(f"❌ Ошибка синтаксиса:")
        print(f"  {e}")
        return False


if __name__ == '__main__':
    print("🚀 Автоматическое исправление async/await ошибок\n")
    
    filename = "C:\Users\User\source\repos\StarsCasinoBot\main.py"
    
    if not Path(filename).exists():
        print(f"❌ Файл {filename} не найден!")
        exit(1)
    
    # Исправляем ошибки
    total_fixes = fix_async_errors(filename)
    
    # Проверяем синтаксис
    print("\n📝 Проверка синтаксиса...")
    if validate_python_syntax(filename):
        print(f"\n🎉 Готово! Исправлено {total_fixes} ошибок")
    else:
        print("\n⚠️  Требуется ручная проверка")

