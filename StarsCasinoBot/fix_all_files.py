import sys
from pathlib import Path
from typing import List

# Импортируем наш фиксер
sys.path.insert(0, str(Path(__file__).parent))
from fix_await_errors import AwaitFixer

def fix_all_files(file_patterns: List[str]) -> dict:
    """Исправляет все файлы по паттернам"""
    
    results = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'files': {}
    }
    
    files_to_fix = []
    
    # Собираем все файлы
    for pattern in file_patterns:
        if '*' in pattern:
            # Glob паттерн
            files_to_fix.extend(Path('.').glob(pattern))
        else:
            # Конкретный файл
            p = Path(pattern)
            if p.exists():
                files_to_fix.append(p)
    
    # Убираем дубликаты
    files_to_fix = list(set(files_to_fix))
    
    print(f"🔧 Найдено файлов для исправления: {len(files_to_fix)}\n")
    
    for filepath in files_to_fix:
        filename = str(filepath)
        print(f"\n{'='*60}")
        print(f"📄 Обработка: {filename}")
        print('='*60)
        
        fixer = AwaitFixer(filepath)
        success = fixer.run()
        
        results['total'] += 1
        results['files'][filename] = {
            'success': success,
            'fixes': fixer.fixes_applied
        }
        
        if success:
            results['success'] += 1
        else:
            results['failed'] += 1
    
    return results


def print_summary(results: dict):
    """Выводит итоговый отчёт"""
    print("\n" + "="*60)
    print("📊 ИТОГОВЫЙ ОТЧЁТ")
    print("="*60 + "\n")
    
    print(f"Всего файлов обработано: {results['total']}")
    print(f"✅ Успешно: {results['success']}")
    print(f"❌ С ошибками: {results['failed']}\n")
    
    if results['files']:
        print("Детали по файлам:\n")
        for filename, info in results['files'].items():
            status = "✅" if info['success'] else "❌"
            print(f"{status} {filename}")
            print(f"   Исправлений: {info['fixes']}")
        print()
    
    print("="*60)


def main():
    """Главная функция пакетного исправления"""
    
    # Паттерны файлов для исправления
    file_patterns = [
        "StarsCasinoBot main.py",
        "StarsCasinoBot database.py",
        "StarsCasinoBot utils.py",
        "StarsCasinoBot games/*.py"
    ]
    
    # Можно передать свои паттерны
    if len(sys.argv) > 1:
        file_patterns = sys.argv[1:]
    
    print("🚀 Пакетное исправление await/async ошибок")
    print(f"📋 Паттерны: {', '.join(file_patterns)}\n")
    
    results = fix_all_files(file_patterns)
    print_summary(results)
    
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()