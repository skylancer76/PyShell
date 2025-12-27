/// <reference types="vite/client" />
import React, { useState, useRef, useEffect } from 'react';
import './App.css';

interface TerminalLine {
  id: string;
  type: 'command' | 'output' | 'error';
  content: string;
}

interface SystemStats {
  cpu: number;
  memory: number;
  networkUp: number;
  networkDown: number;
}

// Get API base URL from environment variable
// In production, this should be set in Vercel environment variables
const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '');

const App: React.FC = () => {
  const [lines, setLines] = useState<TerminalLine[]>([
    {
      id: '1',
      type: 'output',
      content: 'Welcome to PyShell Terminal v1.0'
    },
    {
      id: '2',
      type: 'output',
      content: 'Type "help" to see available commands.'
    },
    {
      id: '3',
      type: 'output',
      content: `Backend URL: ${API_BASE}`
    }
  ]);

  const [currentInput, setCurrentInput] = useState('');
  const [isAutocompleting, setIsAutocompleting] = useState(false);
  const [typedLength, setTypedLength] = useState(0);
  const [currentDirectory, setCurrentDirectory] = useState('~');
  const [stats, setStats] = useState<SystemStats>({
    cpu: 17,
    memory: 25,
    networkUp: 1.8,
    networkDown: 0.1
  });
  const [hint, setHint] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const lineIdCounter = useRef(4);

  // Helper function to measure text width
  const getTextWidth = (text: string, font: string) => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    if (context) {
      context.font = font;
      return context.measureText(text).width;
    }
    return 0;
  };

  const addLine = (content: string, type: TerminalLine['type'] = 'output') => {
    const newLine: TerminalLine = {
      id: (lineIdCounter.current++).toString(),
      type,
      content
    };
    setLines(prev => [...prev, newLine]);
  };

  const executeCommand = async (input: string) => {
    if (!input.trim()) return;

    if (!API_BASE) {
      addLine(`Error: Backend URL not configured. Please set VITE_API_URL environment variable.`, 'error');
      return;
    }

    addLine(`${currentDirectory} > ${input}`, 'command');

    try {
      console.log('Attempting to connect to:', `${API_BASE}/execute`);
      const response = await fetch(`${API_BASE}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: input.trim() }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.output === '<CLEAR_SCREEN>') {
          setLines([]);
        } else {
          addLine(data.output);
          if (input.trim().startsWith('cd')) {
            const pwdResponse = await fetch(`${API_BASE}/execute`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ command: 'pwd' }),
            });
            if (pwdResponse.ok) {
              const pwdData = await pwdResponse.json();
              setCurrentDirectory(pwdData.output);
            }
          }
        }
      } else {
        addLine(`Error: Backend server returned status ${response.status}. Check your backend URL: ${API_BASE}`, 'error');
      }
    } catch (error: any) {
      console.error('Command execution error:', error);
      addLine(`Error: ${error.message}. Check your backend URL: ${API_BASE}`, 'error');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      executeCommand(currentInput);
      setCurrentInput('');
      setIsAutocompleting(false);
      setTypedLength(0);
      setHint(null);
      return;
    }

    if (e.key === 'Tab' || e.key === 'ArrowRight') {
      const el = inputRef.current;
      if (el && hint) {
        e.preventDefault();
        setCurrentInput(hint);
        setHint(null);
        setIsAutocompleting(false);
      }
      return;
    }
  };

  const handleChange = async (value: string) => {
    setIsAutocompleting(false);
    setCurrentInput(value);

    const hasSpace = value.includes(' ');
    if (!value || hasSpace) {
      setHint(null);
      return;
    }

    const prefix = value;
    setTypedLength(prefix.length);
    try {
      const res = await fetch(`${API_BASE}/autocomplete?prefix=${encodeURIComponent(prefix)}`);
      if (!res.ok) return;
      const data = await res.json();
      const first: string | undefined = data.suggestions && data.suggestions[0];
      if (first && first.toLowerCase().startsWith(prefix.toLowerCase()) && first.length > prefix.length) {
        setHint(first);
        setIsAutocompleting(true);
      } else {
        setHint(null);
      }
    } catch (_e) { }
  };

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE}/stats`);
        if (response.ok) {
          const data = await response.json();
          setStats({
            cpu: data.cpu,
            memory: data.mem,
            networkUp: data.net_up / (1024 * 1024),
            networkDown: data.net_down / (1024 * 1024)
          });
        }
      } catch (error) {
        setStats(prev => ({
          cpu: Math.max(5, Math.min(95, prev.cpu + (Math.random() - 0.5) * 8)),
          memory: Math.max(20, Math.min(80, prev.memory + (Math.random() - 0.5) * 3)),
          networkUp: Math.max(0.1, prev.networkUp + (Math.random() - 0.5) * 1.5),
          networkDown: Math.max(0.1, prev.networkDown + (Math.random() - 0.5) * 1.5)
        }));
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [lines]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }

    const testConnection = async () => {
      if (!API_BASE) {
        addLine(`⚠️ Backend URL not configured. Please set VITE_API_URL environment variable.`, 'error');
        addLine(`💡 In Vercel: Go to Settings → Environment Variables and add VITE_API_URL`, 'output');
        return;
      }

      try {
        console.log('Testing connection to:', `${API_BASE}/test`);
        const response = await fetch(`${API_BASE}/test`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);

        if (response.ok) {
          const data = await response.json();
          addLine(`✅ Backend connected: ${data.message}`, 'output');
        } else {
          addLine(`❌ Backend connection failed: Status ${response.status} - ${response.statusText}`, 'error');
        }
      } catch (error: any) {
        console.error('Connection test error:', error);
        addLine(`❌ Backend connection failed: ${error.message}`, 'error');
        addLine(`🔗 Trying to connect to: ${API_BASE}`, 'output');
        addLine(`💡 Make sure the backend URL is correct and the backend is deployed.`, 'output');
      }
    };

    testConnection();
  }, []);

  // Calculate the offset for the ghost suggestion
  const getGhostOffset = () => {
    if (!inputRef.current || !currentInput) return 0;

    const font = window.getComputedStyle(inputRef.current).font;
    return getTextWidth(currentInput, font);
  };

  return (
    <div className="terminal-window">
      <div className="terminal-header">
        <div className="window-controls">
          <button className="control-btn close"></button>
          <button className="control-btn minimize"></button>
          <button className="control-btn maximize"></button>
        </div>
        <div className="terminal-title">pyshell</div>
      </div>

      <div className="terminal-content" ref={contentRef}>
        {lines.map((line) => (
          <div key={line.id} className={`terminal-line ${line.type}`}>
            {line.content}
          </div>
        ))}

        <div className="terminal-input-area">
          <span className="prompt">{currentDirectory}</span>
          <span className="prompt-arrow">{'>'}</span>
          <div style={{ position: 'relative', flex: 1 }}>
            <input
              ref={inputRef}
              type="text"
              className="terminal-input"
              value={currentInput}
              onChange={(e) => handleChange(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Enter command..."
              autoComplete="off"
              spellCheck="false"
            />
            {hint && (
              <span
                className="ghost-suggestion"
                style={{
                  left: `${getGhostOffset()}px`
                }}
              >
                {hint.slice(currentInput.length)}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="terminal-status">
        <div className="status-item">
          <svg className="status-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z" />
          </svg>
          <span className="status-value">{stats.memory.toFixed(0)}%</span>
        </div>

        <div className="status-item">
          <svg className="status-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
          </svg>
          <span className="status-value">{stats.cpu.toFixed(0)}%</span>
        </div>

        <div className="status-item">
          <svg className="status-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </div>

        <div className="status-item">
          <svg className="status-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 7h-8v6h8V7zm-2 4h-4V9h4v2zm4.5-9H2.5C1.67 2 1 2.67 1 3.5v17C1 21.33 1.67 22 2.5 22h19c.83 0 1.5-.67 1.5-1.5v-17C23 2.67 22.33 2 21.5 2zM21 20H3V4h18v16z" />
          </svg>
          <span className="status-value">{stats.networkDown.toFixed(1)} kB ↓</span>
        </div>

        <div className="status-item">
          <svg className="status-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 7h-8v6h8V7zm-2 4h-4V9h4v2zm4.5-9H2.5C1.67 2 1 2.67 1 3.5v17C1 21.33 1.67 22 2.5 22h19c.83 0 1.5-.67 1.5-1.5v-17C23 2.67 22.33 2 21.5 2zM21 20H3V4h18v16z" />
          </svg>
          <span className="status-value">{stats.networkUp.toFixed(1)} kB ↑</span>
        </div>
      </div>
    </div>
  );
};

export default App;