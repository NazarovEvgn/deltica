import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from docxtpl import DocxTemplate

# Загружаем пакетный шаблон
template = DocxTemplate('docs/docx-templates/template_labels_batch.docx')

# Тестовые данные - 3 единицы оборудования
test_data = {
    'equipments': [
        {
            'equipment_name': 'Конус балансирный Васильева',
            'equipment_model': 'КБВ',
            'factory_number': '138',
            'inventory_number': '00-00011466',
            'verification_date': '02.04.2025',
            'verification_due': '01.04.2027',
            'department': 'ГТЛ'
        },
        {
            'equipment_name': 'Манометр',
            'equipment_model': 'МП-100',
            'factory_number': '5678',
            'inventory_number': '00-00022345',
            'verification_date': '15.03.2025',
            'verification_due': '14.03.2026',
            'department': 'ЛБР'
        },
        {
            'equipment_name': 'Термометр ртутный',
            'equipment_model': 'ТЛ-4',
            'factory_number': '9999',
            'inventory_number': '00-00033456',
            'verification_date': '01.01.2025',
            'verification_due': '31.12.2026',
            'department': 'СМТСиК'
        }
    ]
}

# Заполняем шаблон
template.render(test_data)

# Сохраняем результат
output_file = 'test_batch_labels_output.docx'
template.save(output_file)

print(f'✓ Пакет этикеток успешно сгенерирован: {output_file}')
print(f'\nКоличество этикеток: {len(test_data["equipments"])}')
print('\nСодержимое:')
for i, eq in enumerate(test_data['equipments'], 1):
    print(f'{i}. {eq["equipment_name"]} {eq["equipment_model"]} (зав. №{eq["factory_number"]})')
