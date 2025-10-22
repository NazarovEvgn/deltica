// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  // Main table
  mainTable: `${API_BASE_URL}/main-table`,
  mainTableFull: (id) => `${API_BASE_URL}/main-table/${id}/full`,

  // Files
  files: (equipmentId) => `${API_BASE_URL}/files/equipment/${equipmentId}`,
  fileUpload: (equipmentId) => `${API_BASE_URL}/files/upload/${equipmentId}`,
  fileView: (fileId) => `${API_BASE_URL}/files/view/${fileId}`,
  fileDownload: (fileId) => `${API_BASE_URL}/files/download/${fileId}`,
  fileDelete: (fileId) => `${API_BASE_URL}/files/${fileId}`,

  // Archive
  archive: `${API_BASE_URL}/archive`,
  archiveRestore: (id) => `${API_BASE_URL}/archive/restore/${id}`,
  archiveDelete: (id) => `${API_BASE_URL}/archive/${id}`,
  archiveEquipment: (id) => `${API_BASE_URL}/archive/equipment/${id}`,

  // Pinned documents
  pinnedDocuments: `${API_BASE_URL}/pinned-documents`,
  pinnedDocumentUpload: `${API_BASE_URL}/pinned-documents/upload`,
  pinnedDocumentView: (id) => `${API_BASE_URL}/pinned-documents/view/${id}`,
  pinnedDocumentDownload: (id) => `${API_BASE_URL}/pinned-documents/download/${id}`,
  pinnedDocumentDelete: (id) => `${API_BASE_URL}/pinned-documents/${id}`,

  // Contracts
  contracts: `${API_BASE_URL}/contracts`,
  contractById: (id) => `${API_BASE_URL}/contracts/${id}`,

  // Backup
  backupHistory: (limit = 20) => `${API_BASE_URL}/backup/history?limit=${limit}`,
  backupCreate: `${API_BASE_URL}/backup/create`,

  // Health & Monitoring
  healthSystem: `${API_BASE_URL}/health/system`,
  healthLogs: (limit = 100) => `${API_BASE_URL}/health/logs?limit=${limit}`,

  // Auth
  auth: `${API_BASE_URL}/auth`,
  login: `${API_BASE_URL}/auth/login`,
  me: `${API_BASE_URL}/auth/me`
}
