import { app, BrowserWindow, ipcMain, shell } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'
import os from 'os'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,  // Отключаем sandbox для работы с файловой системой через IPC
      webSecurity: false  // Отключаем CORS для localhost API
    },
    icon: path.join(__dirname, '../public/favicon.png')
  })

  // В режиме разработки загружаем из Vite dev server
  if (process.env.NODE_ENV === 'development') {
    // Очистка кэша в dev режиме для предотвращения проблем с RevoGrid
    mainWindow.webContents.session.clearCache()

    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    // В production загружаем собранные файлы
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// IPC обработчик для открытия файлов
ipcMain.handle('open-file', async (event, arrayBuffer, filename) => {
  try {
    // Создаем временную папку для документов
    const tempDir = path.join(os.tmpdir(), 'deltica-docs')
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true })
    }

    // Путь к временному файлу
    const filePath = path.join(tempDir, filename)

    // Сохраняем файл
    const buffer = Buffer.from(arrayBuffer)
    fs.writeFileSync(filePath, buffer)

    // Открываем файл в дефолтном приложении (Word для .docx)
    await shell.openPath(filePath)

    return { success: true, path: filePath }
  } catch (error) {
    console.error('Error opening file:', error)
    return { success: false, error: error.message }
  }
})

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
