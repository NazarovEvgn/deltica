// API Configuration
// В Electron режиме используем сохраненный URL из конфига
// В веб режиме используем environment variable или дефолт
let API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Функция для получения актуального API URL (для Electron)
export async function getApiBaseUrl() {
  // Если это Electron и есть сохраненная конфигурация
  if (window.electron) {
    try {
      const config = await window.electron.getConfig()
      if (config && config.serverUrl) {
        return config.serverUrl
      }
    } catch (error) {
      console.error('Ошибка загрузки конфигурации:', error)
    }
  }
  return API_BASE_URL
}

// Функция для обновления базового URL (вызывается после сохранения конфига)
export function updateApiBaseUrl(newUrl) {
  API_BASE_URL = newUrl
  // Пересоздаем endpoints с новым URL
  Object.assign(API_ENDPOINTS, createEndpoints(newUrl))
}

// Вспомогательная функция для создания endpoints
function createEndpoints(baseUrl) {
  return {
    // Main table
    mainTable: `${baseUrl}/main-table`,
    mainTableFull: (id) => `${baseUrl}/main-table/${id}/full`,

    // Files
    files: (equipmentId) => `${baseUrl}/files/equipment/${equipmentId}`,
    fileUpload: (equipmentId) => `${baseUrl}/files/upload/${equipmentId}`,
    fileView: (fileId) => `${baseUrl}/files/view/${fileId}`,
    fileDownload: (fileId) => `${baseUrl}/files/download/${fileId}`,
    fileDelete: (fileId) => `${baseUrl}/files/${fileId}`,

    // Archive
    archive: `${baseUrl}/archive`,
    archiveRestore: (id) => `${baseUrl}/archive/restore/${id}`,
    archiveDelete: (id) => `${baseUrl}/archive/${id}`,
    archiveEquipment: (id) => `${baseUrl}/archive/equipment/${id}`,

    // Pinned documents
    pinnedDocuments: `${baseUrl}/pinned-documents`,
    pinnedDocumentUpload: `${baseUrl}/pinned-documents/upload`,
    pinnedDocumentView: (id) => `${baseUrl}/pinned-documents/view/${id}`,
    pinnedDocumentDownload: (id) => `${baseUrl}/pinned-documents/download/${id}`,
    pinnedDocumentDelete: (id) => `${baseUrl}/pinned-documents/${id}`,

    // Contracts
    contracts: `${baseUrl}/contracts`,
    contractById: (id) => `${baseUrl}/contracts/${id}`,

    // Backup
    backupHistory: (limit = 20) => `${baseUrl}/backup/history?limit=${limit}`,
    backupCreate: `${baseUrl}/backup/create`,

    // Health & Monitoring
    healthSystem: `${baseUrl}/health/system`,
    healthLogs: (limit = 100) => `${baseUrl}/health/logs?limit=${limit}`,

    // Auth
    auth: `${baseUrl}/auth`,
    login: `${baseUrl}/auth/login`,
    me: `${baseUrl}/auth/me`
  }
}

// Экспортируем endpoints
export const API_ENDPOINTS = createEndpoints(API_BASE_URL)

// Синхронный экспорт для обратной совместимости
export { API_BASE_URL }
