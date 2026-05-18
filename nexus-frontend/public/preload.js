const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // For communicating with main process
  openPartnerPortal: (url) => ipcRenderer.invoke('open-partner-portal', url),
  
  // Platform info
  platform: process.platform,
  isElectron: true,
});
