import { contextBridge, ipcRenderer } from 'electron'

console.log('Preload script загружен')

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
    console.log('openFile вызван из renderer process:', filename)
    const result = await ipcRenderer.invoke('open-file', arrayBuffer, filename)
    console.log('openFile результат:', result)
    return result
  }
})

console.log('window.electron экспортирован в renderer process')
