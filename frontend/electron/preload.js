import { contextBridge, ipcRenderer } from 'electron'

// Экспозиция безопасных API в renderer process
contextBridge.exposeInMainWorld('electron', {
  platform: process.platform,
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron
  },
  // API для работы с файлами
  openFile: async (arrayBuffer, filename) => {
    return await ipcRenderer.invoke('open-file', arrayBuffer, filename)
  },
  // API для undo/redo функциональности
  onUndo: (callback) => {
    ipcRenderer.on('undo-action', callback)
  },
  removeUndoListener: () => {
    ipcRenderer.removeAllListeners('undo-action')
  },
  // API для работы с конфигурацией
  getConfig: async () => {
    return await ipcRenderer.invoke('get-config')
  },
  saveConfig: async (config) => {
    return await ipcRenderer.invoke('save-config', config)
  }
})
