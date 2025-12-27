import ast
import re 
from pathlib import Path 
from typing import Set, Dict, List, Tuple 
import sys

class AsyncFunctionCollector(ast.NodeVisitor): 
    """Собирает все async функции из кода"""

def __init__(self):
    self.async_functions: Set[str] = set()
    self.regular_functions: Set[str] = set()

def visit_AsyncFunctionDef(self, node):
    """Регистрируем async функции"""
    self.async_functions.add(node.name)
    self.generic_visit(node)

def visit_FunctionDef(self, node):
    """Регистрируем обычные функции"""
    self.regular_functions.add(node.name)
    self.generic_visit(node)
class AwaitAnalyzer(ast.NodeVisitor): """Анализирует использование await в коде"""

def __init__(self, async_functions: Set[str]):
    self.async_functions = async_functions
    self.errors: List[Dict] = []
    self.current_function = None
    self.is_in_async_function = False
    self.function_stack = []

def visit_AsyncFunctionDef(self, node):
    """Анализируем async функции"""
    self.function_stack.append({
        'name': node.name,
        'is_async': True,
        'lineno': node.lineno
    })

    old_func = self.current_function
    old_is_async = self.is_in_async_function

    self.current_function = node.name
    self.is_in_async_function = True

    self.generic_visit(node)

    self.current_function = old_func
    self.is_in_async_function = old_is_async
    self.function_stack.pop()

def visit_FunctionDef(self, node):
    """Анализируем обычные функции"""
    self.function_stack.append({
        'name': node.name,
        'is_async': False,
        'lineno': node.lineno
    })

    # Проверяем использует ли функция await
    has_await = self._has_await_in_body(node)

    if has_await:
        self.errors.append({
            'type': 'missing_async',
            'line': node.lineno,
            'function': node.name,
            'message': f"Функция '{node.name}' использует await, но не объявлена как async"
        })

    old_func = self.current_function
    old_is_async = self.is_in_async_function

    self.current_function = node.name
    self.is_in_async_function = False

    self.generic_visit(node)

    self.current_function = old_func
    self.is_in_async_function = old_is_async
    self.function_stack.pop()

def visit_Await(self, node):
    """Проверяем использование await"""
    if not self.is_in_async_function:
        self.errors.append({
            'type': 'await_outside_async',
            'line': node.lineno,
            'function': self.current_function,
            'message': f"await используется вне async функции"
        })

    self.generic_visit(node)

def visit_Call(self, node):
    """Проверяем вызовы async функций"""
    func_name = self._get_function_name(node)

    if func_name in self.async_functions:
        # Проверяем есть ли await
        if not self._is_awaited(node):
            self.errors.append({
                'type': 'missing_await',
                'line': node.lineno,
                'function': func_name,
                'message': f"Вызов async функции '{func_name}' без await"
            })

    self.generic_visit(node)

def _get_function_name(self, node) -> str:
    """Получает имя вызываемой функции"""
    if isinstance(node.func, ast.Name):
        return node.func.id
    elif isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""

def _is_awaited(self, node) -> bool:
    """Проверяет используется ли await перед вызовом"""
    # Это упрощенная проверка через родительский узел
    parent = getattr(node, '_parent', None)
    return isinstance(parent, ast.Await)

def _has_await_in_body(self, node) -> bool:
    """Проверяет есть ли await в теле функции"""
    for child in ast.walk(node):
        if isinstance(child, ast.Await):
            return True
    return False
class AwaitFixer: """Исправляет await/async ошибки в коде"""

def __init__(self, filename: str):
    self.filename = filename
    self.lines: List[str] = []
    self.async_functions: Set[str] = set()
    self.fixes_applied = 0

def load_file(self):
    """Загружает файл"""
    with open(self.filename, 'r', encoding='Unicode') as f:
        self.lines = f.readlines()

def save_file(self):
    """Сохраняет файл"""
    with open(self.filename, 'w', encoding='Unicode') as f:
        f.writelines(self.lines)

def create_backup(self):
    """Создает резервную копию"""
    backup_path = self.filename + '.backup'
    with open(backup_path, 'w', encoding='Unicode') as f:
        f.writelines(self.lines)
    return backup_path

def collect_async_functions(self):
    """Собирает все async функции"""
    try:
        code = ''.join(self.lines)
        tree = ast.parse(code)

        collector = AsyncFunctionCollector()
        collector.visit(tree)

        self.async_functions = collector.async_functions

        # Добавляем известные async функции из Telegram
        telegram_async = {
            'answer', 'edit_message_text', 'send_message', 
            'send_invoice', 'reply_text', 'delete_message'
        }
        self.async_functions.update(telegram_async)

        return True
    except SyntaxError:
        return False

def analyze_errors(self) -> List[Dict]:
    """Анализирует ошибки в коде"""
    try:
        code = ''.join(self.lines)
        tree = ast.parse(code)

        # Добавляем родительские связи
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                child._parent = parent

        analyzer = AwaitAnalyzer(self.async_functions)
        analyzer.visit(tree)

        return analyzer.errors
    except SyntaxError as e:
        return [{
            'type': 'syntax_error',
            'line': e.lineno,
            'message': str(e.msg)
        }]

def fix_missing_async(self, line_num: int) -> bool:
    """Добавляет async к функции"""
    if line_num <= 0 or line_num > len(self.lines):
        return False

    line = self.lines[line_num - 1]

    if 'def ' in line and 'async def' not in line:
        # Добавляем async перед def
        self.lines[line_num - 1] = line.replace('def ', 'async def ', 1)
        self.fixes_applied += 1
        return True

    return False

def fix_missing_await(self, line_num: int, function_name: str) -> bool:
    """Добавляет await перед вызовом функции"""
    if line_num <= 0 or line_num > len(self.lines):
        return False

    line = self.lines[line_num - 1]

    # Проверяем что это не определение функции
    if 'def ' in line:
        return False

    # Ищем вызов функции без await
    pattern = rf'(?<!await\s)(?<!await\s\s)({re.escape(function_name)}\s*\()'

    if re.search(pattern, line):
        # Добавляем await
        new_line = re.sub(
            pattern,
            rf'await \1',
            line,
            count=1
        )
        self.lines[line_num - 1] = new_line
        self.fixes_applied += 1
        return True

    return False

def fix_await_outside_async(self, line_num: int) -> bool:
    """Исправляет await вне async функции"""
    if line_num <= 0 or line_num > len(self.lines):
        return False

    # Находим функцию содержащую эту строку
    for i in range(line_num - 1, -1, -1):
        line = self.lines[i]

        if 'def ' in line:
            # Нашли функцию - делаем её async
            if 'async def' not in line:
                self.lines[i] = line.replace('def ', 'async def ', 1)
                self.fixes_applied += 1
                return True
            break

    return False

def fix_all_errors(self, errors: List[Dict]) -> int:
    """Исправляет все найденные ошибки"""
    fixed = 0

    # Сортируем ошибки по типу для правильного порядка исправления
    errors_sorted = sorted(errors, key=lambda x: (
        0 if x['type'] == 'missing_async' else
        1 if x['type'] == 'await_outside_async' else 2
    ))

    for error in errors_sorted:
        error_type = error['type']
        line_num = error['line']

        if error_type == 'missing_async':
            if self.fix_missing_async(line_num):
                print(f"  ✅ Строка {line_num}: Добавлен async к функции '{error['function']}'")
                fixed += 1

        elif error_type == 'await_outside_async':
            if self.fix_await_outside_async(line_num):
                print(f"  ✅ Строка {line_num}: Функция сделана async")
                fixed += 1

        elif error_type == 'missing_await':
            if self.fix_missing_await(line_num, error['function']):
                print(f"  ✅ Строка {line_num}: Добавлен await перед '{error['function']}'")
                fixed += 1

    return fixed

def validate_syntax(self) -> Tuple[bool, str]:
    """Проверяет синтаксис после исправлений"""
    try:
        code = ''.join(self.lines)
        ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Строка {e.lineno}: {e.msg}"

def run(self) -> bool:
    """Запускает процесс исправления"""
    print(f"🔧 Анализ файла: {self.filename}\n")

    # Загружаем файл
    self.load_file("StarsCasinoBot/main.py")

    # Создаём бэкап
    backup = self.create_backup()
    print(f"💾 Создан бэкап: {backup}\n")

    # Собираем async функции
    print("📋 Сбор async функций...")
    if not self.collect_async_functions():
        print("⚠️  Файл содержит синтаксические ошибки\n")

    print(f"   Найдено async функций: {len(self.async_functions)}\n")

    # Анализируем ошибки
    print("🔍 Поиск ошибок...")
    errors = self.analyze_errors()

    if not errors:
        print("✅ Ошибок не найдено!\n")
        return True

    print(f"   Найдено ошибок: {len(errors)}\n")

    # Группируем ошибки по типу
    error_types = {}
    for error in errors:
        error_type = error['type']
        if error_type not in error_types:
            error_types[error_type] = []
        error_types[error_type].append(error)

    print("📊 Типы ошибок:")
    for error_type, err_list in error_types.items():
        type_names = {
            'missing_async': 'Отсутствует async',
            'missing_await': 'Отсутствует await',
            'await_outside_async': 'await вне async функции',
            'syntax_error': 'Синтаксическая ошибка'
        }
        print(f"   {type_names.get(error_type, error_type)}: {len(err_list)}")

    print("\n" + "="*50)
    print("🔧 Начинаем исправление...\n")

    # Исправляем ошибки
    fixed = self.fix_all_errors(errors)

    if fixed > 0:
        # Сохраняем изменения
        self.save_file()
        print(f"\n💾 Изменения сохранены\n")

        # Проверяем синтаксис
        print("📝 Проверка синтаксиса...")
        is_valid, message = self.validate_syntax()

        if is_valid:
            print("✅ Синтаксис корректен!\n")
            print("="*50)
            print(f"🎉 Успешно исправлено: {fixed} ошибок")
            print("="*50)
            return True
        else:
            print(f"❌ Ошибка синтаксиса: {message}\n")
            print("⚠️  Требуется ручная проверка")
            return False
    else:
        print("\n⚠️  Не удалось автоматически исправить ошибки")
        print("💡 Попробуйте исправить вручную или проверьте бэкап")
        return False