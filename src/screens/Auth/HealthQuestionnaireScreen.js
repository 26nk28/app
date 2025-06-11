import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext'; // For user info if needed, though IDs from location state
import { personalAgentApi } from '../../services/api'; // Assuming this will be added to api.js

const HealthQuestionnaireScreen = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth(); // Mainly to ensure user is auth'd if directly navigated

  const [userId, setUserId] = useState(null);
  const [agentId, setAgentId] = useState(null);
  // const [onboardingSessionId, setOnboardingSessionId] = useState(null); // If needed by API

  const [messages, setMessages] = useState([]); // Stores { id, text, sender: 'agent' | 'user' }
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  const messagesEndRef = useRef(null); // To auto-scroll to the latest message

  useEffect(() => {
    // Redirect if not authenticated or necessary state is missing
    if (!isAuthenticated()) {
      navigate('/login');
      return;
    }
    if (location.state && location.state.userId && location.state.agentId) {
      setUserId(location.state.userId);
      setAgentId(location.state.agentId);
      // setOnboardingSessionId(location.state.onboardingSessionId);
      console.log("HealthQuestionnaireScreen: Received state:", location.state);
    } else {
      console.error("HealthQuestionnaireScreen: Missing user/agent IDs in location state.");
      setError("Required information to start the questionnaire is missing. Please try onboarding again.");
      // navigate('/'); // Or back to user-info
      return;
    }
  }, [location, navigate, isAuthenticated]);

  // Fetch the first question when component mounts and IDs are set
  useEffect(() => {
    if (userId && agentId) {
      const fetchFirstQuestion = async () => {
        setIsLoading(true);
        setError('');
        try {
          // Assumes startQuestionnaire returns the first question.
          // The agent.py script currently starts with "Let's begin." if mem_text is empty.
          // We need to adapt the backend to provide this as a structured response.
          const response = await personalAgentApi.startQuestionnaire({ userId, agentId });
          if (response && response.first_question) {
            setMessages([{ id: Date.now(), text: response.first_question, sender: 'agent' }]);
          } else {
            // Fallback if the start endpoint doesn't give a question directly,
            // or if the agent's first turn is just an intro.
            // The current agent.py asks "Let's begin." then an actual question.
            // This might mean `startQuestionnaire` is just a trigger,
            // and `respondToQuestionnaire` with an initial empty/null answer gets the *actual* first question.
            // For this mock, let's assume `startQuestionnaire` gives the first real question.
             setMessages([{ id: Date.now(), text: "Welcome to the health questionnaire! Let's get started. What are your primary health goals?", sender: 'agent' }]); // Mock first q
            // setError("Could not fetch the first question.");
          }
        } catch (err) {
          setError(err.message || "Failed to start questionnaire. Please try again later.");
          console.error("Error starting questionnaire:", err);
        }
        setIsLoading(false);
      };
      fetchFirstQuestion();
    }
  }, [userId, agentId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleInputChange = (e) => {
    setCurrentInput(e.target.value);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!currentInput.trim() || isLoading || isComplete) return;

    const userAnswer = currentInput;
    const lastAgentQuestion = messages.filter(m => m.sender === 'agent').pop()?.text || "";

    setMessages(prev => [...prev, { id: Date.now(), text: userAnswer, sender: 'user' }]);
    setCurrentInput('');
    setIsLoading(true);
    setError('');

    try {
      const response = await personalAgentApi.respondToQuestionnaire({
        userId,
        agentId,
        answer: userAnswer,
        last_question_text: lastAgentQuestion // Sending last agent question might be useful for context on backend
      });

      if (response.next_question) {
        setMessages(prev => [...prev, { id: Date.now() + 1, text: response.next_question, sender: 'agent' }]);
      } else if (response.questionnaire_complete) {
        setMessages(prev => [...prev, { id: Date.now() + 1, text: response.completion_message || "Thank you! Your health profile is updated.", sender: 'agent' }]);
        setIsComplete(true);
      } else {
        // Fallback for unexpected response
        setError("Received an unexpected response from the agent.");
      }
    } catch (err) {
      setError(err.message || "Failed to send message. Please try again.");
      // Optionally, allow resending or add the user's message back to input
      // For simplicity, we just show an error.
      setMessages(prev => prev.slice(0, -1)); // Remove user's optimistic message if API fails
    }
    setIsLoading(false);
  };

  if (!userId || !agentId && !error) {
      return <div style={styles.container}><p>Loading questionnaire setup...</p></div>;
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Health Questionnaire</h2>
      <p style={styles.subTitle}>Chat with HarmonyHelper to complete your health profile.</p>
      {error && <p style={styles.errorText}>{error}</p>}

      <div style={styles.chatWindow}>
        {messages.map(msg => (
          <div key={msg.id} style={msg.sender === 'user' ? styles.userMessage : styles.agentMessage}>
            <p style={styles.messageText}>{msg.text}</p>
          </div>
        ))}
        <div ref={messagesEndRef} /> {/* For auto-scrolling */}
      </div>

      {isComplete ? (
        <div style={styles.completionContainer}>
          <p style={styles.completionText}>Questionnaire Complete! Proceed to your dashboard.</p>
          <button onClick={() => navigate('/')} className="button-primary" style={styles.button}>
            Go to Dashboard
          </button>
        </div>
      ) : (
        <form onSubmit={handleSendMessage} style={styles.inputForm}>
          <input
            type="text"
            value={currentInput}
            onChange={handleInputChange}
            placeholder="Type your answer..."
            style={styles.input}
            disabled={isLoading}
          />
          <button type="submit" className="button-primary" style={styles.button} disabled={isLoading || !currentInput.trim()}>
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      )}
    </div>
  );
};

// Basic styles - should be refined
const styles = {
  container: { maxWidth: '600px', margin: '20px auto', padding: 'var(--spacing-large)', backgroundColor: 'var(--surface-color)', borderRadius: 'var(--border-radius)', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', display: 'flex', flexDirection: 'column'},
  title: { textAlign: 'center', color: 'var(--primary-color)', marginBottom: 'var(--spacing-small)'},
  subTitle: { textAlign: 'center', color: 'var(--text-color)', marginBottom: 'var(--spacing-medium)', fontSize: 'var(--font-size-small)'},
  errorText: { color: 'var(--error-color)', textAlign: 'center', fontSize: 'var(--font-size-small)', marginBottom: 'var(--spacing-medium)'},
  chatWindow: {
    height: '400px', // Fixed height for chat window
    overflowY: 'auto',
    border: '1px solid #ccc',
    borderRadius: 'var(--border-radius)',
    padding: 'var(--spacing-medium)',
    marginBottom: 'var(--spacing-medium)',
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-small)',
  },
  userMessage: { alignSelf: 'flex-end', backgroundColor: 'var(--primary-color)', color: 'var(--text-color-light)', padding: 'var(--spacing-small) var(--spacing-medium)', borderRadius: '15px 15px 0 15px', maxWidth: '70%'},
  agentMessage: { alignSelf: 'flex-start', backgroundColor: '#e0e0e0', color: 'var(--text-color)', padding: 'var(--spacing-small) var(--spacing-medium)', borderRadius: '15px 15px 15px 0', maxWidth: '70%'},
  messageText: { margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' },
  inputForm: { display: 'flex', gap: 'var(--spacing-small)'},
  input: { flexGrow: 1, padding: 'var(--spacing-medium)', border: '1px solid #ccc', borderRadius: 'var(--border-radius)', fontSize: 'var(--font-size-medium)'},
  button: { padding: 'var(--spacing-medium)' }, // Use class for consistent button style
  completionContainer: { textAlign: 'center', marginTop: 'var(--spacing-medium)'},
  completionText: { marginBottom: 'var(--spacing-medium)', fontSize: 'var(--font-size-medium)'}
};

export default HealthQuestionnaireScreen;
