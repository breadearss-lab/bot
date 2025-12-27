import sys

def check_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    bad_chars = {
        ''': "LEFT SINGLE QUOTATION MARK",
        ''': "RIGHT SINGLE QUOTATION MARK",
        '"': "LEFT DOUBLE QUOTATION MARK",
        '"': "RIGHT DOUBLE QUOTATION MARK"
    }
    
    errors = []
    for line_num, line in enumerate(content.split('\n'), 1):
        for char, name in bad_chars.items():
            if char in line:
                errors.append(f"Строка {line_num}: найден {name}")
    
    if errors:
        print("Найдены неправильные кавычки:")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ Все кавычки правильные!")

if __name__ == '__main__':
    check_file('StarsCasinoBot/main.py')