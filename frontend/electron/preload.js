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
  }
})
