import React, { useRef, useEffect, useState } from 'react';

interface PartnerWebviewProps {
  url: string;
  name: string;
  icon: string;
  onClose: () => void;
  color: string;
}

// Electron webview methods type (not in standard DOM types)
interface ElectronWebview extends HTMLElement {
  canGoBack: () => boolean;
  canGoForward: () => boolean;
  goBack: () => void;
  goForward: () => void;
  reload: () => void;
  loadURL: (url: string) => void;
  src: string;
}

// Check if we're running in Electron
const isElectron = () => {
  return typeof window !== 'undefined' && 
         (window as any).electronAPI?.isElectron === true;
};

const PartnerWebview: React.FC<PartnerWebviewProps> = ({ url, name, icon, onClose, color }) => {
  const webviewRef = useRef<ElectronWebview>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentUrl, setCurrentUrl] = useState(url);
  const [canGoBack, setCanGoBack] = useState(false);
  const [canGoForward, setCanGoForward] = useState(false);

  useEffect(() => {
    const webview = webviewRef.current;
    if (!webview) return;

    const handleLoadStart = () => setIsLoading(true);
    const handleLoadStop = () => {
      setIsLoading(false);
      if (webview.canGoBack) setCanGoBack(webview.canGoBack());
      if (webview.canGoForward) setCanGoForward(webview.canGoForward());
    };
    const handleNavigate = (e: any) => {
      setCurrentUrl(e.url);
    };

    webview.addEventListener('did-start-loading', handleLoadStart);
    webview.addEventListener('did-stop-loading', handleLoadStop);
    webview.addEventListener('did-navigate', handleNavigate);
    webview.addEventListener('did-navigate-in-page', handleNavigate);

    return () => {
      webview.removeEventListener('did-start-loading', handleLoadStart);
      webview.removeEventListener('did-stop-loading', handleLoadStop);
      webview.removeEventListener('did-navigate', handleNavigate);
      webview.removeEventListener('did-navigate-in-page', handleNavigate);
    };
  }, []);

  const goBack = () => webviewRef.current?.goBack?.();
  const goForward = () => webviewRef.current?.goForward?.();
  const reload = () => webviewRef.current?.reload?.();
  const goHome = () => webviewRef.current?.loadURL?.(url);

  // Fallback for non-Electron (web browser)
  if (!isElectron()) {
    return (
      <div className="flex flex-col h-full bg-gray-900">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700" style={{ backgroundColor: color + '20' }}>
          <div className="flex items-center gap-3">
            <span className="text-xl">{icon}</span>
            <div>
              <h3 className="font-bold text-white text-sm">{name}</h3>
              <p className="text-[11px] text-gray-400 truncate max-w-md">{url}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <a 
              href={url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition hover:opacity-90"
              style={{ backgroundColor: color }}
            >
              Open {name} ↗
            </a>
            <button 
              onClick={onClose}
              className="px-3 py-2 rounded-lg text-sm font-semibold bg-gray-700 hover:bg-gray-600 transition"
            >
              ✕
            </button>
          </div>
        </div>
        
        {/* Message for web browser */}
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
          <div className="text-6xl mb-4">🖥️</div>
          <h2 className="text-xl font-bold text-white mb-2">Desktop App Required</h2>
          <p className="text-gray-400 max-w-md mb-6">
            To embed partner portals directly in NEXUS, you need to run the 
            <span className="text-orange-400 font-semibold"> NEXUS Desktop App</span>.
          </p>
          <p className="text-gray-500 text-sm mb-6">
            In the web browser, click the button above to open {name} in a new tab.
          </p>
          <div className="text-left bg-gray-800 rounded-lg p-4 text-sm">
            <p className="text-gray-400 mb-2">To run NEXUS Desktop:</p>
            <code className="text-green-400">npm run electron-dev</code>
          </div>
        </div>
      </div>
    );
  }

  // Electron webview
  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Browser Chrome / Toolbar */}
      <div className="flex items-center gap-2 px-3 py-2 border-b border-gray-700 bg-gray-800">
        {/* Navigation buttons */}
        <div className="flex items-center gap-1">
          <button 
            onClick={goBack} 
            disabled={!canGoBack}
            className={`p-1.5 rounded ${canGoBack ? 'hover:bg-gray-700 text-gray-300' : 'text-gray-600 cursor-not-allowed'}`}
          >
            ←
          </button>
          <button 
            onClick={goForward} 
            disabled={!canGoForward}
            className={`p-1.5 rounded ${canGoForward ? 'hover:bg-gray-700 text-gray-300' : 'text-gray-600 cursor-not-allowed'}`}
          >
            →
          </button>
          <button onClick={reload} className="p-1.5 rounded hover:bg-gray-700 text-gray-300">
            ↻
          </button>
          <button onClick={goHome} className="p-1.5 rounded hover:bg-gray-700 text-gray-300">
            🏠
          </button>
        </div>

        {/* URL Bar */}
        <div className="flex-1 flex items-center gap-2 bg-gray-700 rounded-lg px-3 py-1.5">
          <span className="text-lg">{icon}</span>
          <span className="text-sm text-white font-medium">{name}</span>
          <span className="text-gray-500">|</span>
          <span className="text-xs text-gray-400 truncate flex-1">{currentUrl}</span>
          {isLoading && <span className="text-blue-400 animate-pulse text-xs">Loading...</span>}
        </div>

        {/* Close button */}
        <button 
          onClick={onClose}
          className="px-3 py-1.5 rounded-lg text-sm font-semibold bg-red-500/20 text-red-400 hover:bg-red-500/30 transition"
        >
          ✕ Close
        </button>
      </div>

      {/* Webview */}
      <webview
        ref={webviewRef as any}
        src={url}
        className="flex-1 w-full"
        style={{ height: 'calc(100% - 48px)' }}
        // @ts-ignore - webview attributes
        allowpopups="true"
        partition="persist:partner"
      />
    </div>
  );
};

export default PartnerWebview;
