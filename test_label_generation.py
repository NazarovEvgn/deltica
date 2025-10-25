import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from docxtpl import DocxTemplate
from datetime import datetime

# Загружаем шаблон
template = DocxTemplate('docs/docx-templates/template_label.docx')

# Тестовые данные (Конус Васильева зав. № 138)
context = {
    'equipment_name': 'Конус балансирный Васильева',
    'equipment_model': 'КБВ',
    'factory_number': '138',
    'inventory_number': '00-00011466',
    'verification_date': '02.04.2025',
    'verification_due': '01.04.2027',
    'department': 'ГТЛ'
}

# Заполняем шаблон
template.render(context)

# Сохраняем результат
output_file = 'test_label_output.docx'
template.save(output_file)

print(f'✓ Этикетка успешно сгенерирована: {output_file}')
print(f'\nИспользованные данные:')
for key, value in context.items():
    print(f'  {key}: {value}')
