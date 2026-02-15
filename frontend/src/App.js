import React, { useState } from 'react';
import './App.css';
import AlertMessage from './components/AlertMessage';
import KnowledgeBase from './components/KnowledgeBase';
import AgentConfig from './components/AgentConfig';
import VoiceConversation from './components/VoiceConversation';
import Instructions from './components/Instructions';
import useDocuments from './hooks/useDocuments';
import usePrompt from './hooks/usePrompt';
import useVoiceConnection from './hooks/useVoiceConnection';

function App() {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const { documents, uploading, handleFileUpload, handleDeleteDocument } =
    useDocuments({ setError, setSuccess });

  const { systemPrompt, setSystemPrompt, handleUpdatePrompt } =
    usePrompt({ setError, setSuccess });

  const { token, livekitUrl, connected, handleConnect, handleDisconnect } =
    useVoiceConnection({ setError });

  return (
    <div className="App">
      <header className="App-header">
        <h1>Voice AI Agent with RAG</h1>
        <p>Real-time voice conversation with document knowledge base</p>
      </header>

      <div className="container">
        <AlertMessage error={error} success={success} />

        <KnowledgeBase
          documents={documents}
          uploading={uploading}
          onFileUpload={handleFileUpload}
          onDeleteDocument={handleDeleteDocument}
        />

        <AgentConfig
          systemPrompt={systemPrompt}
          onPromptChange={setSystemPrompt}
          onUpdatePrompt={handleUpdatePrompt}
        />

        <VoiceConversation
          connected={connected}
          token={token}
          livekitUrl={livekitUrl}
          documents={documents}
          onConnect={handleConnect}
          onDisconnect={handleDisconnect}
        />

        <Instructions />
      </div>
    </div>
  );
}

export default App;
