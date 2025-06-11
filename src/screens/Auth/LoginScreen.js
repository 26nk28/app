import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext'; // Import useAuth

const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth(); // Get login from context

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const result = await login(email, password); // Use context login
    setIsLoading(false);

    if (result.success) {
      console.log('LoginScreen: Login successful via context');
      navigate('/');
    } else {
      setError(result.message || 'Invalid email or password.');
      console.log('LoginScreen: Login failed via context', result.message);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Login to HarmonyPlate</h2>
      <form onSubmit={handleLogin} style={styles.form}>
        {error && <p style={styles.errorText}>{error}</p>}
        <div style={styles.inputGroup}>
          <label htmlFor="email" style={styles.label}>Email:</label>
          <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required style={styles.input} disabled={isLoading}/>
        </div>
        <div style={styles.inputGroup}>
          <label htmlFor="password" style={styles.label}>Password:</label>
          <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={styles.input} disabled={isLoading}/>
        </div>
        <button type="submit" className="button-primary" style={styles.button} disabled={isLoading}>
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p style={styles.linkText}>
        Don't have an account? <Link to="/signup">Sign Up</Link>
      </p>
    </div>
  );
};

// Re-using styles
const styles = {
  container: { maxWidth: '400px', margin: '50px auto', padding: 'var(--spacing-large)', backgroundColor: 'var(--surface-color)', borderRadius: 'var(--border-radius)', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'},
  title: { textAlign: 'center', color: 'var(--primary-color)', marginBottom: 'var(--spacing-medium)'},
  form: { display: 'flex', flexDirection: 'column', gap: 'var(--spacing-medium)'},
  inputGroup: { display: 'flex', flexDirection: 'column'},
  label: { marginBottom: 'var(--spacing-small)', color: 'var(--text-color)', fontSize: 'var(--font-size-small)'},
  input: { padding: 'var(--spacing-small)', border: '1px solid #ccc', borderRadius: 'var(--border-radius)', fontSize: 'var(--font-size-medium)'},
  button: { padding: 'var(--spacing-medium) var(--spacing-small)'},
  errorText: { color: 'var(--error-color)', textAlign: 'center', fontSize: 'var(--font-size-small)'},
  linkText: { marginTop: 'var(--spacing-medium)', textAlign: 'center', fontSize: 'var(--font-size-small)'}
};
export default LoginScreen;
