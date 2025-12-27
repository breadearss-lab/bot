import re

def fix_indentation(filename):
    """Исправляет отступы в файле"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем табы на 4 пробела
    content = content.replace('\t', '    ')
    
    # Сохраняем
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Исправлены отступы в {filename}")

if __name__ == '__main__':
    fix_indentation('StarsCasinoBot/main.py')