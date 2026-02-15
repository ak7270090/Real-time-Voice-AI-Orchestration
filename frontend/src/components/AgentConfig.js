import React from 'react';
import styles from './AgentConfig.module.css';

function AgentConfig({ systemPrompt, onPromptChange, onUpdatePrompt }) {
  return (
    <section className="card">
      <h2>Agent Configuration</h2>
      <div className={styles.promptSection}>
        <label htmlFor="system-prompt">System Prompt:</label>
        <textarea
          id="system-prompt"
          value={systemPrompt}
          onChange={(e) => onPromptChange(e.target.value)}
          rows={5}
          placeholder="Enter system prompt for the agent..."
        />
        <button onClick={onUpdatePrompt} className="button-primary">
          Update Prompt
        </button>
      </div>
    </section>
  );
}

export default AgentConfig;
