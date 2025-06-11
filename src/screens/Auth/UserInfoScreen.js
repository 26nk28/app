import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext'; // Import useAuth

const UserInfoScreen = () => {
  const [phone, setPhone] = useState('');
  const [healthForm, setHealthForm] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { signupAndOnboard } = useAuth(); // Get the onboarding function

  const [userData, setUserData] = useState({ name: '', email: '' });

  useEffect(() => {
    if (location.state && location.state.email && location.state.name) {
      setUserData({ name: location.state.name, email: location.state.email });
    } else {
      console.warn("UserInfoScreen accessed without user name/email. Redirecting to signup.");
      navigate('/signup');
    }
  }, [location, navigate]);

  const handleSubmitUserInfo = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!healthForm.trim()) {
        setError("Health summary is required.");
        setIsLoading(false);
        return;
    }

    const onboardingData = {
      name: userData.name,
      email: userData.email,
      phone: phone,
      health_form: healthForm,
    };

    const result = await signupAndOnboard(onboardingData);
    setIsLoading(false);

    if (result.success && result.data) {
      console.log('UserInfoScreen: Onboarding API call successful', result.data);
      // result.data contains { message, onboarding_session_id, user_id, agent_id }
      // Navigate to health questionnaire, passing the necessary IDs
      navigate('/health-questionnaire', {
        state: {
          userId: result.data.user_id,
          agentId: result.data.agent_id,
          onboardingSessionId: result.data.onboarding_session_id
        }
      });
    } else {
      setError(result.message || "Failed to submit user information. Please try again.");
      console.error('UserInfoScreen: Onboarding API call failed', result.message);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Complete Your Profile, {userData.name}</h2>
      <p style={styles.subTitle}>Tell us a bit more to personalize your HarmonyPlate experience.</p>
      <form onSubmit={handleSubmitUserInfo} style={styles.form}>
        {error && <p style={styles.errorText}>{error}</p>}
        <div style={styles.inputGroup}>
          <label htmlFor="phone" style={styles.label}>Phone Number (Optional):</label>
          <input type="tel" id="phone" value={phone} onChange={(e) => setPhone(e.target.value)} style={styles.input} disabled={isLoading}/>
        </div>
        <div style={styles.inputGroup}>
          <label htmlFor="healthForm" style={styles.label}>Initial Health Summary:</label>
          <textarea id="healthForm" value={healthForm} onChange={(e) => setHealthForm(e.target.value)} rows="5" required style={styles.textarea} placeholder="Briefly describe dietary preferences, allergies, or health goals (e.g., vegetarian, allergic to nuts, looking for low-carb meals)." disabled={isLoading}></textarea>
          <p style={styles.infoText}>Our HarmonyHelper agent will chat with you next to refine these details!</p>
        </div>
        <button type="submit" className="button-primary" style={styles.button} disabled={isLoading}>
          {isLoading ? 'Submitting...' : 'Continue to Health Chat'}
        </button>
      </form>
    </div>
  );
};

// Re-using styles
const styles = {
  container: { maxWidth: '500px', margin: '50px auto', padding: 'var(--spacing-large)', backgroundColor: 'var(--surface-color)', borderRadius: 'var(--border-radius)', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'},
  title: { textAlign: 'center', color: 'var(--primary-color)', marginBottom: 'var(--spacing-small)'},
  subTitle: { textAlign: 'center', color: 'var(--text-color)', marginBottom: 'var(--spacing-medium)', fontSize: 'var(--font-size-small)'},
  form: { display: 'flex', flexDirection: 'column', gap: 'var(--spacing-medium)'},
  inputGroup: { display: 'flex', flexDirection: 'column'},
  label: { marginBottom: 'var(--spacing-small)', color: 'var(--text-color)', fontSize: 'var(--font-size-small)'},
  input: { padding: 'var(--spacing-small)', border: '1px solid #ccc', borderRadius: 'var(--border-radius)', fontSize: 'var(--font-size-medium)'},
  textarea: { padding: 'var(--spacing-small)', border: '1px solid #ccc', borderRadius: 'var(--border-radius)', fontSize: 'var(--font-size-medium)', fontFamily: 'inherit', minHeight: '100px'},
  button: { padding: 'var(--spacing-medium) var(--spacing-small)'},
  errorText: { color: 'var(--error-color)', textAlign: 'center', fontSize: 'var(--font-size-small)'},
  infoText: { fontSize: 'var(--font-size-small)', color: '#666', marginTop: 'var(--spacing-small)'}
};

export default UserInfoScreen;
