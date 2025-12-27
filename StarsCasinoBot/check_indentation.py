import sys

def check_indentation(filename):
    """Проверка отступов в файле"""
    errors = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        # Пропускаем пустые строки и комментарии
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        # Проверяем на табы
        if '\t' in line:
            errors.append(f"Строка {i}: Используются табы вместо пробелов")
        
        # Проверяем на смешанные отступы
        if line.startswith(' ') and '\t' in line[:len(line) - len(line.lstrip())]:
            errors.append(f"Строка {i}: Смешанные табы и пробелы")
        
        # Проверяем кратность 4 пробелам
        indent = len(line) - len(line.lstrip())
        if indent > 0 and indent % 4 != 0:
            errors.append(f"Строка {i}: Отступ {indent} не кратен 4")
    
    if errors:
        print(f"❌ Найдены ошибки в {filename}:")
        for error in errors[:10]:  # Показываем первые 10
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... и ещё {len(errors) - 10} ошибок")
        return False
    else:
        print(f"✅ {filename}: отступы корректны")
        return True

if __name__ == '__main__':
    files = ['main.py', 'config.py', 'database.py', 'utils.py']
    all_ok = all(check_indentation(f) for f in files if Path(f).exists())
    
    if all_ok:
        print("\n🎉 Все файлы проверены!")
    else:
        print("\n⚠️  Требуется исправление отступов")
        sys.exit(1)