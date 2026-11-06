import React, { useState, useEffect, useRef } from 'react';
import { 
  Shield, Play, Square, Terminal, Plus, Trash2, 
  Settings, Users, MessageSquare, Zap, Sliders, 
  Download, RefreshCw, Hash, Target, CheckCircle2, 
  AlertTriangle, Upload, FileText, Activity, Lock, Unlock,
  Cpu, Server, Radio, Power, Layers
} from 'lucide-react';

export default function App() {
  // --- Navigation Tab State ---
  const [activeTab, setActiveTab] = useState('control_center'); // 'control_center' | 'nodes_matrix'

  // --- Header Stats & Uptime ---
  const [uptimeSeconds, setUptimeSeconds] = useState(3815);

  // --- Node Authorization State ---
  const [sessionIdInput, setSessionIdInput] = useState('');

  // --- Dynamic Target Switcher State ---
  const [targetIdentityInput, setTargetIdentityInput] = useState('');

  // --- Group Name Protection (NC Lock) State ---
  const [ncThreadId, setNcThreadId] = useState('260564389102837');
  const [ncSecuredTitle, setNcSecuredTitle] = useState('SECURE TITLE');
  const [isNcLockActive, setIsNcLockActive] = useState(false);
  const [emojiIndex, setEmojiIndex] = useState(0);

  // Auto-rotating suffix emoji list for NC Lock
  const ncEmojis = ['💕', '🔥', '✨', '👑', '⚡', '😈', '🚀', '💣', '🛡️', '⚡'];

  // --- Sequential Mass GC Creator State ---
  const [massPrefix, setMassPrefix] = useState('Raid');
  const [massTargetUser, setMassTargetUser] = useState('');
  const [massChannelsCount, setMassChannelsCount] = useState(20);

  // --- Campaign / Flood Matrix State ---
  const [isCampaignActive, setIsCampaignActive] = useState(false);
  const [primaryTargetName, setPrimaryTargetName] = useState('AIMGAND-REHAND');
  const [routingStrategy, setRoutingStrategy] = useState('Matrix-Wide (All Group Chats)');
  const [targetGcId, setTargetGcId] = useState('260564389102837');
  const [jitterPacingDelay, setJitterPacingDelay] = useState(3.5);
  const [payloadProfile, setPayloadProfile] = useState('Profile Alpha (Heavy Abuse)');
  const [customOperatorLines, setCustomOperatorLines] = useState('Custom text line 1\nCustom text line 2');

  // --- Synchronized Nodes State ---
  const [nodes, setNodes] = useState([
    {
      id: 1,
      handle: 'yachudnangiho',
      sessionId: '58291048291%3AF9xKls0291...',
      followers: 4,
      dispatched: 305,
      dropped: 0,
      channels: 1,
      target: 'AIMGAND-REHAND',
      status: 'OPERATIONAL',
      isSelected: true,
      isNcSelected: true
    },
    {
      id: 2,
      handle: 'abusive_node_02',
      sessionId: '49201948102%3AKls8301928...',
      followers: 12,
      dispatched: 142,
      dropped: 1,
      channels: 3,
      target: 'AIMGAND-REHAND',
      status: 'OPERATIONAL',
      isSelected: true,
      isNcSelected: true
    }
  ]);

  // --- JSON File Upload State ---
  const [jsonFileName, setJsonFileName] = useState('No file chosen');

  // --- Telemetry & Event Log State ---
  const [logs, setLogs] = useState([
    { id: 1, time: '15:29:35', user: 'yachudnangiho', target: 'AIMGAND-REHAND', gc: '260564389...' },
    { id: 2, time: '15:29:46', user: 'yachudnangiho', target: 'AIMGAND-REHAND', gc: '260564389...' },
    { id: 3, time: '15:29:58', user: 'yachudnangiho', target: 'AIMGAND-REHAND', gc: '260564389...' },
    { id: 4, time: '15:30:10', user: 'yachudnangiho', target: 'AIMGAND-REHAND', gc: '260564389...' },
    { id: 5, time: '15:30:22', user: 'yachudnangiho', target: 'AIMGAND-REHAND', gc: '260564389...' }
  ]);

  const logContainerRef = useRef(null);

  // --- Helper: Format IST Time (HH:MM:SS) ---
  function getIstTime() {
    const options = { timeZone: 'Asia/Kolkata', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
    return new Date().toLocaleTimeString('en-US', options);
  }

  // --- Helper: Format Uptime (Xh Ym Zs) ---
  function formatUptime(totalSecs) {
    const hrs = Math.floor(totalSecs / 3600);
    const mins = Math.floor((totalSecs % 3600) / 60);
    const secs = totalSecs % 60;
    return `${hrs}h ${mins}m ${secs}s`;
  }

  // Uptime timer
  useEffect(() => {
    const timer = setInterval(() => {
      setUptimeSeconds(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Auto-scroll logs
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  // --- Calculate Single Jitter Pacing Delay ---
  const calculateJitter = (baseSec) => {
    const base = parseFloat(baseSec) || 3.5;
    const variation = (Math.random() * 0.4 - 0.2) * base; // ±20% micro jitter
    return Math.max(0.5, base + variation).toFixed(2);
  };

  // --- Background Campaign Dispatcher Loop ---
  useEffect(() => {
    let campaignInterval = null;
    if (isCampaignActive) {
      const activeNodes = nodes.filter(n => n.isSelected);
      if (activeNodes.length === 0) return;

      const pacingMs = Math.max(1000, (parseFloat(jitterPacingDelay) || 3.5) * 1000);

      campaignInterval = setInterval(() => {
        const randomNode = activeNodes[Math.floor(Math.random() * activeNodes.length)];
        const effectiveJitter = calculateJitter(jitterPacingDelay);
        const gcDisplay = targetGcId ? (targetGcId.length > 10 ? `${targetGcId.slice(0, 9)}...` : targetGcId) : '260564389...';

        setNodes(prev => prev.map(n => n.id === randomNode.id ? { ...n, dispatched: n.dispatched + 1 } : n));

        setLogs(prev => [
          ...prev.slice(-200),
          {
            id: Date.now() + Math.random(),
            time: getIstTime(),
            user: randomNode.handle,
            target: primaryTargetName || 'TARGET',
            gc: gcDisplay,
            jitter: effectiveJitter
          }
        ]);
      }, pacingMs);
    }

    return () => clearInterval(campaignInterval);
  }, [isCampaignActive, nodes, primaryTargetName, targetGcId, jitterPacingDelay]);

  // --- Background NC Lock Loop (Name Protection with Specific Selected IDs) ---
  useEffect(() => {
    let ncInterval = null;
    if (isNcLockActive) {
      const activeNcNodes = nodes.filter(n => n.isNcSelected);
      if (activeNcNodes.length === 0) return;

      const pacingMs = Math.max(1500, (parseFloat(jitterPacingDelay) || 3.5) * 1000);

      ncInterval = setInterval(() => {
        const nextEmojiIdx = (emojiIndex + 1) % ncEmojis.length;
        setEmojiIndex(nextEmojiIdx);

        const currentEmoji = ncEmojis[nextEmojiIdx];
        const newTitle = `${ncSecuredTitle} ${currentEmoji}`;
        const randomNode = activeNcNodes[Math.floor(Math.random() * activeNcNodes.length)];
        const gcDisplay = ncThreadId ? (ncThreadId.length > 10 ? `${ncThreadId.slice(0, 9)}...` : ncThreadId) : '260564389...';

        setLogs(prev => [
          ...prev.slice(-200),
          {
            id: Date.now() + Math.random(),
            time: getIstTime(),
            user: randomNode.handle,
            target: `NC_LOCK: "${newTitle}"`,
            gc: gcDisplay
          }
        ]);
      }, pacingMs);
    }

    return () => clearInterval(ncInterval);
  }, [isNcLockActive, emojiIndex, ncSecuredTitle, ncThreadId, nodes, jitterPacingDelay]);

  // Node Authorization
  const handleAuthorizeNode = (e) => {
    e.preventDefault();
    if (!sessionIdInput.trim()) return;

    const fakeHandle = `node_${Math.floor(1000 + Math.random() * 9000)}`;
    const newNode = {
      id: Date.now(),
      handle: fakeHandle,
      sessionId: sessionIdInput.trim().slice(0, 25) + '...',
      followers: Math.floor(Math.random() * 50),
      dispatched: 0,
      dropped: 0,
      channels: 1,
      target: primaryTargetName,
      status: 'OPERATIONAL',
      isSelected: true,
      isNcSelected: true
    };

    setNodes([...nodes, newNode]);
    setSessionIdInput('');

    setLogs(prev => [
      ...prev,
      {
        id: Date.now(),
        time: getIstTime(),
        user: fakeHandle,
        target: 'NODE REGISTERED & AUTHORIZED',
        gc: 'SYS_AUTH'
      }
    ]);
  };

  // Dynamic Target Update
  const handleUpdateTarget = (e) => {
    e.preventDefault();
    if (!targetIdentityInput.trim()) return;
    const newTarget = targetIdentityInput.trim();
    setPrimaryTargetName(newTarget);
    setNodes(prev => prev.map(n => ({ ...n, target: newTarget })));

    setLogs(prev => [
      ...prev,
      {
        id: Date.now(),
        time: getIstTime(),
        user: 'SYSTEM',
        target: `DYNAMIC TARGET UPDATED -> ${newTarget}`,
        gc: 'TARGET_SYNC'
      }
    ]);
    setTargetIdentityInput('');
  };

  // NC Lock Actions
  const handleActivateNcLock = () => {
    setIsNcLockActive(true);
    setLogs(prev => [
      ...prev,
      {
        id: Date.now(),
        time: getIstTime(),
        user: 'SYSTEM',
        target: `NC LOCK ACTIVATED -> GC: ${ncThreadId}`,
        gc: 'NC_PROTECT'
      }
    ]);
  };

  const handleTerminateNcLock = () => {
    setIsNcLockActive(false);
    setLogs(prev => [
      ...prev,
      {
        id: Date.now(),
        time: getIstTime(),
        user: 'SYSTEM',
        target: 'NC LOCK TERMINATED',
        gc: 'NC_STOP'
      }
    ]);
  };

  // Campaign Actions
  const handleLaunchCampaign = () => {
    setIsCampaignActive(true);
  };

  const handleHaltCampaign = () => {
    setIsCampaignActive(false);
    setIsNcLockActive(false);
    setLogs(prev => [
      ...prev,
      {
        id: Date.now(),
        time: getIstTime(),
        user: 'SYSTEM',
        target: 'HALT ALL ACTIVE DISPATCHERS TRIGGERED',
        gc: 'EMERGENCY_STOP'
      }
    ]);
  };

  // Toggles for Nodes
  const toggleNodeSelection = (id) => {
    setNodes(prev => prev.map(n => n.id === id ? { ...n, isSelected: !n.isSelected } : n));
  };

  const toggleNcNodeSelection = (id) => {
    setNodes(prev => prev.map(n => n.id === id ? { ...n, isNcSelected: !n.isNcSelected } : n));
  };

  const handleRevokeNode = (id) => {
    const nodeToRevoke = nodes.find(n => n.id === id);
    setNodes(prev => prev.filter(n => n.id !== id));
    if (nodeToRevoke) {
      setLogs(prev => [
        ...prev,
        {
          id: Date.now(),
          time: getIstTime(),
          user: nodeToRevoke.handle,
          target: 'NODE REVOKED & DISCONNECTED',
          gc: 'SYS_REVOKE'
        }
      ]);
    }
  };

  const handleFileUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      setJsonFileName(e.target.files[0].name);
    }
  };

  const handleExportLinks = () => {
    const textContent = logs.map(l => `[${l.time}] [@Abusivegang] [${l.user}] DISPATCHED -> Target: ${l.target} | GC: ${l.gc}`).join('\n');
    const blob = new Blob([textContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'link.txt';
    a.click();
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#e0e0e0] font-sans p-2 sm:p-4 lg:p-6 select-none">
      
      {/* ================= HEADER BAR ================= */}
      <header className="max-w-[1600px] mx-auto mb-4 bg-[#141414] border border-[#2e0b11] rounded-lg p-3 sm:p-5 shadow-[0_0_20px_rgba(255,0,60,0.15)]">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          
          {/* Header Title & Branding */}
          <div className="flex flex-col">
            <h1 className="text-xl sm:text-2xl font-black font-mono text-[#ff003c] tracking-widest uppercase drop-shadow-[0_0_8px_rgba(255,0,60,0.8)]">
              AARYAV PANNEL SPAM IG
            </h1>
            <span className="font-mono text-xs font-bold text-[#b0a8a6] tracking-wider mt-0.5">
              Owner: <span className="text-[#ff003c] font-black">@Abusivegang</span> | Operator: <span className="text-white">S</span>
            </span>
          </div>

          {/* Header Right Actions & Uptime */}
          <div className="flex items-center gap-4">
            <span className="font-mono text-xs sm:text-sm text-[#8a8a8a]">
              Uptime: <strong className="text-white font-mono">{formatUptime(uptimeSeconds)}</strong>
            </span>
            <button
              onClick={handleHaltCampaign}
              className="px-5 py-2 bg-gradient-to-r from-[#800016] to-[#4a000d] hover:from-[#a8001d] hover:to-[#6b0013] text-white text-xs sm:text-sm font-black tracking-wider uppercase rounded border border-[#ff003c]/40 transition-all shadow-[0_0_10px_rgba(128,0,22,0.5)] active:scale-95"
            >
              Terminate Session
            </button>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex items-center gap-2 mt-4 pt-3 border-t border-[#261014]">
          <button
            onClick={() => setActiveTab('control_center')}
            className={`px-6 py-2 rounded text-xs sm:text-sm font-black font-mono tracking-wider transition-all border ${
              activeTab === 'control_center'
                ? 'bg-[#ff003c] text-white border-[#ff4d73] shadow-[0_0_15px_rgba(255,0,60,0.6)]'
                : 'bg-[#1a1a1a] text-[#8a8a8a] border-[#2e2e2e] hover:bg-[#262626] hover:text-white'
            }`}
          >
            Control Center
          </button>
          <button
            onClick={() => setActiveTab('nodes_matrix')}
            className={`px-6 py-2 rounded text-xs sm:text-sm font-black font-mono tracking-wider transition-all border ${
              activeTab === 'nodes_matrix'
                ? 'bg-[#ff003c] text-white border-[#ff4d73] shadow-[0_0_15px_rgba(255,0,60,0.6)]'
                : 'bg-[#1a1a1a] text-[#8a8a8a] border-[#2e2e2e] hover:bg-[#262626] hover:text-white'
            }`}
          >
            Nodes Matrix
          </button>
        </div>
      </header>

      {/* ================= TAB 1: CONTROL CENTER ================= */}
      {activeTab === 'control_center' && (
        <main className="max-w-[1600px] mx-auto space-y-4">
          
          {/* Top 3 Grid Columns */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* PANEL 1: NODE AUTHORIZATION */}
            <div className="bg-[#141414] border border-[#2e0b11] rounded-lg p-4 flex flex-col justify-between shadow-lg hover:border-[#ff003c]/30 transition-all">
              <div>
                <h3 className="text-xs font-black font-mono text-[#ff003c] uppercase tracking-wider mb-3">
                  NODE AUTHORIZATION
                </h3>
                <div className="space-y-2">
                  <label className="text-[11px] text-[#8a8a8a] font-mono block">Session ID Cookie String</label>
                  <input
                    type="text"
                    value={sessionIdInput}
                    onChange={(e) => setSessionIdInput(e.target.value)}
                    placeholder="Paste sessionid cookie..."
                    className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                  />
                </div>
              </div>
              <button
                onClick={handleAuthorizeNode}
                className="mt-4 w-full py-2.5 bg-[#ff003c] hover:bg-[#e60036] text-white font-black text-xs sm:text-sm uppercase tracking-wider rounded border border-[#ff4d73] transition-all shadow-[0_0_10px_rgba(255,0,60,0.4)] active:scale-95"
              >
                Authorize & Register Node
              </button>
            </div>

            {/* PANEL 2: DYNAMIC TARGET SWITCHER */}
            <div className="bg-[#141414] border border-[#2e0b11] rounded-lg p-4 flex flex-col justify-between shadow-lg hover:border-[#ff003c]/30 transition-all">
              <div>
                <h3 className="text-xs font-black font-mono text-[#ff003c] uppercase tracking-wider mb-3">
                  DYNAMIC TARGET SWITCHER
                </h3>
                <div className="space-y-2">
                  <label className="text-[11px] text-[#8a8a8a] font-mono block">New Target Identity / Username</label>
                  <input
                    type="text"
                    value={targetIdentityInput}
                    onChange={(e) => setTargetIdentityInput(e.target.value)}
                    placeholder="Enter target name..."
                    className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                  />
                </div>
              </div>
              <button
                onClick={handleUpdateTarget}
                className="mt-4 w-full py-2.5 bg-[#ff003c] hover:bg-[#e60036] text-white font-black text-xs sm:text-sm uppercase tracking-wider rounded border border-[#ff4d73] transition-all shadow-[0_0_10px_rgba(255,0,60,0.4)] active:scale-95"
              >
                Update Target Instantly
              </button>
            </div>

            {/* PANEL 3: AUTOMA CUSTOM JSON PARSER */}
            <div className="bg-[#141414] border border-[#2e0b11] rounded-lg p-4 flex flex-col justify-between shadow-lg hover:border-[#ff003c]/30 transition-all">
              <div>
                <h3 className="text-xs font-black font-mono text-[#ff003c] uppercase tracking-wider mb-3">
                  AUTOMA CUSTOM JSON PARSER
                </h3>
                <div className="space-y-2">
                  <label className="text-[11px] text-[#8a8a8a] font-mono block">Upload Your Custom JSON File</label>
                  <div className="flex items-center gap-2 bg-[#0a0a0a] border border-[#2e2e2e] rounded p-1">
                    <label className="cursor-pointer bg-[#242424] hover:bg-[#333333] text-xs font-mono text-[#e0e0e0] px-3 py-1 rounded border border-[#3a3a3a]">
                      Choose File
                      <input type="file" accept=".json" onChange={handleFileUpload} className="hidden" />
                    </label>
                    <span className="text-xs font-mono text-[#8a8a8a] truncate">{jsonFileName}</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => {
                  setLogs(prev => [...prev, { id: Date.now(), time: getIstTime(), user: 'SYSTEM', target: 'JSON PAYLOADS EXTRACTED & SAVED', gc: 'AUTOMA_PARSER' }]);
                }}
                className="mt-4 w-full py-2.5 bg-[#ff003c] hover:bg-[#e60036] text-white font-black text-xs sm:text-sm uppercase tracking-wider rounded border border-[#ff4d73] transition-all shadow-[0_0_10px_rgba(255,0,60,0.4)] active:scale-95"
              >
                Save & Extract JSON Payloads
              </button>
            </div>

          </div>

          {/* Middle 3 Grid Columns */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* PANEL 4: GROUP NAME PROTECTION (NC LOCK) WITH NODE SELECTOR */}
            <div className="bg-[#141414] border border-[#2e0b11] rounded-lg p-4 space-y-3 shadow-lg hover:border-[#ff003c]/30 transition-all">
              <h3 className="text-xs font-black font-mono text-[#ff003c] uppercase tracking-wider">
                GROUP NAME PROTECTION (NC LOCK)
              </h3>

              {/* Active Node Selectors for NC Lock */}
              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Active NC Node Selectors (Session IDs)</label>
                <div className="bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 max-h-24 overflow-y-auto space-y-1 custom-scrollbar">
                  {nodes.map(node => (
                    <label key={node.id} className="flex items-center gap-2 cursor-pointer text-xs font-mono text-white">
                      <input
                        type="checkbox"
                        checked={node.isNcSelected || false}
                        onChange={() => toggleNcNodeSelection(node.id)}
                        className="accent-[#ff003c]"
                      />
                      <span>@{node.handle}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Target Group ID / Thread Link</label>
                <input
                  type="text"
                  value={ncThreadId}
                  onChange={(e) => setNcThreadId(e.target.value)}
                  placeholder="Thread ID..."
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Secured Group Title</label>
                <input
                  type="text"
                  value={ncSecuredTitle}
                  onChange={(e) => setNcSecuredTitle(e.target.value)}
                  placeholder="SECURE TITLE"
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                />
              </div>

              <div className="pt-2 space-y-2">
                <button
                  onClick={handleActivateNcLock}
                  disabled={isNcLockActive}
                  className={`w-full py-2 bg-[#ff003c] hover:bg-[#e60036] text-white font-black text-xs uppercase tracking-wider rounded border border-[#ff4d73] transition-all shadow-[0_0_10px_rgba(255,0,60,0.4)] ${isNcLockActive ? 'opacity-50 cursor-not-allowed' : 'active:scale-95'}`}
                >
                  {isNcLockActive ? `NC Lock Active (${ncEmojis[emojiIndex]})` : 'Activate NC Lock'}
                </button>
                <button
                  onClick={handleTerminateNcLock}
                  disabled={!isNcLockActive}
                  className={`w-full py-2 bg-[#800016] hover:bg-[#a8001d] text-white font-black text-xs uppercase tracking-wider rounded border border-[#ff003c]/40 transition-all shadow-md ${!isNcLockActive ? 'opacity-50 cursor-not-allowed' : 'active:scale-95'}`}
                >
                  Terminate NC Lock
                </button>
              </div>
            </div>

            {/* PANEL 5: SEQUENTIAL MASS GC CREATOR */}
            <div className="bg-[#141414] border border-[#2e0b11] rounded-lg p-4 space-y-3 shadow-lg hover:border-[#ff003c]/30 transition-all">
              <h3 className="text-xs font-black font-mono text-[#ff003c] uppercase tracking-wider">
                SEQUENTIAL MASS GC CREATOR
              </h3>

              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Deployment Prefix</label>
                <input
                  type="text"
                  value={massPrefix}
                  onChange={(e) => setMassPrefix(e.target.value)}
                  placeholder="Raid"
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Target Account Username</label>
                <input
                  type="text"
                  value={massTargetUser}
                  onChange={(e) => setMassTargetUser(e.target.value)}
                  placeholder="username (no @)"
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Total Channels Count</label>
                <input
                  type="number"
                  value={massChannelsCount}
                  onChange={(e) => setMassChannelsCount(Number(e.target.value))}
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                />
              </div>

              <button
                onClick={() => {
                  setLogs(prev => [...prev, { id: Date.now(), time: getIstTime(), user: 'SYSTEM', target: `MASS CHANNELS DEPLOYED (${massChannelsCount})`, gc: 'MASS_CREATOR' }]);
                }}
                className="w-full py-2 bg-[#ff003c] hover:bg-[#e60036] text-white font-black text-xs uppercase tracking-wider rounded border border-[#ff4d73] transition-all shadow-[0_0_10px_rgba(255,0,60,0.4)] active:scale-95"
              >
                Deploy Mass Channels
              </button>
            </div>

            {/* PANEL 6: MULTI-NODE ROUTER & FLOOD MATRIX */}
            <div className="bg-[#141414] border border-[#2e0b11] rounded-lg p-4 space-y-3 shadow-lg hover:border-[#ff003c]/30 transition-all">
              <h3 className="text-xs font-black font-mono text-[#ff003c] uppercase tracking-wider">
                MULTI-NODE ROUTER & FLOOD MATRIX
              </h3>

              {/* Active Node Selectors */}
              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Active Node Selectors</label>
                <div className="bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 max-h-24 overflow-y-auto space-y-1 custom-scrollbar">
                  {nodes.map(node => (
                    <label key={node.id} className="flex items-center gap-2 cursor-pointer text-xs font-mono text-white">
                      <input
                        type="checkbox"
                        checked={node.isSelected}
                        onChange={() => toggleNodeSelection(node.id)}
                        className="accent-[#ff003c]"
                      />
                      <span>@{node.handle}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Primary Target Name */}
              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Primary Target Name</label>
                <input
                  type="text"
                  value={primaryTargetName}
                  onChange={(e) => setPrimaryTargetName(e.target.value)}
                  placeholder="Target Name"
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                />
              </div>

              {/* Routing Strategy */}
              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Routing Strategy</label>
                <select
                  value={routingStrategy}
                  onChange={(e) => setRoutingStrategy(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                >
                  <option value="Matrix-Wide (All Group Chats)">Matrix-Wide (All Group Chats)</option>
                  <option value="Isolated Group Only">Isolated Group Only</option>
                  <option value="Sequential Rotation">Sequential Rotation</option>
                </select>
              </div>

              {/* Target GC ID */}
              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Target GC ID (If Isolated Selected)</label>
                <input
                  type="text"
                  value={targetGcId}
                  onChange={(e) => setTargetGcId(e.target.value)}
                  placeholder="Thread ID..."
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                />
              </div>

              {/* Single Jitter Pacing Delay */}
              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Jitter Pacing Delay (Seconds)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0.5"
                  value={jitterPacingDelay}
                  onChange={(e) => setJitterPacingDelay(parseFloat(e.target.value) || 3.5)}
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                />
              </div>

              {/* Payload Profile Matrix */}
              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Payload Profile Matrix</label>
                <select
                  value={payloadProfile}
                  onChange={(e) => setPayloadProfile(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none"
                >
                  <option value="Profile Alpha (Heavy Abuse)">Profile Alpha (Heavy Abuse)</option>
                  <option value="Profile Beta (Moderate Flood)">Profile Beta (Moderate Flood)</option>
                  <option value="Profile Custom Lines">Profile Custom Lines</option>
                </select>
              </div>

              {/* Custom Operator Lines */}
              <div className="space-y-1">
                <label className="text-[11px] text-[#8a8a8a] font-mono block">Custom Operator Lines (Use {'{target}'})</label>
                <textarea
                  rows="3"
                  value={customOperatorLines}
                  onChange={(e) => setCustomOperatorLines(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-[#2e2e2e] rounded p-2 text-xs font-mono text-white focus:border-[#ff003c] focus:outline-none custom-scrollbar"
                />
              </div>

              {/* Action Buttons */}
              <div className="space-y-2 pt-2">
                <button
                  onClick={handleLaunchCampaign}
                  disabled={isCampaignActive}
                  className={`w-full py-2.5 bg-[#ff003c] hover:bg-[#e60036] text-white font-black text-xs sm:text-sm uppercase tracking-wider rounded border border-[#ff4d73] transition-all shadow-[0_0_12px_rgba(255,0,60,0.5)] ${isCampaignActive ? 'opacity-50 cursor-not-allowed' : 'active:scale-95'}`}
                >
                  {isCampaignActive ? 'Campaign Dispatching...' : 'Launch Campaign'}
                </button>

                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={handleHaltCampaign}
                    className="py-2 bg-[#800016] hover:bg-[#a8001d] text-white font-black text-xs uppercase tracking-wider rounded border border-[#ff003c]/40 transition-all shadow-md active:scale-95"
                  >
                    Halt All Active
                  </button>
                  <button
                    onClick={handleExportLinks}
                    className="py-2 bg-[#1a1a1a] hover:bg-[#262626] text-white font-black text-xs uppercase tracking-wider rounded border border-[#2e2e2e] transition-all shadow-md active:scale-95"
                  >
                    Export link.txt
                  </button>
                </div>
              </div>
            </div>

          </div>

          {/* PANEL 7: REAL-TIME TELEMETRY & EVENT LOG */}
          <section className="bg-[#141414] border border-[#2e0b11] rounded-lg p-4 shadow-2xl">
            <h3 className="text-xs font-black font-mono text-[#ff003c] uppercase tracking-wider mb-3">
              REAL-TIME TELEMETRY & EVENT LOG (MANAGED BY @ABUSIVEGANG)
            </h3>

            <div
              ref={logContainerRef}
              className="h-64 overflow-y-auto bg-[#050505] border border-[#2e0b11] rounded p-3 font-mono text-xs text-[#a0a0a0] space-y-1.5 custom-scrollbar shadow-inner"
            >
              {logs.map((log) => (
                <div key={log.id} className="leading-relaxed">
                  <span className="text-[#666666]">[{log.time}]</span>{' '}
                  <span className="text-[#ff003c] font-bold">[@Abusivegang]</span>{' '}
                  <span className="text-[#00ffcc]">[{log.user}]</span>{' '}
                  <span className="text-[#ff003c] font-black">DISPATCHED</span>{' '}
                  <span className="text-white">→ Target: <em className="text-[#ff4d73] font-bold">{log.target}</em></span>{' '}
                  <span className="text-[#777777]">| GC: {log.gc}</span>
                </div>
              ))}
            </div>
          </section>

        </main>
      )}

      {/* ================= TAB 2: NODES MATRIX ================= */}
      {activeTab === 'nodes_matrix' && (
        <main className="max-w-[1600px] mx-auto space-y-4">
          <section className="bg-[#141414] border border-[#2e0b11] rounded-lg p-6 shadow-2xl">
            
            <div className="border-b border-[#2e0b11] pb-4 mb-6">
              <h2 className="text-sm font-black font-mono text-[#ff003c] uppercase tracking-wider">
                OPERATOR NODES & CAMPAIGN PERFORMANCE MATRIX (@ABUSIVEGANG INFRASTRUCTURE)
              </h2>
              <p className="text-xs font-mono text-[#8a8a8a] mt-1">
                Active Synchronized Nodes: <strong className="text-white">{nodes.length}</strong>
              </p>
            </div>

            {/* Nodes Grid Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {nodes.map((node) => (
                <div 
                  key={node.id} 
                  className="bg-[#0a0a0a] border border-[#2e0b11] rounded-lg p-4 space-y-4 shadow-xl hover:border-[#ff003c]/60 transition-all"
                >
                  <div className="flex items-center justify-between border-b border-[#1a1a1a] pb-3">
                    <div>
                      <span className="text-xs font-mono text-[#8a8a8a] block">Target: <strong className="text-white italic">{node.target}</strong></span>
                      <span className="text-sm font-mono font-black text-[#ff003c]">Node Handle: @{node.handle}</span>
                    </div>
                    <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-[#00ffcc]/10 text-[#00ffcc] border border-[#00ffcc]/30 rounded">
                      {node.status}
                    </span>
                  </div>

                  <div className="text-xs font-mono text-[#8a8a8a]">
                    Followers: <span className="text-white font-bold">{node.followers}</span>
                  </div>

                  {/* Metrics Box */}
                  <div className="grid grid-cols-3 gap-2 bg-[#141414] border border-[#2e2e2e] p-3 rounded text-center">
                    <div>
                      <span className="text-[10px] font-mono text-[#8a8a8a] uppercase block">DISPATCHED</span>
                      <span className="text-sm font-black font-mono text-[#ff003c]">{node.dispatched}</span>
                    </div>
                    <div>
                      <span className="text-[10px] font-mono text-[#8a8a8a] uppercase block">DROPPED</span>
                      <span className="text-sm font-black font-mono text-[#800016]">{node.dropped}</span>
                    </div>
                    <div>
                      <span className="text-[10px] font-mono text-[#8a8a8a] uppercase block">CHANNELS</span>
                      <span className="text-sm font-black font-mono text-white">{node.channels}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleRevokeNode(node.id)}
                    className="w-full py-2 bg-[#800016] hover:bg-[#a8001d] text-white font-black text-xs uppercase tracking-wider rounded border border-[#ff003c]/40 transition-all shadow-md active:scale-95"
                  >
                    Revoke & Disconnect Node
                  </button>
                </div>
              ))}
            </div>

          </section>
        </main>
      )}

      {/* Custom Scrollbar Styles */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #0a0a0a;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #2e0b11;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #ff003c;
        }
      `}</style>
    </div>
  );
}