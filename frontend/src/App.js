import React, { useState, useEffect, useCallback } from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  useRoomContext,
  useConnectionState,
} from '@livekit/components-react';
import '@livekit/components-styles';
import { ConnectionState } from 'livekit-client';
import './App.css';
import api from './services/apiClient';

/**
 * Main App Component
 * 
 * This is the complete UI for the Voice AI Agent with RAG
 * Features:
 * 1. Document upload and management
 * 2. System prompt editing
 * 3. Voice conversation with LiveKit
 * 4. Live transcription
 * 5. RAG source tracking
 */
function App() {
  // State management
  const [token, setToken] = useState('');
  const [livekitUrl, setLivekitUrl] = useState('');
  const [connected, setConnected] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Load initial data
  useEffect(() => {
    loadPrompt();
    loadDocuments();
  }, []);

  /**
   * Load current system prompt from backend
   */
  const loadPrompt = async () => {
    try {
      const response = await api.get('/prompt');
      setSystemPrompt(response.data.system_prompt);
    } catch (err) {
      console.error('Error loading prompt:', err);
      setError('Failed to load system prompt');
    }
  };

  /**
   * Load list of uploaded documents
   */
  const loadDocuments = async () => {
    try {
      const response = await api.get('/documents');
      setDocuments(response.data);
    } catch (err) {
      console.error('Error loading documents:', err);
    }
  };

  /**
   * Update system prompt
   */
  const handleUpdatePrompt = async () => {
    try {
      await api.post('/prompt', { system_prompt: systemPrompt });
      setSuccess('Prompt updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error updating prompt:', err);
      setError('Failed to update prompt');
    }
  };

  /**
   * Upload document to knowledge base
   */
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.pdf') && !file.name.endsWith('.txt')) {
      setError('Only PDF and TXT files are supported');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/upload-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess(`Document uploaded: ${response.data.chunks_created} chunks created`);
      setTimeout(() => setSuccess(''), 3000);
      
      // Reload documents list
      await loadDocuments();
    } catch (err) {
      console.error('Error uploading document:', err);
      setError('Failed to upload document');
    } finally {
      setUploading(false);
      event.target.value = ''; // Reset file input
    }
  };

  /**
   * Connect to LiveKit room
   */
  const handleConnect = async () => {
    try {
      setError('');
      
      // Generate LiveKit token
      const roomName = `voice-agent-room-${Date.now()}`;
      const response = await api.post('/generate-token', {
        room_name: roomName,
        participant_name: `User-${Date.now()}`,
      });

      setToken(response.data.token);
      setLivekitUrl(response.data.url);
      setConnected(true);
      
      console.log('Connection details:', {
        url: response.data.url,
        room: response.data.room_name
      });
    } catch (err) {
      console.error('Error connecting:', err);
      setError('Failed to connect to voice agent');
    }
  };

  /**
   * Disconnect from room
   */
  const handleDisconnect = () => {
    setToken('');
    setLivekitUrl('');
    setConnected(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Voice AI Agent with RAG</h1>
        <p>Real-time voice conversation with document knowledge base</p>
      </header>

      <div className="container">
        {/* Error/Success Messages */}
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {/* Document Upload Section */}
        <section className="card">
          <h2>Knowledge Base</h2>
          <div className="upload-section">
            <label htmlFor="file-upload" className="upload-button">
              {uploading ? 'Uploading...' : 'Upload Document (PDF/TXT)'}
            </label>
            <input
              id="file-upload"
              type="file"
              accept=".pdf,.txt"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: 'none' }}
            />
          </div>

          {/* Documents List */}
          <div className="documents-list">
            <h3>Uploaded Documents ({documents.length})</h3>
            {documents.length === 0 ? (
              <p className="empty-state">No documents uploaded yet</p>
            ) : (
              <ul>
                {documents.map((doc, index) => (
                  <li key={index}>
                    <div className="doc-info">
                      <strong>{doc.filename}</strong>
                      <span className="doc-meta">
                        {doc.chunk_count} chunks • {(doc.file_size / 1024).toFixed(1)} KB
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        {/* System Prompt Section */}
        <section className="card">
          <h2>Agent Configuration</h2>
          <div className="prompt-section">
            <label htmlFor="system-prompt">System Prompt:</label>
            <textarea
              id="system-prompt"
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              rows={5}
              placeholder="Enter system prompt for the agent..."
            />
            <button onClick={handleUpdatePrompt} className="button-primary">
              Update Prompt
            </button>
          </div>
        </section>

        {/* Voice Agent Section */}
        <section className="card">
          <h2>Voice Conversation</h2>
          
          {!connected ? (
            <div className="connect-section">
              <p>Click below to start talking with the AI agent</p>
              <button onClick={handleConnect} className="button-large button-primary">
                Connect to Agent
              </button>
            </div>
          ) : (
            <div className="voice-section">
              {token && livekitUrl && (
                <LiveKitRoom
                  token={token}
                  serverUrl={livekitUrl}
                  connect={true}
                  audio={true}
                  video={false}
                  onConnected={() => console.log('LiveKit room connected')}
                  onDisconnected={() => console.log('LiveKit room disconnected')}
                >
                  <VoiceAssistantUI documents={documents} />
                  <RoomAudioRenderer />
                </LiveKitRoom>
              )}
              
              <button onClick={handleDisconnect} className="button-secondary">
                Disconnect
              </button>
            </div>
          )}
        </section>

        {/* Instructions */}
        <section className="card instructions">
          <h2>How to Use</h2>
          <ol>
            <li><strong>Upload Documents:</strong> Add PDF or TXT files to the knowledge base</li>
            <li><strong>Configure Prompt:</strong> Customize how the agent behaves</li>
            <li><strong>Connect:</strong> Click "Connect to Agent" to start voice conversation</li>
            <li><strong>Talk:</strong> Ask questions about your uploaded documents</li>
            <li><strong>Listen:</strong> The agent will retrieve relevant info and respond</li>
          </ol>
        </section>
      </div>
    </div>
  );
}

/**
 * Voice Assistant UI Component
 * Shows live transcription and agent state
 */
function VoiceAssistantUI({ documents }) {
  const roomContext = useRoomContext();
  const connectionState = useConnectionState();
  const [agentState, setAgentState] = useState('idle');
  
  useEffect(() => {
    console.log('Connection state:', connectionState);
  }, [connectionState]);

  // Simple state display based on connection
  useEffect(() => {
    if (connectionState === ConnectionState.Connected) {
      setAgentState('connected');
    } else if (connectionState === ConnectionState.Connecting) {
      setAgentState('connecting');
    } else {
      setAgentState('disconnected');
    }
  }, [connectionState]);

  return (
    <div className="voice-assistant">
      <div className="status">
        <div className={`status-indicator ${agentState}`}>
          {connectionState === ConnectionState.Connected && 'Connected - Ready to talk!'}
          {connectionState === ConnectionState.Connecting && 'Connecting...'}
          {connectionState === ConnectionState.Disconnected && 'Disconnected'}
          {connectionState === ConnectionState.Reconnecting && 'Reconnecting...'}
        </div>
      </div>

      <div className="connection-info">
        <p><strong>Connection Status:</strong> {connectionState}</p>
        {connectionState === ConnectionState.Connected && (
          <p className="success-text">You can now speak! The agent is listening.</p>
        )}
      </div>

      <div className="tips">
        <p><strong>Tip:</strong> Ask about your uploaded documents!</p>
        <p>Example: "What does the document say about...?"</p>
        {(!documents || documents.length === 0) && (
          <p className="warning-text">Upload documents first to get better answers!</p>
        )}
      </div>
    </div>
  );
}

export default App;