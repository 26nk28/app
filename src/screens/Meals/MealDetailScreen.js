import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { mealApi } from '../../services/api';

const MealDetailScreen = () => {
  const { mealId } = useParams();
  const navigate = useNavigate();
  const [meal, setMeal] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (mealId) {
      const fetchMeal = async () => {
        setIsLoading(true);
        setError('');
        try {
          const data = await mealApi.getMealDetails(mealId);
          setMeal(data);
        } catch (err) {
          setError(err.message || "Failed to fetch meal details.");
          console.error("Fetch meal details error:", err);
        }
        setIsLoading(false);
      };
      fetchMeal();
    } else {
        setError("Meal ID is missing.");
        setIsLoading(false);
    }
  }, [mealId]);

  if (isLoading) {
    return <div style={styles.container}><p>Loading meal details...</p></div>;
  }

  if (error) {
    return <div style={styles.container}><p style={styles.errorText}>{error}</p><Link to="/">Go Home</Link></div>;
  }

  if (!meal) {
    return <div style={styles.container}><p>Meal not found.</p><Link to="/">Go Home</Link></div>;
  }

  return (
    <div style={styles.container}>
      <button onClick={() => navigate(-1)} style={styles.backButton}>&larr; Back</button>
      <h2 style={styles.title}>{meal.name}</h2>

      <div style={styles.imagePlaceholder}>Meal Image Placeholder</div>

      <div style={styles.section}>
        <h3 style={styles.subHeader}>Overview</h3>
        <p><strong style={styles.detailLabel}>Cuisine:</strong> {meal.cuisine_type}</p>
        <p><strong style={styles.detailLabel}>Preparation Time:</strong> {meal.prep_time} minutes</p>
        <p><strong style={styles.detailLabel}>Difficulty:</strong> {meal.difficulty}</p>
        {meal.nutritional_info && <p><strong style={styles.detailLabel}>Nutrition (approx.):</strong> {meal.nutritional_info}</p>}
      </div>

      <div style={styles.section}>
        <h3 style={styles.subHeader}>Ingredients</h3>
        {meal.ingredients && meal.ingredients.length > 0 ? (
          <ul style={styles.list}>
            {meal.ingredients.map((ingredient, index) => (
              <li key={index} style={styles.listItem}>{ingredient}</li>
            ))}
          </ul>
        ) : <p>Ingredients not available.</p>}
      </div>

      <div style={styles.section}>
        <h3 style={styles.subHeader}>Recipe / Instructions</h3>
        <p style={styles.recipeText}>{meal.recipe || 'Recipe not available.'}</p>
      </div>

      {meal.group_compatibility_breakdown && (
        <div style={styles.section}>
            <h3 style={styles.subHeader}>Group Compatibility</h3>
            <p>Compatible for {meal.compatible_members_count} / {meal.total_members_in_group} members in the original suggested group context.</p>
            <ul style={styles.list}>
                {meal.group_compatibility_breakdown.map(member => (
                    <li key={member.member_id} style={{...styles.listItem, color: member.compatible ? 'var(--success-color)' : 'var(--error-color)'}}>
                        <strong>{member.name || member.member_id}:</strong> {member.compatible ? 'Compatible' : `Not Compatible (${member.reason || 'No specific reason'})`}
                    </li>
                ))}
            </ul>
        </div>
      )}
      {/* TODO: Add to favorites or meal plan button */}
    </div>
  );
};

const styles = {
  container: { maxWidth: '800px', margin: '20px auto', padding: 'var(--spacing-large)', backgroundColor: 'var(--surface-color)', borderRadius: 'var(--border-radius)', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'},
  title: { textAlign: 'center', color: 'var(--primary-color)', marginBottom: 'var(--spacing-medium)'},
  backButton: { marginBottom: 'var(--spacing-medium)', padding: 'var(--spacing-small) var(--spacing-medium)', backgroundColor: '#eee', border: '1px solid #ccc', borderRadius: 'var(--border-radius)', cursor: 'pointer'},
  errorText: { color: 'var(--error-color)', textAlign: 'center', marginBottom: 'var(--spacing-medium)'},
  imagePlaceholder: { height: '250px', backgroundColor: '#e0e0e0', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 'var(--border-radius)', color: '#aaa', marginBottom: 'var(--spacing-large)', fontSize: '1.5rem'},
  section: { marginBottom: 'var(--spacing-large)', paddingBottom: 'var(--spacing-medium)', borderBottom: '1px solid #eee'},
  subHeader: { color: 'var(--primary-color)', marginBottom: 'var(--spacing-small)', fontSize: '1.3rem'},
  detailLabel: { fontWeight: 'bold', color: '#333'},
  list: { listStyleType: 'disc', paddingLeft: '20px'},
  listItem: { marginBottom: 'var(--spacing-small)', fontSize: 'var(--font-size-medium)'},
  recipeText: { whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: 'var(--font-size-medium)'}
};

export default MealDetailScreen;
