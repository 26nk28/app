import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { groupApi, invitationApi } from '../../services/api'; // Ensure invitationApi is added

const GroupsListScreen = () => {
  const [groups, setGroups] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [isLoadingGroups, setIsLoadingGroups] = useState(false);
  const [isLoadingInvitations, setIsLoadingInvitations] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const fetchGroups = useCallback(async () => {
    setIsLoadingGroups(true);
    // setError(''); // Clear error related to groups specifically
    try {
      const fetchedGroups = await groupApi.getGroups();
      setGroups(fetchedGroups);
    } catch (err) {
      setError(prev => prev + " Failed to fetch groups. " + (err.message || ''));
      console.error("Fetch groups error:", err);
    }
    setIsLoadingGroups(false);
  }, []);

  const fetchInvitations = useCallback(async () => {
    setIsLoadingInvitations(true);
    // setError(''); // Clear error related to invitations specifically
    try {
      const fetchedInvitations = await invitationApi.getPendingInvitations();
      setInvitations(fetchedInvitations);
    } catch (err) {
      setError(prev => prev + " Failed to fetch invitations. " + (err.message || ''));
      console.error("Fetch invitations error:", err);
    }
    setIsLoadingInvitations(false);
  }, []);

  useEffect(() => {
    fetchGroups();
    fetchInvitations();
  }, [fetchGroups, fetchInvitations]);

  const handleViewGroup = (groupId) => {
    navigate(`/groups/${groupId}`);
  };

  const handleAcceptInvitation = async (invitationId) => {
    setError('');
    try {
      await invitationApi.acceptInvitation(invitationId);
      // Refresh both invitations and groups list
      fetchInvitations();
      fetchGroups();
      alert('Invitation accepted successfully!'); // Or a more subtle notification
    } catch (err) {
      setError(err.message || "Failed to accept invitation.");
      console.error("Accept invitation error:", err);
      alert(`Error: ${err.message || "Failed to accept invitation."}`);
    }
  };

  const handleDeclineInvitation = async (invitationId) => {
    setError('');
    try {
      await invitationApi.declineInvitation(invitationId);
      fetchInvitations(); // Refresh invitations list
      alert('Invitation declined.');
    } catch (err) {
      setError(err.message || "Failed to decline invitation.");
      console.error("Decline invitation error:", err);
      alert(`Error: ${err.message || "Failed to decline invitation."}`);
    }
  };

  // const isLoading = isLoadingGroups || isLoadingInvitations; // This was defined but not used directly.

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>My Groups</h2>
        <Link to="/groups/create" className="button-primary" style={styles.createButton}>
          Create New Group
        </Link>
      </div>

      {error && <p style={styles.errorText}>{error.trim()}</p>}

      {/* Pending Invitations Section */}
      <div style={styles.invitationsSection}>
        <h3 style={styles.subHeader}>Pending Invitations ({invitations.length})</h3>
        {isLoadingInvitations && <p>Loading invitations...</p>}
        {!isLoadingInvitations && invitations.length === 0 && <p style={styles.emptyMessageSmall}>No pending invitations.</p>}
        {invitations.map(inv => (
          <div key={inv.id} style={styles.invitationItem}>
            <p style={styles.invitationText}>
              Join '<strong>{inv.groupName}</strong>' (invited by <em>{inv.inviterName || 'a user'}</em>)
            </p>
            <div style={styles.invitationActions}>
              <button onClick={() => handleAcceptInvitation(inv.id)} className="button-primary" style={{...styles.invitationButton, backgroundColor: 'var(--success-color)'}}>Accept</button>
              <button onClick={() => handleDeclineInvitation(inv.id)} className="button-primary" style={{...styles.invitationButton, backgroundColor: 'var(--error-color)'}}>Decline</button>
            </div>
          </div>
        ))}
      </div>

      <h3 style={styles.subHeader}>Your Groups ({groups.length})</h3>
      {isLoadingGroups && <p>Loading groups...</p>}
      {!isLoadingGroups && groups.length === 0 && !error.includes("Failed to fetch groups") && ( // Avoid double empty message if groups fetch failed
        <p style={styles.emptyMessage}>You are not a member of any groups yet. Why not create one?</p>
      )}

      <div style={styles.groupsGrid}>
        {groups.map(group => (
          <div key={group.id} style={styles.groupCard} onClick={() => handleViewGroup(group.id)}>
            <h3 style={styles.groupName}>{group.name}</h3>
            <p style={styles.groupMembers}>{group.memberCount} Member(s)</p>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  container: { maxWidth: '800px', margin: '20px auto', padding: 'var(--spacing-large)'},
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-large)'},
  title: { color: 'var(--primary-color)'},
  createButton: { textDecoration: 'none', padding: 'var(--spacing-small) var(--spacing-medium)'},
  errorText: { color: 'var(--error-color)', textAlign: 'center', marginBottom: 'var(--spacing-medium)', whiteSpace: 'pre-wrap'},
  emptyMessage: { textAlign: 'center', fontSize: 'var(--font-size-medium)', color: '#666', marginTop: 'var(--spacing-large)'},
  emptyMessageSmall: { textAlign: 'left', fontSize: 'var(--font-size-small)', color: '#666', marginTop: 'var(--spacing-small)'},
  groupsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 'var(--spacing-medium)'},
  groupCard: { padding: 'var(--spacing-medium)', backgroundColor: 'var(--surface-color)', borderRadius: 'var(--border-radius)', boxShadow: '0 1px 5px rgba(0,0,0,0.08)', cursor: 'pointer', transition: 'transform 0.2s ease-in-out, boxShadow 0.2s ease-in-out'},
  groupName: { color: 'var(--primary-color)', marginBottom: 'var(--spacing-small)', fontSize: 'var(--font-size-large)'},
  groupMembers: { fontSize: 'var(--font-size-small)', color: '#555'},
  invitationsSection: { marginBottom: 'var(--spacing-large)', paddingBottom:'var(--spacing-medium)', borderBottom: '2px solid var(--primary-color)'},
  subHeader: { color: 'var(--primary-color)', marginBottom: 'var(--spacing-medium)', marginTop: 'var(--spacing-medium)'},
  invitationItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 'var(--spacing-medium)', border: '1px solid #eee', borderRadius: 'var(--border-radius)', marginBottom: 'var(--spacing-small)', backgroundColor: 'var(--surface-color)'},
  invitationText: { margin: 0, flexGrow: 1 },
  invitationActions: { display: 'flex', gap: 'var(--spacing-small)'},
  invitationButton: { padding: 'var(--spacing-small) var(--spacing-medium)', fontSize: 'var(--font-size-small)'}
};

export default GroupsListScreen;
