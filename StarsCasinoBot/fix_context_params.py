import re
from pathlib import Path

def fix_context_parameters(filename):
    """Добавляет context ко всем async функциям-обработчикам"""
    
    print(f"🔧 Исправление параметров context в: {filename}\n")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Создаём бэкап
    backup = filename + '.backup'
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"💾 Бэкап создан: {backup}\n")
    
    fixes = 0
    
    # Паттерн для async функций с update но без context
    pattern = r'(async def \w+\(update: Update)\):'
    
    def replace_func(match):
        nonlocal fixes
        fixes += 1
        return match.group(1) + ', context: ContextTypes.DEFAULT_TYPE):'
    
    # Заменяем
    new_content = re.sub(pattern, replace_func, content)
    
    # Специальный случай для periodic_cleanup (только context)
    pattern2 = r'async def periodic_cleanup\(\):'
    new_content = re.sub(
        pattern2,
        'async def periodic_cleanup(context: ContextTypes.DEFAULT_TYPE):',
        new_content
    )
    
    if new_content != content:
        fixes += new_content.count('context: ContextTypes.DEFAULT_TYPE') - content.count('context: ContextTypes.DEFAULT_TYPE')
    
    # Сохраняем
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Исправлено функций: {fixes}")
    print(f"\n{'='*60}")
    
    return fixes


if __name__ == '__main__':
    import sys
    
    filename = sys.argv[1] if len(sys.argv) > 1 else 'StarsCasinoBot/main.py'
    
    if not Path(filename).exists():
        print(f"❌ Файл {filename} не найден!")
        sys.exit(1)
    
    fixes = fix_context_parameters(filename)
    
    if fixes > 0:
        print("🎉 Исправление завершено!")
    else:
        print("ℹ️  Исправлений не требуется")