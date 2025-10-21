import { computed } from 'vue'

/**
 * Composable для расчета аналитических данных по верификации оборудования
 * @param {Ref<Array>} equipmentData - реактивный массив оборудования из базы данных
 * @returns {Object} - объект с вычисляемыми свойствами аналитики
 */
export function useAnalytics(equipmentData) {
  // Текущий год
  const currentYear = new Date().getFullYear()

  // Карта названий подразделений (технические значения → отображаемые названия)
  // Исключены: Группа СМ (gruppa_sm), ОГМК (ogmk)
  const departmentMap = {
    gtl: 'ГТЛ',
    lbr: 'ЛБР',
    ltr: 'ЛТР',
    lhaiei: 'ЛХАиЭИ',
    oii: 'ОИИ',
    ooops: 'ОООПС',
    smtsik: 'СМТСиК',
    soii: 'СОИИ',
    to: 'ТО',
    ts: 'ТС',
    es: 'ЭС'
  }

  // Названия месяцев
  const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ]

  /**
   * Календарь верификаций: количество оборудования по подразделениям и месяцам
   * Структура: Array<{ department: string, monthCounts: Array<number> }>
   */
  const verificationCalendar = computed(() => {
    const calendar = []

    // Проходим по всем подразделениям
    Object.keys(departmentMap).forEach(deptKey => {
      const monthCounts = Array(12).fill(0) // Массив для 12 месяцев

      // Фильтруем оборудование по подразделению
      const deptEquipment = equipmentData.value.filter(
        item => item.department === deptKey
      )

      // Подсчитываем оборудование по месяцам на основе verification_plan
      deptEquipment.forEach(item => {
        if (item.verification_plan) {
          const planDate = new Date(item.verification_plan)
          const planYear = planDate.getFullYear()
          const planMonth = planDate.getMonth() // 0-11

          // Учитываем только текущий год
          if (planYear === currentYear) {
            monthCounts[planMonth]++
          }
        }
      })

      calendar.push({
        department: departmentMap[deptKey],
        departmentKey: deptKey,
        monthCounts
      })
    })

    return calendar
  })

  /**
   * Итоговая строка: сумма по месяцам по всем подразделениям
   */
  const monthlyTotals = computed(() => {
    const totals = Array(12).fill(0)

    verificationCalendar.value.forEach(row => {
      row.monthCounts.forEach((count, index) => {
        totals[index] += count
      })
    })

    return totals
  })

  /**
   * Статистика: общее количество проведенных поверок в текущем году
   * (оборудование с типом верификации 'verification' и датой поверки в текущем году)
   */
  const totalVerifications = computed(() => {
    return equipmentData.value.filter(item => {
      if (!item.verification_date || item.verification_type !== 'verification') {
        return false
      }

      const verDate = new Date(item.verification_date)
      return verDate.getFullYear() === currentYear
    }).length
  })

  /**
   * Статистика: общее количество проведенных калибровок в текущем году
   */
  const totalCalibrations = computed(() => {
    return equipmentData.value.filter(item => {
      if (!item.verification_date || item.verification_type !== 'calibration') {
        return false
      }

      const verDate = new Date(item.verification_date)
      return verDate.getFullYear() === currentYear
    }).length
  })

  /**
   * Статистика: общее количество проведенных аттестаций в текущем году
   */
  const totalCertifications = computed(() => {
    return equipmentData.value.filter(item => {
      if (!item.verification_date || item.verification_type !== 'certification') {
        return false
      }

      const verDate = new Date(item.verification_date)
      return verDate.getFullYear() === currentYear
    }).length
  })

  /**
   * Статистика: всего работ по верификации (сумма всех типов)
   */
  const totalWorks = computed(() => {
    return totalVerifications.value + totalCalibrations.value + totalCertifications.value
  })

  return {
    verificationCalendar,
    monthlyTotals,
    monthNames,
    currentYear,
    // Статистические показатели
    totalVerifications,
    totalCalibrations,
    totalCertifications,
    totalWorks
  }
}
