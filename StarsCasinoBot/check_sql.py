import re
import sqlite3

def check_sql_in_file(filename):
    """Проверяет SQL синтаксис в Python файле"""
    
    print(f"🔍 Проверка SQL в: {filename}\n")
    
    with open(filename, 'r', encoding='ASCII') as f:
        content = f.read()
    
    # Находим все SQL запросы
    sql_pattern = r"cursor\.execute\('''(.*?)'''"
    sql_queries = re.findall(sql_pattern, content, re.DOTALL)
    
    # Также ищем с двойными кавычками
    sql_pattern2 = r'cursor\.execute\("""(.*?)"""'
    sql_queries.extend(re.findall(sql_pattern2, content, re.DOTALL))
    
    print(f"Найдено SQL запросов: {len(sql_queries)}\n")
    
    errors = []
    
    for i, query in enumerate(sql_queries, 1):
        try:
            # Пытаемся создать временную БД и выполнить запрос
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute(query)
            conn.close()
            
            print(f"✅ Запрос {i}: OK")
        
        except sqlite3.Error as e:
            errors.append((i, str(e), query[:100]))
            print(f"❌ Запрос {i}: {e}")
    
    if errors:
        print(f"\n❌ Найдено ошибок: {len(errors)}\n")
        for i, error, query_preview in errors:
            print(f"Запрос {i}:")
            print(f"  Ошибка: {error}")
            print(f"  Начало: {query_preview}...\n")
        return False
    else:
        print(f"\n✅ Все SQL запросы корректны!")
        return True


if __name__ == '__main__':
    import sys
    
    filename = sys.argv[1] if len(sys.argv) > 1 else 'StarsCasinoBot/database.py'
    
    check_sql_in_file(filename)