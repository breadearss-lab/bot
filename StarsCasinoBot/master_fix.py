import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

class MasterFixer:
    """Главный класс для исправления всех проблем"""
    
    def __init__(self, project_dir='.'):
        self.project_dir = Path(project_dir)
        self.backup_dir = self.project_dir / 'backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
        self.fixes_log = []
    
    def create_full_backup(self):
        """Создаёт полную резервную копию проекта"""
        print("💾 Создание резервной копии проекта...")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        python_files = list(self.project_dir.glob('*.py'))
        python_files.extend(self.project_dir.glob('games/*.py'))
        
        for file in python_files:
            if file.is_file():
                backup_file = self.backup_dir / file.name
                shutil.copy2(file, backup_file)
        
        print(f"   ✅ Бэкап создан: {self.backup_dir}\n")
    
    def fix_quotes(self):
        """Исправляет типографские кавычки"""
        print("🔧 Исправление кавычек...")
        
        replacements = {
            ''': "'",
            ''': "'",
            '"': '"',
            '"': '"',
            '‚': "'",
            '„': '"',
        }
        
        files = list(self.project_dir.glob('*.py'))
        files.extend(self.project_dir.glob('games/*.py'))
        
        total_fixes = 0
        
        for file in files:
            if not file.is_file():
                continue
            
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            for bad, good in replacements.items():
                content = content.replace(bad, good)
            
            if content != original:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixes = sum(original.count(bad) for bad in replacements.keys())
                total_fixes += fixes
                print(f"   ✅ {file.name}: {fixes} замен")
        
        self.fixes_log.append(f"Кавычки: {total_fixes} исправлений")
        print(f"   Всего исправлено: {total_fixes}\n")
    
    def fix_indentation(self):
        """Исправляет отступы"""
        print("🔧 Исправление отступов...")
        
        files = list(self.project_dir.glob('*.py'))
        files.extend(self.project_dir.glob('games/*.py'))
        
        total_fixes = 0
        
        for file in files:
            if not file.is_file():
                continue
            
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            fixed_lines = []
            file_fixes = 0
            
            for line in lines:
                original = line
                
                # Заменяем табы на пробелы
                if '\t' in line:
                    line = line.replace('\t', '    ')
                    file_fixes += 1
                
                # Убираем пробелы в конце
                if line.rstrip() != line.rstrip(' \t'):
                    line = line.rstrip() + '\n' if line.endswith('\n') else line.rstrip()
                    file_fixes += 1
                
                fixed_lines.append(line)
            
            if file_fixes > 0:
                with open(file, 'w', encoding='utf-8') as f:
                    f.writelines(fixed_lines)
                
                total_fixes += file_fixes
                print(f"   ✅ {file.name}: {file_fixes} исправлений")
        
        self.fixes_log.append(f"Отступы: {total_fixes} исправлений")
        print(f"   Всего исправлено: {total_fixes}\n")
    
    def fix_empty_blocks(self):
        """Исправляет пустые блоки кода"""
        print("🔧 Исправление пустых блоков...")
        
        files = list(self.project_dir.glob('*.py'))
        files.extend(self.project_dir.glob('games/*.py'))
        
        total_fixes = 0
        
        for file in files:
            if not file.is_file():
                continue
            
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            fixed_lines = []
            i = 0
            file_fixes = 0
            
            while i < len(lines):
                line = lines[i]
                fixed_lines.append(line)
                
                # Проверяем блоки с :
                if line.strip().endswith(':'):
                    current_indent = len(line) - len(line.lstrip())
                    
                    # Проверяем следующую строку
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        next_indent = len(next_line) - len(next_line.lstrip())
                        
                        # Если следующая строка не имеет отступа или это не docstring
                        if (next_line.strip() == '' or next_indent <= current_indent) and \
                           not next_line.strip().startswith('"""') and \
                           not next_line.strip().startswith("'''"):
                            # Добавляем pass
                            fixed_lines.append(' ' * (current_indent + 4) + 'pass\n')
                            file_fixes += 1
                
                i += 1
            
            if file_fixes > 0:
                with open(file, 'w', encoding='utf-8') as f:
                    f.writelines(fixed_lines)
                
                total_fixes += file_fixes
                print(f"   ✅ {file.name}: {file_fixes} блоков")
        
        self.fixes_log.append(f"Пустые блоки: {total_fixes} исправлений")
        print(f"   Всего исправлено: {total_fixes}\n")
    
    def fix_await_async(self):
        """Исправляет проблемы с await/async"""
        print("🔧 Исправление await/async...")
        
        # Импортируем наш фиксер
        try:
            from fix_await_errors import AwaitFixer
            
            files = ['main.py', 'database.py', 'utils.py']
            games_files = list(self.project_dir.glob('games/*.py'))
            files.extend([str(f.name) for f in games_files])
            
            total_fixes = 0
            
            for filename in files:
                filepath = self.project_dir / filename
                
                if not filepath.exists():
                    continue
                
                fixer = AwaitFixer(str(filepath))
                fixer.load_file()
                fixer.collect_async_functions()
                errors = fixer.analyze_errors()
                
                if errors:
                    fixed = fixer.fix_all_errors(errors)
                    if fixed > 0:
                        fixer.save_file()
                        total_fixes += fixed
                        print(f"   ✅ {filename}: {fixed} исправлений")
            
            self.fixes_log.append(f"Await/Async: {total_fixes} исправлений")
            print(f"   Всего исправлено: {total_fixes}\n")
        
        except ImportError:
            print("   ⚠️  Модуль fix_await_errors.py не найден, пропускаем...\n")
    
    def validate_all(self):
        """Проверяет все файлы на синтаксис"""
        print("📝 Проверка синтаксиса...")
        
        import ast
        
        files = list(self.project_dir.glob('*.py'))
        files.extend(self.project_dir.glob('games/*.py'))
        
        errors = []
        
        for file in files:
            if not file.is_file():
                continue
            
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                ast.parse(code)
                print(f"   ✅ {file.name}")
            
            except SyntaxError as e:
                errors.append({
                    'file': file.name,
                    'line': e.lineno,
                    'message': e.msg
                })
                print(f"   ❌ {file.name}: строка {e.lineno} - {e.msg}")
        
        print()
        return len(errors) == 0, errors
    
    def print_summary(self, success, errors):
        """Выводит итоговую сводку"""
        print("\n" + "="*60)
        print("📊 ИТОГОВЫЙ ОТЧЁТ")
        print("="*60 + "\n")
        
        print("Выполненные исправления:\n")
        for log in self.fixes_log:
            print(f"   • {log}")
        
        print(f"\n💾 Резервная копия: {self.backup_dir}")
        
        if success:
            print("\n" + "="*60)
            print("✅ ВСЕ ФАЙЛЫ ИСПРАВЛЕНЫ УСПЕШНО!")
            print("="*60)
        else:
            print("\n❌ Обнаружены ошибки синтаксиса:\n")
            for error in errors:
                print(f"   {error['file']}, строка {error['line']}: {error['message']}")
            print("\n💡 Требуется ручное исправление этих ошибок")
            print("="*60)
    
    def run(self):
        """Запускает полное исправление"""
        print("="*60)
        print("🚀 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ ПРОЕКТА")
        print("="*60)
        print()
        
        # Шаг 1: Бэкап
        self.create_full_backup()
        
        # Шаг 2: Исправление кавычек
        self.fix_quotes()
        
        # Шаг 3: Исправление отступов
        self.fix_indentation()
        
        # Шаг 4: Исправление пустых блоков
        self.fix_empty_blocks()
        
        # Шаг 5: Исправление await/async
        self.fix_await_async()
        
        # Шаг 6: Валидация
        success, errors = self.validate_all()
        
        # Итоги
        self.print_summary(success, errors)
        
        return success


def main():
    """Главная функция"""
    project_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    fixer = MasterFixer(project_dir)
    success = fixer.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()