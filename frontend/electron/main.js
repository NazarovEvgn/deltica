import { app, BrowserWindow, ipcMain, shell, Menu } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'
import os from 'os'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

let mainWindow
let splashWindow

// Создание окна загрузки (splash screen)
function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 500,
    height: 300,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: false
    }
  })

  // Читаем логотип и конвертируем в base64
  const logoPath = path.join(__dirname, '../public/favicon.png')
  let logoBase64 = ''
  try {
    const logoBuffer = fs.readFileSync(logoPath)
    logoBase64 = `data:image/png;base64,${logoBuffer.toString('base64')}`
  } catch (error) {
    console.error('Error loading logo:', error)
  }

  // HTML для splash screen с лого и названием (в стиле приложения)
  const splashHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {
          margin: 0;
          padding: 0;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          background-color: #ececec;
          font-family: 'PT Astra Sans', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .splash-container {
          text-align: center;
          background: white;
          padding: 60px 80px;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .logo-wrapper {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          margin-bottom: 40px;
        }
        .logo {
          width: 48px;
          height: 48px;
        }
        .title {
          font-size: 32px;
          font-weight: 900;
          color: #333333;
          letter-spacing: 0.5px;
        }
        .subtitle {
          font-size: 14px;
          color: #666666;
          margin-bottom: 40px;
        }
        .loader {
          width: 40px;
          height: 40px;
          border: 3px solid #e0e0e0;
          border-top-color: #0071BC;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      </style>
    </head>
    <body>
      <div class="splash-container">
        <div class="logo-wrapper">
          <img src="${logoBase64}" class="logo" alt="Deltica" />
          <div class="title">Deltica</div>
        </div>
        <div class="subtitle">Управление метрологическим оборудованием</div>
        <div class="loader"></div>
      </div>
    </body>
    </html>
  `

  splashWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(splashHTML)}`)
}

// Создание меню приложения
function createMenu() {
  const template = [
    {
      label: 'Файл',
      submenu: [
        {
          label: 'Перезагрузить',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            if (mainWindow) mainWindow.reload()
          }
        },
        { type: 'separator' },
        {
          label: 'Выход',
          accelerator: 'Alt+F4',
          click: () => {
            app.quit()
          }
        }
      ]
    },
    {
      label: 'Правка',
      submenu: [
        {
          label: 'Отменить',
          accelerator: 'CmdOrCtrl+Z',
          click: () => {
            // Отправляем событие в renderer process для отмены редактирования
            if (mainWindow) {
              mainWindow.webContents.send('undo-action')
            }
          }
        },
        {
          label: 'Повторить',
          accelerator: 'CmdOrCtrl+Y',
          role: 'redo'
        },
        { type: 'separator' },
        {
          label: 'Вырезать',
          accelerator: 'CmdOrCtrl+X',
          role: 'cut'
        },
        {
          label: 'Копировать',
          accelerator: 'CmdOrCtrl+C',
          role: 'copy'
        },
        {
          label: 'Вставить',
          accelerator: 'CmdOrCtrl+V',
          role: 'paste'
        },
        { type: 'separator' },
        {
          label: 'Выбрать всё',
          accelerator: 'CmdOrCtrl+A',
          role: 'selectAll'
        }
      ]
    },
    {
      label: 'Вид',
      submenu: [
        {
          label: 'Увеличить масштаб',
          accelerator: 'CmdOrCtrl+Plus',
          role: 'zoomIn'
        },
        {
          label: 'Уменьшить масштаб',
          accelerator: 'CmdOrCtrl+-',
          role: 'zoomOut'
        },
        {
          label: 'Сбросить масштаб',
          accelerator: 'CmdOrCtrl+0',
          role: 'resetZoom'
        },
        { type: 'separator' },
        {
          label: 'Полноэкранный режим',
          accelerator: 'F11',
          role: 'togglefullscreen'
        },
        { type: 'separator' },
        {
          label: 'Инструменты разработчика',
          accelerator: 'F12',
          click: () => {
            if (mainWindow) mainWindow.webContents.toggleDevTools()
          }
        }
      ]
    },
    {
      label: 'Окно',
      submenu: [
        {
          label: 'Свернуть',
          accelerator: 'CmdOrCtrl+M',
          role: 'minimize'
        },
        {
          label: 'Закрыть',
          accelerator: 'CmdOrCtrl+W',
          role: 'close'
        }
      ]
    },
    {
      label: 'Справка',
      submenu: [
        {
          label: 'О программе',
          click: () => {
            const { dialog } = require('electron')
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'О программе Deltica',
              message: 'Deltica v1.0.0',
              detail: 'Управление метрологическим оборудованием\n\nРазработчик: NazarovEvgn\nGitHub: https://github.com/NazarovEvgn/deltica',
              buttons: ['OK']
            })
          }
        }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    show: false,  // Не показываем сразу, показываем после загрузки
    title: 'Deltica - Управление метрологическим оборудованием',
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
    // DevTools можно открыть через F12 или меню "Вид" -> "Инструменты разработчика"
  } else {
    // В production загружаем собранные файлы
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // Когда главное окно готово, показываем его и закрываем splash screen
  mainWindow.once('ready-to-show', () => {
    // Закрываем splash и показываем главное окно сразу
    if (splashWindow) {
      splashWindow.close()
      splashWindow = null
    }
    mainWindow.show()
  })

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
  createMenu()
  createSplashWindow()  // Сначала показываем splash screen
  createWindow()        // Потом создаем главное окно (скрытое)

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
