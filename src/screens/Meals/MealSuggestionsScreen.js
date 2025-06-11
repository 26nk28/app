import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { mealApi } from '../../services/api'; // To be added to api.js

const MealSuggestionsScreen = () => {
  const { groupId } = useParams(); // Get groupId from URL
  const navigate = useNavigate();

  const [suggestions, setSuggestions] = useState([]);
  const [filteredSuggestions, setFilteredSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Filter states
  const [cuisineFilter, setCuisineFilter] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('');
  // Add more filters as needed (e.g., prepTime)

  const availableCuisines = ['Italian', 'Mexican', 'Indian', 'Chinese', 'Any']; // Mock
  const availableDifficulties = ['Easy', 'Medium', 'Hard', 'Any']; // Mock

  const fetchSuggestions = useCallback(async () => {
    if (!groupId) {
        setError("Group ID is missing.");
        return;
    }
    setIsLoading(true);
    setError('');
    try {
      // Pass current filters to the API call (mocked API will handle them)
      const fetchedSuggestions = await mealApi.getMealSuggestions(groupId, {
        cuisine: cuisineFilter === 'Any' ? '' : cuisineFilter,
        difficulty: difficultyFilter === 'Any' ? '' : difficultyFilter,
      });
      setSuggestions(fetchedSuggestions);
      setFilteredSuggestions(fetchedSuggestions); // Initially, filtered is same as all
    } catch (err) => {
      setError(err.message || "Failed to fetch meal suggestions.");
      console.error("Fetch meal suggestions error:", err);
    }
    setIsLoading(false);
  }, [groupId, cuisineFilter, difficultyFilter]); // Re-fetch if filters change

  useEffect(() => {
    fetchSuggestions();
  }, [fetchSuggestions]);

  if (!groupId) {
    return <div style={styles.container}><p style={styles.errorText}>No Group ID provided. Cannot fetch suggestions.</p> <Link to="/groups">Go to groups</Link></div>;
  }

  if (isLoading) {
    return <div style={styles.container}><p>Loading meal suggestions for group {groupId}...</p></div>;
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Meal Suggestions for Group</h2>
      <Link to={`/groups/${groupId}`} style={styles.backLink}>&larr; Back to Group Details</Link>

      {error && <p style={styles.errorText}>{error}</p>}

      <div style={styles.filterContainer}>
        <h3 style={styles.filterTitle}>Filters</h3>
        <div style={styles.filterGroup}>
          <label htmlFor="cuisineFilter" style={styles.filterLabel}>Cuisine:</label>
          <select id="cuisineFilter" value={cuisineFilter} onChange={(e) => setCuisineFilter(e.target.value)} style={styles.filterSelect}>
            {availableCuisines.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div style={styles.filterGroup}>
          <label htmlFor="difficultyFilter" style={styles.filterLabel}>Difficulty:</label>
          <select id="difficultyFilter" value={difficultyFilter} onChange={(e) => setDifficultyFilter(e.target.value)} style={styles.filterSelect}>
            {availableDifficulties.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
      </div>

      {filteredSuggestions.length === 0 && !isLoading && !error && (
        <p style={styles.emptyMessage}>No meal suggestions found for this group with the current filters.</p>
      )}

      <div style={styles.suggestionsGrid}>
        {filteredSuggestions.map(meal => (
          <div key={meal.id || meal.name} style={styles.mealCard} onClick={() => navigate(`/meals/details/${meal.id || meal.name}`)}>
            <div style={styles.mealImagePlaceholder}>Image</div>
            <h3 style={styles.mealName}>{meal.name}</h3>
            <p style={styles.mealInfo}>Cuisine: {meal.cuisine_type}</p>
            <p style={styles.mealInfo}>Prep Time: {meal.prep_time} mins</p>
            <p style={styles.mealInfo}>Difficulty: {meal.difficulty}</p>
            <p style={styles.mealInfo}>Compatible: {meal.compatible_members_count}/{meal.total_members_in_group} members</p>
            {meal.incompatible_reasons && meal.incompatible_reasons.length > 0 && (
                <small style={styles.incompatibleReason}>Restrictions: {meal.incompatible_reasons.join(', ')}</small>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  container: { maxWidth: '900px', margin: '20px auto', padding: 'var(--spacing-large)'},
  title: { textAlign: 'center', color: 'var(--primary-color)', marginBottom: 'var(--spacing-medium)'},
  backLink: { display: 'inline-block', marginBottom: 'var(--spacing-medium)', color: 'var(--primary-color)', textDecoration: 'none' },
  errorText: { color: 'var(--error-color)', textAlign: 'center', marginBottom: 'var(--spacing-medium)'},
  emptyMessage: { textAlign: 'center', fontSize: 'var(--font-size-medium)', color: '#666', marginTop: 'var(--spacing-large)'},
  filterContainer: { backgroundColor: 'var(--surface-color)', padding: 'var(--spacing-medium)', borderRadius: 'var(--border-radius)', marginBottom: 'var(--spacing-large)', boxShadow: '0 1px 3px rgba(0,0,0,0.05)'},
  filterTitle: { color: 'var(--primary-color)', marginBottom: 'var(--spacing-medium)', borderBottom: '1px solid #eee', paddingBottom: 'var(--spacing-small)'},
  filterGroup: { display: 'inline-block', marginRight: 'var(--spacing-large)', marginBottom: 'var(--spacing-small)'},
  filterLabel: { marginRight: 'var(--spacing-small)', fontSize: 'var(--font-size-small)'},
  filterSelect: { padding: 'var(--spacing-small)', borderRadius: 'var(--border-radius)', border: '1px solid #ccc'},
  suggestionsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 'var(--spacing-medium)'},
  mealCard: { padding: 'var(--spacing-medium)', backgroundColor: 'var(--surface-color)', borderRadius: 'var(--border-radius)', boxShadow: '0 1px 5px rgba(0,0,0,0.08)', cursor: 'pointer', transition: 'transform 0.2s ease-in-out, boxShadow 0.2s ease-in-out'},
  mealImagePlaceholder: { height: '150px', backgroundColor: '#e0e0e0', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 'var(--border-radius) var(--border-radius) 0 0', color: '#aaa', marginBottom: 'var(--spacing-small)'},
  mealName: { color: 'var(--primary-color)', marginBottom: 'var(--spacing-small)', fontSize: 'var(--font-size-large)'},
  mealInfo: { fontSize: 'var(--font-size-small)', color: '#555', marginBottom: '4px'},
  incompatibleReason: { fontSize: '0.75rem', color: 'var(--error-color)', display: 'block', marginTop: 'var(--spacing-small)'}
};

export default MealSuggestionsScreen;
