import ast
import sys
from pathlib import Path

class AsyncChecker(ast.NodeVisitor):
    """Проверяет правильность использования async/await"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.current_function = None
        self.async_functions = set()
    
    def visit_AsyncFunctionDef(self, node):
        """Посещаем async функции"""
        self.async_functions.add(node.name)
        old_func = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_func
    
    def visit_FunctionDef(self, node):
        """Посещаем обычные функции"""
        old_func = self.current_function
        self.current_function = node.name
        
        # Проверяем есть ли await в обычной функции
        for child in ast.walk(node):
            if isinstance(child, ast.Await):
                self.errors.append(
                    f"Строка {node.lineno}: Функция '{node.name}' использует await, "
                    f"но не объявлена как async"
                )
                break
        
        self.generic_visit(node)
        self.current_function = old_func
    
    def visit_Await(self, node):
        """Проверяем использование await"""
        if self.current_function is None:
            self.errors.append(
                f"Строка {node.lineno}: await используется вне функции"
            )
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Проверяем вызовы функций"""
        # Получаем имя вызываемой функции
        func_name = None
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        # Проверяем вызовы async функций без await
        if func_name in self.async_functions:
            # Проверяем есть ли await перед вызовом
            # Это упрощённая проверка
            parent = getattr(node, 'parent', None)
            if not isinstance(parent, ast.Await):
                self.warnings.append(
                    f"Строка {node.lineno}: Возможно отсутствует await "
                    f"перед вызовом async функции '{func_name}'"
                )
        
        self.generic_visit(node)


def check_file(filename):
    """Проверяет файл на async/await проблемы"""
    
    print(f"🔍 Проверка файла: {filename}\n")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим AST
        tree = ast.parse(content)
        
        # Добавляем родительские ссылки
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                child.parent = parent
        
        # Проверяем
        checker = AsyncChecker()
        checker.visit(tree)
        
        # Выводим результаты
        if checker.errors:
            print("❌ ОШИБКИ:")
            for error in checker.errors:
                print(f"  {error}")
            print()
        
        if checker.warnings:
            print("⚠️  ПРЕДУПРЕЖДЕНИЯ:")
            for warning in checker.warnings:
                print(f"  {warning}")
            print()
        
        if not checker.errors and not checker.warnings:
            print("✅ Проблем не обнаружено!")
        
        print(f"\n📊 Статистика:")
        print(f"  Async функций: {len(checker.async_functions)}")
        print(f"  Ошибок: {len(checker.errors)}")
        print(f"  Предупреждений: {len(checker.warnings)}")
        
        return len(checker.errors) == 0
    
    except SyntaxError as e:
        print(f"❌ Синтаксическая ошибка в файле:")
        print(f"  Строка {e.lineno}: {e.msg}")
        return False
    
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'StarsCasinoBot/main.py'
    
    if not Path(filename).exists():
        print(f"❌ Файл {filename} не найден!")
        sys.exit(1)
    
    success = check_file(filename)
    sys.exit(0 if success else 1)