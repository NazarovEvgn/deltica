# План разработки

## Реализовать CRUD на фронтэнде (использовать Vue.js, Vite, RevoGrid, Naive UI)
  - создать в файловой структуре Vue.js отдельный компонент для основной таблицы MainTable.vue
  - реализовать базовый вывод данных (далее как get_data_default) в MainTable, который будет отображаться всегда при запуске приложения.
    - get_data_default выводит следующие атрибуты в MainTable: equipment_name, equipment_model, factory_number, inventory_number, verification_type, verification_interval, verification_date, verification_due, verification_plan, verification_state, status
  - реализовать в отдельном компоненте кнопку "Добавить" для добавления нового оборудование через модальное окно с полями всех атрибутов из всех моделей.
  - реализовать в MainTable редактирование и удаление данных.
