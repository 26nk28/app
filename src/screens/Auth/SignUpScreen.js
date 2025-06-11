import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const SignUpScreen = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSignUp = (e) => {
    e.preventDefault();
    setError('');
    if (!name || !email || !password || !confirmPassword) {
      setError("All fields are required.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords don't match!");
      return;
    }
    // Navigate to UserInfoScreen, passing name and email.
    // The actual user creation/onboarding API call will happen there.
    console.log('SignUpScreen: Navigating to UserInfoScreen with:', { name, email });
    navigate('/user-info', { state: { name, email } });
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Create your HarmonyPlate Account</h2>
      <form onSubmit={handleSignUp} style={styles.form}>
        {error && <p style={styles.errorText}>{error}</p>}
        <div style={styles.inputGroup}>
          <label htmlFor="name" style={styles.label}>Full Name:</label>
          <input type="text" id="name" value={name} onChange={(e) => setName(e.target.value)} required style={styles.input}/>
        </div>
        <div style={styles.inputGroup}>
          <label htmlFor="email" style={styles.label}>Email:</label>
          <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required style={styles.input}/>
        </div>
        <div style={styles.inputGroup}>
          <label htmlFor="password" style={styles.label}>Password:</label>
          <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={styles.input}/>
        </div>
        <div style={styles.inputGroup}>
          <label htmlFor="confirmPassword" style={styles.label}>Confirm Password:</label>
          <input type="password" id="confirmPassword" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required style={styles.input}/>
        </div>
        <button type="submit" className="button-primary" style={styles.button}>Next: Profile Info</button>
      </form>
      <p style={styles.linkText}>
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
};

const styles = { // Using same styles for brevity
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

export default SignUpScreen;
