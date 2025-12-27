import re
from pathlib import Path

def fix_if_return_errors(filename):
    """Исправляет все ошибки связанные с if, return, и структурой кода"""
    
    print(f"🔧 Исправление структуры кода в: {filename}\n")
    
    # Создаём бэкап
    backup = filename + '.backup'
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    with open(backup, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"💾 Бэкап создан: {backup}\n")
    
    fixed_lines = []
    fixes = 0
    i = 0
    
    while i < len(lines):
        line = lines[i]
        original_line = line
        
        # 1. Исправляем return вне функций
        if line.strip().startswith('return') and i > 0:
            # Проверяем, находимся ли мы внутри функции
            indent = len(line) - len(line.lstrip())
            
            # Ищем определение функции выше
            found_function = False
            for j in range(i - 1, -1, -1):
                prev_line = lines[j].strip()
                prev_indent = len(lines[j]) - len(lines[j].lstrip())
                
                if prev_line.startswith('def ') or prev_line.startswith('async def '):
                    if prev_indent < indent:
                        found_function = True
                        break
                
                # Если нашли строку с меньшим отступом (не пустую) - значит вне функции
                if prev_line and prev_indent < indent and not prev_line.startswith('#'):
                    break
            
            if not found_function:
                # return вне функции - заменяем на pass или удаляем
                print(f"  ⚠️  Строка {i+1}: return вне функции - заменён на pass")
                line = ' ' * indent + 'pass\n'
                fixes += 1
        
        # 2. Исправляем if без тела
        if line.strip().endswith(':') and ('if ' in line or 'elif ' in line or 'else:' in line):
            # Проверяем следующую строку
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                current_indent = len(line) - len(line.lstrip())
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Если следующая строка не имеет большего отступа или пустая
                if next_line.strip() == '' or next_indent <= current_indent:
                    print(f"  ⚠️  Строка {i+1}: if/else без тела - добавлен pass")
                    fixed_lines.append(line)
                    fixed_lines.append(' ' * (current_indent + 4) + 'pass\n')
                    fixes += 1
                    i += 1
                    continue
        
        # 3. Исправляем функции без тела
        if line.strip().startswith('def ') or line.strip().startswith('async def '):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                current_indent = len(line) - len(line.lstrip())
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Если это docstring, проверяем что после него есть код
                if next_line.strip().startswith('"""') or next_line.strip().startswith("'''"):
                    # Ищем конец docstring
                    quote = '"""' if '"""' in next_line else "'''"
                    j = i + 1
                    
                    # Если docstring на одной строке
                    if next_line.count(quote) >= 2:
                        j += 1
                    else:
                        # Многострочный docstring
                        j += 1
                        while j < len(lines) and quote not in lines[j]:
                            j += 1
                        j += 1
                    
                    # Проверяем что после docstring есть код
                    if j < len(lines):
                        after_doc = lines[j]
                        after_indent = len(after_doc) - len(after_doc.lstrip())
                        
                        if after_doc.strip() == '' or after_indent <= current_indent:
                            print(f"  ⚠️  Строка {i+1}: Функция без тела - добавлен pass")
                            fixed_lines.append(line)
                            fixed_lines.append(next_line)
                            
                            # Копируем docstring
                            k = i + 2
                            while k < j:
                                fixed_lines.append(lines[k])
                                k += 1
                            
                            fixed_lines.append(' ' * (current_indent + 4) + 'pass\n')
                            fixes += 1
                            i = j
                            continue
                
                elif next_line.strip() == '' or next_indent <= current_indent:
                    print(f"  ⚠️  Строка {i+1}: Функция без тела - добавлен pass")
                    fixed_lines.append(line)
                    fixed_lines.append(' ' * (current_indent + 4) + 'pass\n')
                    fixes += 1
                    i += 1
                    continue
        
        # 4. Исправляем неправильные отступы
        if line.strip() and not line.strip().startswith('#'):
            indent = len(line) - len(line.lstrip())
            
            # Проверяем кратность 4
            if indent % 4 != 0 and indent > 0:
                correct_indent = (indent // 4) * 4
                if indent % 4 >= 2:
                    correct_indent += 4
                
                line = ' ' * correct_indent + line.lstrip()
                print(f"  ⚠️  Строка {i+1}: Исправлен отступ {indent} -> {correct_indent}")
                fixes += 1
        
        # 5. Заменяем табы на пробелы
        if '\t' in line:
            line = line.replace('\t', '    ')
            fixes += 1
        
        fixed_lines.append(line)
        i += 1
    
    # Сохраняем исправленный файл
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"\n{'='*50}")
    print(f"✅ Исправлено ошибок: {fixes}")
    print(f"💾 Бэкап: {backup}")
    print(f"{'='*50}\n")
    
    return fixes


def fix_specific_patterns(filename):
    """Исправляет специфичные паттерны ошибок"""
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes = 0
    
    # 1. Исправляем "if not query:" без блока
    pattern1 = r'(if not query:)\s*\n(\s*)([^\s])'
    
    def fix_if_not_query(match):
        nonlocal fixes
        indent = match.group(2)
        next_code = match.group(3)
        
        # Если следующий код не имеет правильного отступа
        if not next_code.startswith(' ' * (len(indent) + 4)):
            fixes += 1
            return f"{match.group(1)}\n{indent}    return\n{indent}{next_code}"
        return match.group(0)
    
    content = re.sub(pattern1, fix_if_not_query, content)
    
    # 2. Исправляем множественные пустые строки
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # 3. Исправляем пробелы в конце строк
    content = re.sub(r'[ \t]+\n', '\n', content)
    
    if content != original_content:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Исправлено паттернов: {fixes}")
    
    return fixes


def validate_syntax(filename):
    """Проверяет синтаксис Python"""
    import ast
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        ast.parse(code)
        print("✅ Синтаксис корректен!")
        return True
    
    except SyntaxError as e:
        print(f"❌ Синтаксическая ошибка:")
        print(f"  Файл: {e.filename}")
        print(f"  Строка {e.lineno}: {e.msg}")
        print(f"  Текст: {e.text}")
        if e.offset:
            print(f"  " + " " * (e.offset - 1) + "^")
        return False
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def show_errors(filename):
    """Показывает все ошибки в файле"""
    import ast
    
    print(f"\n🔍 Поиск ошибок в {filename}...\n")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        ast.parse(code)
        print("✅ Ошибок не найдено!")
    
    except SyntaxError as e:
        print(f"❌ Найдена ошибка:")
        print(f"  Тип: SyntaxError")
        print(f"  Строка: {e.lineno}")
        print(f"  Сообщение: {e.msg}")
        
        if e.text:
            print(f"\n  Код:")
            print(f"  {e.lineno-1} | ...")
            print(f"  {e.lineno}   | {e.text.rstrip()}")
            
            if e.offset:
                print(f"        | {' ' * (e.offset-1)}^")
            
            # Показываем контекст
            lines = code.split('\n')
            if e.lineno < len(lines):
                print(f"  {e.lineno+1} | {lines[e.lineno]}")
        
        print(f"\n💡 Возможные причины:")
        
        if "unexpected indent" in e.msg:
            print(f"  - Неожиданный отступ")
            print(f"  - Проверьте что используете только пробелы (не табы)")
            print(f"  - Убедитесь что отступ кратен 4 пробелам")
        
        elif "expected an indented block" in e.msg:
            print(f"  - Ожидается блок кода с отступом")
            print(f"  - После : должен быть блок кода")
            print(f"  - Добавьте pass если блок пустой")
        
        elif "'return' outside function" in e.msg or "return" in e.msg:
            print(f"  - return используется вне функции")
            print(f"  - Проверьте отступы")
        
        elif "invalid character" in e.msg:
            print(f"  - Неправильный символ (возможно типографские кавычки)")
            print(f"  - Замените ' и ' на '")
            print(f"  - Замените " " на \"")


if __name__ == '__main__':
    import sys
    
    filename = 'StarsCasinoBot/main.py'
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    if not Path(filename).exists():
        print(f"❌ Файл {filename} не найден!")
        sys.exit(1)
    
    print("🚀 Исправление структуры кода\n")
    print("="*50)
    
    # Показываем текущие ошибки
    show_errors(filename)
    
    print("\n" + "="*50)
    print("\n🔧 Начинаем исправление...\n")
    
    # Исправляем
    total_fixes = 0
    total_fixes += fix_if_return_errors(filename)
    total_fixes += fix_specific_patterns(filename)
    
    # Проверяем результат
    print("\n📝 Финальная проверка...\n")
    
    if validate_syntax(filename):
        print(f"\n🎉 Успешно! Исправлено {total_fixes} ошибок")
        sys.exit(0)
    else:
        print(f"\n⚠️  Остались ошибки. Требуется ручная проверка.")
        print(f"💾 Оригинал сохранён в {filename}.backup")
        sys.exit(1)