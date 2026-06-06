const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openPartnerPortal: (url) => ipcRenderer.invoke('open-partner-portal', url),
  openPartnerExternal: (url) => ipcRenderer.invoke('open-partner-external', url),
  platform: process.platform,
  isElectron: true,
});
