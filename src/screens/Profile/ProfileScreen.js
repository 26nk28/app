import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { userProfileApi } from '../../services/api'; // To be added to api.js
import { useNavigate } from 'react-router-dom'; // Import useNavigate

const ProfileScreen = () => {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate(); // Initialize useNavigate
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    phone: '',
    healthSummary: 'Your detailed health summary will appear here after completing the questionnaire and further interactions. For now, this is a placeholder.',
  });

  useEffect(() => {
    const fetchProfile = async () => {
      setIsLoading(true);
      setError('');
      try {
        const data = await userProfileApi.getProfile();
        setProfileData({
          name: data.name || '',
          email: data.email || '',
          phone: data.phone || '',
          healthSummary: data.healthSummary || 'No health summary available yet.',
        });
      } catch (err) {
        setError(err.message || "Failed to fetch profile data.");
        console.error("Profile fetch error:", err);
      }
      setIsLoading(false);
    };

    if (token) {
        fetchProfile();
    } else if (user) {
        setProfileData({
            name: user.name || '',
            email: user.email || '',
            phone: user.phone || '',
            healthSummary: user.healthSummary || 'Health summary from context (placeholder).',
        });
    }
  }, [user, token]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
  };

  const handleEditToggle = () => {
    setIsEditing(!isEditing);
    setError('');
    setSuccessMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccessMessage('');
    try {
      const updatedData = await userProfileApi.updateProfile({
        name: profileData.name,
        phone: profileData.phone,
      });
      setProfileData(prev => ({ ...prev, ...updatedData }));
      setSuccessMessage("Profile updated successfully!");
      setIsEditing(false);
    } catch (err) {
      setError(err.message || "Failed to update profile.");
      console.error("Profile update error:", err);
    }
    setIsLoading(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login'); // Redirect to login after logout
  };

  if (isLoading && !profileData.email) {
      return <div style={styles.container}><p>Loading profile...</p></div>;
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>My Profile</h2>
      {error && <p style={styles.errorText}>{error}</p>}
      {successMessage && <p style={styles.successText}>{successMessage}</p>}

      {isEditing ? (
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label htmlFor="name" style={styles.label}>Full Name:</label>
            <input type="text" id="name" name="name" value={profileData.name} onChange={handleInputChange} style={styles.input} required />
          </div>
          <div style={styles.inputGroup}>
            <label htmlFor="email" style={styles.label}>Email:</label>
            <input type="email" id="email" name="email" value={profileData.email} style={{...styles.input, backgroundColor: '#f0f0f0'}} readOnly />
            <small style={styles.infoText}>Email cannot be changed.</small>
          </div>
          <div style={styles.inputGroup}>
            <label htmlFor="phone" style={styles.label}>Phone Number:</label>
            <input type="tel" id="phone" name="phone" value={profileData.phone} onChange={handleInputChange} style={styles.input} />
          </div>

          <div style={styles.buttonGroup}>
            <button type="submit" className="button-primary" style={styles.button} disabled={isLoading}>
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
            <button type="button" onClick={handleEditToggle} style={{...styles.button, ...styles.buttonSecondary}} disabled={isLoading}>
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <div style={styles.viewMode}>
          <p style={styles.field}><strong style={styles.fieldLabel}>Name:</strong> {profileData.name}</p>
          <p style={styles.field}><strong style={styles.fieldLabel}>Email:</strong> {profileData.email}</p>
          <p style={styles.field}><strong style={styles.fieldLabel}>Phone:</strong> {profileData.phone || 'Not provided'}</p>

          <h3 style={styles.subHeader}>Health Summary</h3>
          <div style={styles.healthSummaryBox}>
            <p>{profileData.healthSummary}</p>
          </div>
          <button onClick={handleEditToggle} className="button-primary" style={styles.button}>Edit Profile</button>
        </div>
      )}
      <button onClick={handleLogout} style={{...styles.button, ...styles.buttonDanger, marginTop: 'var(--spacing-large)'}}>
        Logout
      </button>
    </div>
  );
};

const styles = {
  container: { maxWidth: '600px', margin: '20px auto', padding: 'var(--spacing-large)', backgroundColor: 'var(--surface-color)', borderRadius: 'var(--border-radius)', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'},
  title: { textAlign: 'center', color: 'var(--primary-color)', marginBottom: 'var(--spacing-medium)'},
  subHeader: { color: 'var(--primary-color)', marginTop: 'var(--spacing-large)', marginBottom: 'var(--spacing-small)' },
  errorText: { color: 'var(--error-color)', textAlign: 'center', marginBottom: 'var(--spacing-medium)'},
  successText: { color: 'var(--success-color)', textAlign: 'center', marginBottom: 'var(--spacing-medium)'},
  form: { display: 'flex', flexDirection: 'column', gap: 'var(--spacing-medium)'},
  inputGroup: { display: 'flex', flexDirection: 'column'},
  label: { marginBottom: 'var(--spacing-small)', color: 'var(--text-color)', fontSize: 'var(--font-size-small)'},
  input: { padding: 'var(--spacing-small)', border: '1px solid #ccc', borderRadius: 'var(--border-radius)', fontSize: 'var(--font-size-medium)'},
  infoText: { fontSize: '0.75rem', color: '#666', marginTop: '4px' },
  viewMode: { display: 'flex', flexDirection: 'column', gap: 'var(--spacing-small)'},
  field: { fontSize: 'var(--font-size-medium)', padding: 'var(--spacing-small) 0', borderBottom: '1px solid #eee'},
  fieldLabel: { color: 'var(--text-color)', marginRight: 'var(--spacing-small)' },
  healthSummaryBox: { border: '1px dashed #ccc', padding: 'var(--spacing-medium)', borderRadius: 'var(--border-radius)', backgroundColor: '#f9f9f9', minHeight: '100px', marginBottom: 'var(--spacing-medium)'},
  button: { padding: 'var(--spacing-medium)', marginTop: 'var(--spacing-small)'},
  buttonGroup: { display: 'flex', gap: 'var(--spacing-medium)', marginTop: 'var(--spacing-small)'},
  buttonSecondary: { backgroundColor: '#aaa', color: 'white'},
  buttonDanger: { backgroundColor: 'var(--error-color)', color: 'white' } // Corrected var name from --error-code to --error-color
};

export default ProfileScreen;
