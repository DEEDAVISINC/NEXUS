const { app, BrowserWindow, ipcMain, shell, session } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

/** Shared session for PRISM partner portals (Uber Health, Quest, etc.) */
const PARTNER_PARTITION = 'persist:partner';

/** Standard Chrome UA — many portals (incl. Uber OAuth) block or break on default Electron UA */
const CHROME_USER_AGENT =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';

let mainWindow;
const oauthWindows = new Set();

function configurePartnerSession() {
  const partnerSession = session.fromPartition(PARTNER_PARTITION);
  partnerSession.setUserAgent(CHROME_USER_AGENT);

  // Allow geolocation / notifications if portal asks (Uber dispatch maps, etc.)
  partnerSession.setPermissionRequestHandler((_webContents, _permission, callback) => {
    callback(true);
  });

  // OAuth flows (auth.uber.com, login.uber.com) rely on third-party cookies in some builds
  if (typeof partnerSession.setCookie === 'function') {
    try {
      partnerSession.cookies.flushStore?.();
    } catch {
      /* optional */
    }
  }
}

function openPartnerOAuthWindow(url, parentWindow) {
  const win = new BrowserWindow({
    width: 520,
    height: 720,
    parent: parentWindow || mainWindow,
    modal: !!parentWindow,
    title: 'Partner sign-in',
    backgroundColor: '#111827',
    webPreferences: {
      partition: PARTNER_PARTITION,
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
    },
  });

  win.webContents.setUserAgent(CHROME_USER_AGENT);
  oauthWindows.add(win);
  win.on('closed', () => oauthWindows.delete(win));
  win.loadURL(url);
  return win;
}

function attachWebviewHandlers(contents) {
  if (contents.getType() !== 'webview') return;

  contents.setUserAgent(CHROME_USER_AGENT);

  // Uber / SSO login often opens auth.uber.com in a popup — route to modal window, same cookie jar
  contents.setWindowOpenHandler(({ url }) => {
    if (url && /^https?:/i.test(url)) {
      openPartnerOAuthWindow(url, mainWindow);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });

  contents.on('did-fail-load', (_event, errorCode, errorDescription, validatedURL) => {
    console.error('[NEXUS partner-webview] did-fail-load', {
      errorCode,
      errorDescription,
      validatedURL,
    });
  });

  contents.on('console-message', (_event, level, message, line, sourceId) => {
    if (isDev && level >= 2) {
      console.warn('[partner-webview console]', message, sourceId, line);
    }
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    title: 'NEXUS Command Center',
    icon: path.join(__dirname, 'favicon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webviewTag: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#111827',
  });

  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  mainWindow.loadURL(startUrl);

  if (isDev) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

  // Main app only — do NOT intercept webview guest popups (handled in attachWebviewHandlers)
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http') && !url.includes('localhost')) {
      shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('web-contents-created', (_event, contents) => {
  attachWebviewHandlers(contents);
});

app.whenReady().then(() => {
  configurePartnerSession();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

ipcMain.handle('open-partner-portal', async (_event, url) => {
  console.log('Opening partner portal:', url);
  return { success: true };
});

/** Fallback: open portal URL in system browser (same session cannot be shared) */
ipcMain.handle('open-partner-external', async (_event, url) => {
  if (url && /^https?:/i.test(url)) {
    await shell.openExternal(url);
    return { success: true };
  }
  return { success: false };
});
