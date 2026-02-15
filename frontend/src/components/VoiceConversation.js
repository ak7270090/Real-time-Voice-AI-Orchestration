import React from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
} from '@livekit/components-react';
import '@livekit/components-styles';
import VoiceAssistantUI from './VoiceAssistantUI';
import styles from './VoiceConversation.module.css';

function VoiceConversation({ connected, token, livekitUrl, documents, onConnect, onDisconnect }) {
  return (
    <section className="card">
      <h2>Voice Conversation</h2>

      {!connected ? (
        <div className={styles.connectSection}>
          <p>Click below to start talking with the AI agent</p>
          <button onClick={onConnect} className="button-large button-primary">
            Connect to Agent
          </button>
        </div>
      ) : (
        <div className={styles.voiceSection}>
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

          <button onClick={onDisconnect} className="button-secondary">
            Disconnect
          </button>
        </div>
      )}
    </section>
  );
}

export default VoiceConversation;
