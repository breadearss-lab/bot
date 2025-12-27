import ast
import sys
from pathlib import Path
from typing import List, Dict

class DetailedAsyncChecker:
    """Подробная проверка async/await"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.issues: List[Dict] = []
        self.async_functions = set()
        self.all_functions = {}
    
    def check(self) -> bool:
        """Запускает проверку"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            
            # Первый проход - собираем функции
            self._collect_functions(tree)
            
            # Второй проход - анализируем
            self._analyze_tree(tree)
            
            return True
        
        except SyntaxError as e:
            self.issues.append({
                'severity': 'CRITICAL',
                'type': 'SyntaxError',
                'line': e.lineno,
                'message': e.msg,
                'text': e.text
            })
            return False
    
    def _collect_functions(self, tree):
        """Собирает все функции"""
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                self.async_functions.add(node.name)
                self.all_functions[node.name] = {
                    'is_async': True,
                    'line': node.lineno,
                    'uses_await': self._contains_await(node)
                }
            
            elif isinstance(node, ast.FunctionDef):
                uses_await = self._contains_await(node)
                self.all_functions[node.name] = {
                    'is_async': False,
                    'line': node.lineno,
                    'uses_await': uses_await
                }
                
                if uses_await:
                    self.issues.append({
                        'severity': 'ERROR',
                        'type': 'MissingAsync',
                        'line': node.lineno,
                        'function': node.name,
                        'message': f"Функция '{node.name}' использует await, но не async",
                        'fix': f"Добавьте 'async' перед 'def {node.name}'"
                    })
    
    def _analyze_tree(self, tree):
        """Анализирует дерево AST"""
        for node in ast.walk(tree):
            # Проверяем вызовы async функций
            if isinstance(node, ast.Call):
                func_name = self._get_func_name(node)
                
                if func_name in self.async_functions:
                    # Проверяем есть ли await
                    parent = getattr(node, '_parent', None)
                    
                    if not isinstance(parent, ast.Await):
                        self.issues.append({
                            'severity': 'ERROR',
                            'type': 'MissingAwait',
                            'line': node.lineno,
                            'function': func_name,
                            'message': f"Вызов async функции '{func_name}()' без await",
                            'fix': f"Добавьте 'await' перед '{func_name}()'"
                        })
        
        # Добавляем родительские связи
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                child._parent = parent
    
    def _contains_await(self, node) -> bool:
        """Проверяет содержит ли узел await"""
        for child in ast.walk(node):
            if isinstance(child, ast.Await):
                return True
        return False
    
    def _get_func_name(self, node) -> str:
        """Получает имя функции из вызова"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""
    
    def print_report(self):
        """Выводит детальный отчёт"""
        print("\n" + "="*60)
        print("📊 ДЕТАЛЬНЫЙ ОТЧЁТ")
        print("="*60 + "\n")
        
        # Статистика
        print("📈 Статистика:\n")
        print(f"   Всего функций: {len(self.all_functions)}")
        print(f"   Async функций: {len(self.async_functions)}")
        print(f"   Обычных функций: {len(self.all_functions) - len(self.async_functions)}")
        
        # Функции с await но без async
        needs_async = [
            name for name, info in self.all_functions.items()
            if not info['is_async'] and info['uses_await']
        ]
        
        if needs_async:
            print(f"   ⚠️  Требуют async: {len(needs_async)}")
        
        print()
        
        # Проблемы по категориям
        if self.issues:
            print(f"🔍 Найдено проблем: {len(self.issues)}\n")
            
            # Группируем по серьёзности
            critical = [i for i in self.issues if i['severity'] == 'CRITICAL']
            errors = [i for i in self.issues if i['severity'] == 'ERROR']
            warnings = [i for i in self.issues if i['severity'] == 'WARNING']
            
            if critical:
                print(f"❌ КРИТИЧЕСКИЕ ({len(critical)}):")
                for issue in critical[:5]:
                    print(f"   Строка {issue['line']}: {issue['message']}")
                if len(critical) > 5:
                    print(f"   ... и ещё {len(critical) - 5}")
                print()
            
            if errors:
                print(f"⚠️  ОШИБКИ ({len(errors)}):")
                for issue in errors[:10]:
                    print(f"   Строка {issue['line']}: {issue['message']}")
                    if 'fix' in issue:
                        print(f"      💡 {issue['fix']}")
                if len(errors) > 10:
                    print(f"   ... и ещё {len(errors) - 10}")
                print()
            
            if warnings:
                print(f"ℹ️  ПРЕДУПРЕЖДЕНИЯ ({len(warnings)}):")
                for issue in warnings[:5]:
                    print(f"   Строка {issue['line']}: {issue['message']}")
                if len(warnings) > 5:
                    print(f"   ... и ещё {len(warnings) - 5}")
                print()
        
        else:
            print("✅ Проблем не обнаружено!\n")
        
        # Рекомендации
        if self.issues:
            print("💡 РЕКОМЕНДАЦИИ:\n")
            print("   1. Запустите: python fix_await_errors.py main.py")
            print("   2. Проверьте исправления в бэкап-файле")
            print("   3. Запустите тесты после исправления")
        
        print("\n" + "="*60)


def main():
    """Главная функция диагностики"""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'main.py'
    
    if not Path(filename).exists():
        print(f"❌ Файл '{filename}' не найден!")
        sys.exit(1)
    
    print("🔍 Диагностика async/await проблем")
    print(f"📄 Файл: {filename}")
    
    checker = DetailedAsyncChecker(filename)
    
    if checker.check():
        checker.print_report()
        sys.exit(0 if not checker.issues else 1)
    else:
        checker.print_report()
        sys.exit(1)


if __name__ == '__main__':
    main()