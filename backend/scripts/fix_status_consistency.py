"""
Скрипт для исправления несоответствий между verification_state и status.
Применяет правильную логику: если состояние не "В работе", то статус должен дублировать состояние.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from backend.core.config import settings

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def fix_status_consistency():
    """Исправляет статусы для оборудования в нерабочих состояниях"""
    engine = create_engine(settings.DATABASE_URL)

    # Маппинг состояний в статусы
    state_to_status_map = {
        'state_storage': 'status_storage',
        'state_verification': 'status_verification',
        'state_repair': 'status_repair'
    }

    with engine.begin() as conn:  # автоматический коммит при успехе
        try:
            total_fixed = 0

            for state, correct_status in state_to_status_map.items():
                # Находим записи с неправильным статусом
                result = conn.execute(text('''
                    SELECT COUNT(*)
                    FROM verification
                    WHERE verification_state = :state
                    AND status != :correct_status
                '''), {'state': state, 'correct_status': correct_status})
                count = result.scalar()

                if count > 0:
                    print(f'\nИсправление {count} записей с состоянием {state}...')

                    # Обновляем статус
                    result = conn.execute(text('''
                        UPDATE verification
                        SET status = :correct_status
                        WHERE verification_state = :state
                        AND status != :correct_status
                    '''), {'state': state, 'correct_status': correct_status})

                    total_fixed += count
                    print(f'✓ Исправлено: {state} → {correct_status} (затронуто строк: {result.rowcount})')

            print(f'\n{"="*60}')
            print(f'Всего исправлено записей: {total_fixed}')

        except Exception as e:
            print(f'\n✗ Ошибка при исправлении: {e}')
            raise

    # Проверяем результат в отдельном соединении
    with engine.connect() as conn:
        print(f'\n{"="*60}')
        print('Проверка после исправления:')
        result = conn.execute(text('''
            SELECT
                verification_state,
                status,
                COUNT(*) as count
            FROM verification
            WHERE verification_state IN ('state_storage', 'state_verification', 'state_repair')
            GROUP BY verification_state, status
            ORDER BY verification_state, status
        '''))

        print('Состояние | Статус | Количество')
        print('=' * 60)
        for row in result:
            match = '✓' if row[0].replace('state_', 'status_') == row[1] else '✗ ОШИБКА'
            print(f'{row[0]} | {row[1]} | {row[2]} {match}')

        print(f'\n{"="*60}')
        print('✓ Исправление завершено успешно!')


if __name__ == '__main__':
    print('Скрипт исправления несоответствий verification_state и status')
    print('=' * 60)
    fix_status_consistency()
