import shutil
from pathlib import Path

def fix_file(filename):
    """Исправляет все проблемы в файле"""
    
    # Бэкап
    backup = filename + '.backup'
    shutil.copy(filename, backup)
    
    # Читаем
    with open(filename, 'r', encoding='UTF-16') as f:
        content = f.read()
    
    # Исправляем кавычки
    quotes = {
        ''': "'", ''': "'",
        '"': '"', '"': '"',
        '‚': "'", '„': '"',
    }
    
    for bad, good in quotes.items():
        content = content.replace(bad, good)
    
    # Исправляем табы
    content = content.replace('\t', '    ')
    
    # Сохраняем
    with open(filename, 'w', encoding='UTF-16') as f:
        f.write(content)
    
    print(f"✅ Исправлен: {filename}")

if __name__ == '__main__':
    files = [
        'StarsCasinoBot/main.py',
        'config.py', 
        'database.py',
        'utils.py',
        'games/roulette.py',
        'games/blackjack.py',
        'games/poker.py',
        'games/chess.py'
    ]
    
    print("🔧 Исправление всех файлов...\n")
    
    for f in files:
        if Path(f).exists():
            fix_file(f)
    
    print("\n🎉 Готово!")