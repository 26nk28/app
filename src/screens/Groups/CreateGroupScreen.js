import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { groupApi } from '../../services/api'; // To be added to api.js
import { useAuth } from '../../contexts/AuthContext'; // To get creator_user_id

const CreateGroupScreen = () => {
  const [groupName, setGroupName] = useState('');
  const [invitedUserEmails, setInvitedUserEmails] = useState(''); // Comma-separated emails
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth(); // Assuming user object in context has 'id' or 'userId'

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!groupName.trim()) {
      setError("Group name is required.");
      return;
    }
    // Ensure user and user.id are available. The mock user in AuthContext needs an 'id'.
    // For now, let's assume AuthContext's mock user has `id: 'user_001_mock'` or similar.
    if (!user || !user.id) {
        setError("User information (including ID) not found. Cannot create group. Please ensure you are logged in or AuthContext provides a mock user ID.");
        console.error("CreateGroupScreen: User ID missing from AuthContext. User object:", user);
        return;
    }

    setIsLoading(true);
    setError('');

    const invited_user_ids_array = invitedUserEmails
      .split(',')
      .map(email => email.trim())
      .filter(email => email);

    const groupData = {
      group_name: groupName,
      creator_user_id: user.id,
      invited_user_ids: invited_user_ids_array,
    };

    try {
      const newGroup = await groupApi.createGroup(groupData);
      console.log('Group created:', newGroup);
      navigate(`/groups/${newGroup.group_id}`);
    } catch (err) {
      setError(err.message || "Failed to create group.");
      console.error("Create group error:", err);
    }
    setIsLoading(false);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Create a New Group</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        {error && <p style={styles.errorText}>{error}</p>}
        <div style={styles.inputGroup}>
          <label htmlFor="groupName" style={styles.label}>Group Name:</label>
          <input
            type="text"
            id="groupName"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            style={styles.input}
            required
            disabled={isLoading}
          />
        </div>
        <div style={styles.inputGroup}>
          <label htmlFor="invitedUserEmails" style={styles.label}>
            Invite Members (User IDs, comma-separated):
          </label>
          <input
            type="text"
            id="invitedUserEmails"
            value={invitedUserEmails}
            onChange={(e) => setInvitedUserEmails(e.target.value)}
            style={styles.input}
            placeholder="Enter user IDs, e.g., user_id1,user_id2"
            disabled={isLoading}
          />
          <small style={styles.infoText}>
            The backend expects a list of user IDs. Max 2 invited users (3 total).
          </small>
        </div>
        <button type="submit" className="button-primary" style={styles.button} disabled={isLoading}>
          {isLoading ? 'Creating Group...' : 'Create Group'}
        </button>
        <button type="button" onClick={() => navigate('/groups')} style={{...styles.button, ...styles.buttonSecondary}} disabled={isLoading}>
            Cancel
        </button>
      </form>
    </div>
  );
};

// Styles (similar to ProfileScreen for consistency)
const styles = {
  container: { maxWidth: '500px', margin: '20px auto', padding: 'var(--spacing-large)', backgroundColor: 'var(--surface-color)', borderRadius: 'var(--border-radius)', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'},
  title: { textAlign: 'center', color: 'var(--primary-color)', marginBottom: 'var(--spacing-medium)'},
  errorText: { color: 'var(--error-color)', textAlign: 'center', marginBottom: 'var(--spacing-medium)'},
  form: { display: 'flex', flexDirection: 'column', gap: 'var(--spacing-medium)'},
  inputGroup: { display: 'flex', flexDirection: 'column'},
  label: { marginBottom: 'var(--spacing-small)', color: 'var(--text-color)', fontSize: 'var(--font-size-small)'},
  input: { padding: 'var(--spacing-small)', border: '1px solid #ccc', borderRadius: 'var(--border-radius)', fontSize: 'var(--font-size-medium)'},
  infoText: { fontSize: '0.75rem', color: '#666', marginTop: '4px' },
  button: { padding: 'var(--spacing-medium)', marginTop: 'var(--spacing-small)'},
  buttonSecondary: { backgroundColor: '#aaa', color: 'white'},
};

export default CreateGroupScreen;
