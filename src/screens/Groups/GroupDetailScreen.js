import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { groupApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const GroupDetailScreen = () => {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth(); // To check if current user is part of group or for leave action

  const [group, setGroup] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showInviteModal, setShowInviteModal] = useState(false); // Placeholder for invite UI
  const [inviteUserId, setInviteUserId] = useState(''); // Placeholder for invite UI

  useEffect(() => {
    const fetchGroupDetails = async () => {
      setIsLoading(true);
      setError('');
      try {
        const details = await groupApi.getGroupDetails(groupId);
        setGroup(details);
      } catch (err) {
        setError(err.message || "Failed to fetch group details.");
        console.error("Fetch group details error:", err);
      }
      setIsLoading(false);
    };
    if (groupId) {
      fetchGroupDetails();
    }
  }, [groupId]);

  const handleLeaveGroup = async () => {
    if (!window.confirm("Are you sure you want to leave this group?")) return;
    setIsLoading(true); // Use a different loading state if needed, or disable button
    setError('');
    try {
      await groupApi.leaveGroup(groupId, user.id); // user.id is current user
      console.log('Successfully left group:', groupId);
      navigate('/groups'); // Navigate back to groups list
    } catch (err) {
      setError(err.message || "Failed to leave group.");
      console.error("Leave group error:", err);
      setIsLoading(false); // Re-enable if error
    }
    // setIsLoading(false); // Should be handled by navigation or specific state
  };

  const handleInviteMember = async () => {
    if (!inviteUserId.trim()) {
        alert("Please enter a User ID to invite.");
        return;
    }
    // In a real app, this would call an API
    console.log(`Attempting to invite user ${inviteUserId} to group ${groupId}`);
    try {
        const updatedGroup = await groupApi.inviteToGroup(groupId, inviteUserId);
        setGroup(updatedGroup); // Refresh group details with new member (mocked)
        setShowInviteModal(false);
        setInviteUserId('');
        alert(`User ${inviteUserId} invited (mocked).`);
    } catch(err) {
        alert(`Failed to invite user: ${err.message}`);
    }
  };

  if (isLoading && !group) {
    return <div style={styles.container}><p>Loading group details...</p></div>;
  }

  if (error) {
    return <div style={styles.container}><p style={styles.errorText}>{error}</p></div>;
  }

  if (!group) {
    return <div style={styles.container}><p>Group not found.</p></div>;
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>{group.name}</h2>

      <div style={styles.section}>
        <h3 style={styles.subHeader}>Members ({group.members ? group.members.length : 0})</h3>
        {group.members && group.members.length > 0 ? (
          <ul style={styles.memberList}>
            {group.members.map(member => (
              <li key={member.id} style={styles.memberItem}>
                {member.name} ({member.id === user.id ? 'You' : member.id})
                {/* TODO: Add remove member button if admin */}
              </li>
            ))}
          </ul>
        ) : (
          <p>No members in this group yet.</p>
        )}
      </div>

      {/* Basic Invite Member UI (Placeholder - could be a modal) */}
      <div style={styles.section}>
        <button onClick={() => setShowInviteModal(prev => !prev)} className="button-primary" style={styles.actionButton}>
          {showInviteModal ? 'Cancel Invite' : 'Invite Member'}
        </button>
        {showInviteModal && (
          <div style={styles.inviteForm}>
            <input
              type="text"
              value={inviteUserId}
              onChange={(e) => setInviteUserId(e.target.value)}
              placeholder="Enter User ID to invite"
              style={styles.input}
            />
            <button onClick={handleInviteMember} className="button-primary" style={{marginLeft: '10px'}}>Send Invite</button>
          </div>
        )}
      </div>

      {/* Section for Group Meal Suggestions */}
      <div style={styles.section}>
        <h3 style={styles.subHeader}>Meal Suggestions</h3>
        <button
          onClick={() => navigate(`/groups/${groupId}/meals`)}
          className="button-primary"
          style={styles.actionButton}
        >
          View Meal Suggestions
        </button>
      </div>

      <div style={styles.actionsContainer}>
        <button onClick={handleLeaveGroup} style={{...styles.actionButton, ...styles.buttonDanger}} disabled={isLoading}>
          {isLoading ? 'Leaving...' : 'Leave Group'}
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: { maxWidth: '700px', margin: '20px auto', padding: 'var(--spacing-large)', backgroundColor: 'var(--surface-color)', borderRadius: 'var(--border-radius)', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'},
  title: { textAlign: 'center', color: 'var(--primary-color)', marginBottom: 'var(--spacing-large)'},
  errorText: { color: 'var(--error-color)', textAlign: 'center', marginBottom: 'var(--spacing-medium)'},
  section: { marginBottom: 'var(--spacing-large)', paddingBottom: 'var(--spacing-medium)', borderBottom: '1px solid #eee'},
  subHeader: { color: 'var(--primary-color)', marginBottom: 'var(--spacing-medium)'},
  memberList: { listStyleType: 'none', padding: 0},
  memberItem: { padding: 'var(--spacing-small) 0', borderBottom: '1px solid #f9f9f9', fontSize: 'var(--font-size-medium)'},
  actionsContainer: { marginTop: 'var(--spacing-large)', display: 'flex', justifyContent: 'center' },
  actionButton: { padding: 'var(--spacing-medium)', textDecoration: 'none' }, // Uses .button-primary class
  buttonDanger: { backgroundColor: 'var(--error-color)', color: 'white'},
  inviteForm: { display: 'flex', marginTop: 'var(--spacing-medium)', gap: 'var(--spacing-small)'},
  input: { flexGrow: 1, padding: 'var(--spacing-small)', border: '1px solid #ccc', borderRadius: 'var(--border-radius)', fontSize: 'var(--font-size-medium)'},
};

export default GroupDetailScreen;
