// Basic API service utility

const BASE_URL = '/api'; // Adjust if your API is hosted elsewhere or has a different prefix

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // If authToken is in localStorage, add it to headers (for protected routes)
  const token = localStorage.getItem('authToken');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Request failed with status: ' + response.status }));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    if (response.status === 204) { // No Content
        return null;
    }
    return await response.json();
  } catch (error) {
    console.error('API request error:', error);
    throw error; // Re-throw to be caught by the calling function
  }
}

export const apiService = {
  get: (endpoint, options) => request(endpoint, { ...options, method: 'GET' }),
  post: (endpoint, body, options) => request(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) }),
  put: (endpoint, body, options) => request(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) }),
  delete: (endpoint, options) => request(endpoint, { ...options, method: 'DELETE' }),
};

// Specific API functions
export const userOnboardingApi = {
  onboardUser: (userData) => {
    // userData should include: name, email, phone (optional), health_form
    // Corresponds to POST /onboard in user_onboarding/api/routes/onboarding.py
    return apiService.post('/user_onboarding/onboard', userData);
    // Note: The actual backend route might be /user_onboarding/onboard based on how FastAPI routers are set up.
    // The user_onboarding main.py mounts its router with a prefix, typically.
    // Let's assume the full path is /api/user_onboarding/onboard
  },
  // login: (credentials) => apiService.post('/auth/login', credentials), // Placeholder for login
};

/*
Backend structure for user_onboarding:
- main.py:
  app.include_router(onboarding_router, prefix="/user_onboarding", tags=["User Onboarding"])
  app.include_router(health_router, prefix="/user_onboarding", tags=["Health"])
- onboarding.py (routes):
  router = APIRouter()
  @router.post("/onboard") async def onboard_user(request: UserOnboardingRequest)
    - UserOnboardingRequest: name, email, phone, health_form

So the frontend should call POST /api/user_onboarding/onboard
*/
// ===========================================
// Personal Agent API (Health Questionnaire)
// MOCKED IMPLEMENTATIONS
// ===========================================
// These functions simulate interactions with a personal agent backend.
// In a real scenario, these would make HTTP requests to endpoints exposed
// by the personal_agent service.

let mockQuestionnaireState = {
  turn: 0,
  questions: [
    "Great! To start, what are your main dietary goals or concerns? (e.g., weight loss, muscle gain, managing allergies, eating healthier)",
    "Thanks! Do you have any food allergies or intolerances we should be aware of? (e.g., nuts, dairy, gluten)",
    "Noted. Are there any specific foods or cuisines you strongly dislike or prefer to avoid?",
    "Almost done! On a typical week, how many days do you prefer to cook at home versus eating out or ordering in?",
    "And finally, what's your general activity level? (e.g., sedentary, lightly active, moderately active, very active)"
  ],
  userName: "User", // Could be fetched or passed if needed
};

export const personalAgentApi = {
  startQuestionnaire: async ({ userId, agentId }) => {
    console.log('MOCK personalAgentApi.startQuestionnaire called with:', { userId, agentId });
    mockQuestionnaireState.turn = 0; // Reset for new session (for mock)
    // Simulate a slight delay
    await new Promise(resolve => setTimeout(resolve, 500));

    if (mockQuestionnaireState.questions.length > 0) {
      return { first_question: `Okay ${mockQuestionnaireState.userName}, let's personalize your health profile. ${mockQuestionnaireState.questions[0]}` };
    }
    return { first_question: "Welcome! It seems we've run out of predefined mock questions to start with." };
  },

  respondToQuestionnaire: async ({ userId, agentId, answer, last_question_text }) => {
    console.log('MOCK personalAgentApi.respondToQuestionnaire called with:', { userId, agentId, answer, last_question_text });
    mockQuestionnaireState.turn++;

    // Simulate backend processing and LLM response delay
    await new Promise(resolve => setTimeout(resolve, 800));

    if (mockQuestionnaireState.turn < mockQuestionnaireState.questions.length) {
      // Provide a generic follow-up before the next question
      let followUp = "Thanks for sharing. ";
      if (mockQuestionnaireState.turn === 1) followUp = "Understood. ";
      if (mockQuestionnaireState.turn === 2) followUp = "Good to know. ";
      if (mockQuestionnaireState.turn === 3) followUp = "Okay. ";

      return { next_question: followUp + mockQuestionnaireState.questions[mockQuestionnaireState.turn] };
    } else {
      // Questionnaire complete
      return {
        questionnaire_complete: true,
        completion_message: "That's all for now! Your health profile has been updated based on our chat. You can always adjust these details later in your profile settings."
      };
    }
  },
};

// ===========================================
// User Profile API
// MOCKED IMPLEMENTATIONS
// ===========================================
// Simulates fetching and updating user profile data.

let mockUserProfile = {
  id: 'user_001_mock',
  name: 'Mock User Name',
  email: 'user@example.com',
  phone: '123-456-7890',
  healthSummary: 'Loves Italian food, trying to eat more vegetables. Allergic to shellfish. Moderately active.',
};

export const userProfileApi = {
  getProfile: async () => {
    console.log('MOCK userProfileApi.getProfile called');
    await new Promise(resolve => setTimeout(resolve, 500));
    /*
      In a real app, this would fetch from /api/users/me or /api/profile.
      It should also ideally use the token from localStorage via apiService.
      The apiService.request function (if called directly or via apiService.get)
      would handle adding the token. If no token, the backend should ideally
      return a 401, which apiService.request would throw as an error.
    */
    return { ...mockUserProfile };
  },

  updateProfile: async (profileUpdates) => {
    console.log('MOCK userProfileApi.updateProfile called with:', profileUpdates);
    await new Promise(resolve => setTimeout(resolve, 700));

    mockUserProfile = {
      ...mockUserProfile,
      ...profileUpdates,
    };
    console.log('MOCK userProfile updated:', mockUserProfile);
    return {
        name: mockUserProfile.name,
        phone: mockUserProfile.phone
    };
  },
};

// ===========================================
// Group API
// MOCKED IMPLEMENTATIONS
// ===========================================

let mockUserGroups = [
  { id: 'group_001', name: 'Roommates Food Club', memberCount: 3, members: [{id: 'user_001_mock', name: 'Me'}, {id: 'user_002', name: 'Alice'}, {id: 'user_003', name: 'Bob'}] },
  { id: 'group_002', name: 'Weekend Brunch Crew', memberCount: 2, members: [{id: 'user_001_mock', name: 'Me'}, {id: 'user_004', name: 'Charlie'}] },
  { id: 'group_003', name: 'Family Dinners', memberCount: 1, members: [{id: 'user_001_mock', name: 'Me'}] },
];
let nextGroupId = 4;
const MAX_GROUP_MEMBERS = 3; // As per group_onboarding backend validation

export const groupApi = {
  getGroups: async () => {
    console.log('MOCK groupApi.getGroups called');
    await new Promise(resolve => setTimeout(resolve, 500));
    return [...mockUserGroups];
  },

  getGroupDetails: async (groupId) => {
    console.log('MOCK groupApi.getGroupDetails called for group:', groupId);
    await new Promise(resolve => setTimeout(resolve, 300));
    const group = mockUserGroups.find(g => g.id === groupId);
    if (group) {
        return JSON.parse(JSON.stringify(group)); // Return a copy to avoid direct state mutation
    }
    throw new Error("Group not found");
  },

  createGroup: async (groupData) => {
    console.log('MOCK groupApi.createGroup called with:', groupData);
    await new Promise(resolve => setTimeout(resolve, 700));

    if (groupData.invited_user_ids.length > (MAX_GROUP_MEMBERS - 1)) { // -1 for creator
        throw new Error(`Validation Error: Maximum ${MAX_GROUP_MEMBERS -1} users can be invited.`);
    }

    const newGroupId = `group_00${nextGroupId++}`;
    const newGroup = {
      id: newGroupId,
      group_id: newGroupId,
      name: groupData.group_name,
      group_name: groupData.group_name,
      members: [
          { id: groupData.creator_user_id, name: 'Creator (You)' },
          ...groupData.invited_user_ids.map(id => ({ id: id, name: `Invited User ${id.slice(-3)}` }))
      ],
      message: 'Group created successfully via mock.',
      onboarding_session_id: `mock_onboarding_sess_${Date.now()}`
    };
    // Update memberCount after members array is finalized
    newGroup.memberCount = newGroup.members.length;

    mockUserGroups.push(newGroup);
    console.log('MOCK new group created:', newGroup);
    return JSON.parse(JSON.stringify(newGroup));
  },

  inviteToGroup: async (groupId, userIdToInvite) => {
    console.log(`MOCK groupApi.inviteToGroup: inviting ${userIdToInvite} to group ${groupId}`);
    await new Promise(resolve => setTimeout(resolve, 500));
    const groupIndex = mockUserGroups.findIndex(g => g.id === groupId);
    if (groupIndex === -1) {
      throw new Error("Group not found for invite.");
    }
    if (mockUserGroups[groupIndex].members.length >= MAX_GROUP_MEMBERS) {
        throw new Error(`Group is full. Cannot invite more than ${MAX_GROUP_MEMBERS} members.`);
    }
    if (mockUserGroups[groupIndex].members.find(m => m.id === userIdToInvite)) {
        throw new Error(`User ${userIdToInvite} is already in the group.`);
    }

    // Add new member (mocked)
    mockUserGroups[groupIndex].members.push({ id: userIdToInvite, name: `Invited ${userIdToInvite.slice(-3)}` });
    mockUserGroups[groupIndex].memberCount = mockUserGroups[groupIndex].members.length;
    console.log(`MOCK User ${userIdToInvite} added to group ${groupId}. New members:`, mockUserGroups[groupIndex].members);
    return JSON.parse(JSON.stringify(mockUserGroups[groupIndex])); // Return updated group
  },

  leaveGroup: async (groupId, userIdLeaving) => {
    console.log(`MOCK groupApi.leaveGroup: user ${userIdLeaving} leaving group ${groupId}`);
    await new Promise(resolve => setTimeout(resolve, 500));
    const groupIndex = mockUserGroups.findIndex(g => g.id === groupId);
    if (groupIndex === -1) {
      throw new Error("Group not found to leave.");
    }

    const memberIndex = mockUserGroups[groupIndex].members.findIndex(m => m.id === userIdLeaving);
    if (memberIndex === -1) {
      // This shouldn't happen if user is in group, but good to check
      throw new Error(`User ${userIdLeaving} not found in group ${groupId}.`);
    }

    mockUserGroups[groupIndex].members.splice(memberIndex, 1);
    mockUserGroups[groupIndex].memberCount = mockUserGroups[groupIndex].members.length;

    // Optional: If group becomes empty, delete it? Or handle that logic elsewhere.
    if (mockUserGroups[groupIndex].members.length === 0) {
      // mockUserGroups.splice(groupIndex, 1);
      console.log(`MOCK Group ${groupId} is now empty after user ${userIdLeaving} left.`);
    } else {
      console.log(`MOCK User ${userIdLeaving} left group ${groupId}. Remaining members:`, mockUserGroups[groupIndex].members);
    }
    return { message: `Successfully left group ${groupId}` };
  },

  // TODO: Mock acceptInvitation, declineInvitation (These are now part of invitationApi)
};

// ===========================================
// Invitation API
// MOCKED IMPLEMENTATIONS
// ===========================================

// Assumes mockUserGroups and groupApi from above for acceptInvitation logic
// This mock state is for invitations *pending for the current user*.
let mockPendingInvitations = [
  { id: 'inv_001', groupId: 'group_002', groupName: 'Weekend Brunch Crew', inviterName: 'Charlie (user_004)' },
  { id: 'inv_002', groupId: 'group_newly_created', groupName: 'Fresh Group', inviterName: 'Some Creator' },
];

export const invitationApi = {
  getPendingInvitations: async () => {
    console.log('MOCK invitationApi.getPendingInvitations called');
    await new Promise(resolve => setTimeout(resolve, 400));
    // In a real app, this would fetch based on the authenticated user's ID.
    return [...mockPendingInvitations];
  },

  acceptInvitation: async (invitationId) => {
    console.log(`MOCK invitationApi.acceptInvitation called for invitation: ${invitationId}`);
    await new Promise(resolve => setTimeout(resolve, 600));

    const invIndex = mockPendingInvitations.findIndex(inv => inv.id === invitationId);
    if (invIndex === -1) {
      throw new Error("Invitation not found or already handled.");
    }

    const invitation = mockPendingInvitations[invIndex];

    // Simulate adding user to the group using groupApi's mock logic
    // This requires the current user's ID. Let's assume 'user_001_mock' is current user for mock.
    const currentUserId = 'user_001_mock'; // This should come from AuthContext in a real scenario

    try {
      // Find or create the group in mockUserGroups to add the member
      let groupToJoin = mockUserGroups.find(g => g.id === invitation.groupId);
      if (!groupToJoin) {
        // If group doesn't exist in mock (e.g. 'group_newly_created'), create a shell for it
        console.warn(`Mock group ${invitation.groupId} not found, creating a shell.`);
        groupToJoin = { id: invitation.groupId, name: invitation.groupName, members: [], memberCount: 0 };
        mockUserGroups.push(groupToJoin);
      }

      // Check if user already in group (idempotency)
      if (!groupToJoin.members.find(m => m.id === currentUserId)) {
        if (groupToJoin.members.length >= 3 /* MAX_GROUP_MEMBERS from groupApi mock */) {
            throw new Error("Group is full. Cannot accept invitation.");
        }
        groupToJoin.members.push({ id: currentUserId, name: 'Me (Accepted Invite)' });
        groupToJoin.memberCount = groupToJoin.members.length;
      } else {
        console.log(`User ${currentUserId} already in group ${invitation.groupId}`);
      }

      mockPendingInvitations.splice(invIndex, 1); // Remove invitation
      console.log(`MOCK Invitation ${invitationId} accepted. User added to group ${invitation.groupId}.`);
      return { message: "Invitation accepted successfully. You've been added to the group." };

    } catch (groupError) {
        console.error("Error during mock accept (adding to group):", groupError);
        // Don't remove invitation if adding to group failed, so user can see error / try again
        throw groupError; // Re-throw the error from groupApi (e.g. group full)
    }
  },

  declineInvitation: async (invitationId) => {
    console.log(`MOCK invitationApi.declineInvitation called for invitation: ${invitationId}`);
    await new Promise(resolve => setTimeout(resolve, 300));

    const invIndex = mockPendingInvitations.findIndex(inv => inv.id === invitationId);
    if (invIndex === -1) {
      throw new Error("Invitation not found or already handled.");
    }

    mockPendingInvitations.splice(invIndex, 1); // Remove invitation
    console.log(`MOCK Invitation ${invitationId} declined.`);
    return { message: "Invitation declined successfully." };
  },
};

// ===========================================
// Meal API
// MOCKED IMPLEMENTATIONS
// ===========================================

const mockMealSuggestionsData = {
  'group_001': [
    { id: 'meal_001', name: 'Spaghetti Carbonara', cuisine_type: 'Italian', prep_time: 30, difficulty: 'Medium', compatible_members_count: 2, total_members_in_group: 3, incompatible_reasons: ['Bob: Vegetarian'] },
    { id: 'meal_002', name: 'Chicken Tacos', cuisine_type: 'Mexican', prep_time: 45, difficulty: 'Easy', compatible_members_count: 3, total_members_in_group: 3, incompatible_reasons: [] },
    { id: 'meal_003', name: 'Vegetable Stir-fry', cuisine_type: 'Chinese', prep_time: 25, difficulty: 'Easy', compatible_members_count: 3, total_members_in_group: 3, incompatible_reasons: [] },
    { id: 'meal_004', name: 'Lentil Soup', cuisine_type: 'Indian', prep_time: 60, difficulty: 'Medium', compatible_members_count: 3, total_members_in_group: 3, incompatible_reasons: [] },
  ],
  'group_002': [
    { id: 'meal_005', name: 'Avocado Toast Deluxe', cuisine_type: 'Any', prep_time: 15, difficulty: 'Easy', compatible_members_count: 2, total_members_in_group: 2, incompatible_reasons: [] },
    { id: 'meal_006', name: 'Pancakes', cuisine_type: 'Any', prep_time: 30, difficulty: 'Easy', compatible_members_count: 1, total_members_in_group: 2, incompatible_reasons: ['Charlie: Gluten-free'] },
  ],
};

const mockMealDetailsData = {
    'meal_001': { id: 'meal_001', name: 'Spaghetti Carbonara', cuisine_type: 'Italian', prep_time: 30, difficulty: 'Medium', ingredients: ['Spaghetti', 'Eggs', 'Pancetta', 'Parmesan Cheese', 'Black Pepper'], recipe: '1. Cook spaghetti. 2. Fry pancetta. 3. Whisk eggs and cheese. 4. Combine all.', nutritional_info: 'Calories: 600, Protein: 30g', compatible_members_count: 2, total_members_in_group: 3, incompatible_reasons: ['Bob: Vegetarian'], group_compatibility_breakdown: [{member_id: 'user_001_mock', compatible: true}, {member_id: 'user_002', compatible: true, name: 'Alice'}, {member_id: 'user_003', compatible: false, name: 'Bob', reason: 'Vegetarian'}] },
    'meal_002': { id: 'meal_002', name: 'Chicken Tacos', cuisine_type: 'Mexican', prep_time: 45, difficulty: 'Easy', ingredients: ['Chicken', 'Tortillas', 'Salsa', 'Lettuce', 'Cheese'], recipe: 'Cook chicken, assemble tacos.', nutritional_info: 'Calories: 450', compatible_members_count: 3, total_members_in_group: 3, incompatible_reasons: [], group_compatibility_breakdown: [{member_id: 'user_001_mock', compatible: true}, {member_id: 'user_002', compatible: true, name: 'Alice'}, {member_id: 'user_003', compatible: true, name: 'Bob'}] },
};

export const mealApi = {
  getMealSuggestions: async (groupId, filters = {}) => {
    console.log(`MOCK mealApi.getMealSuggestions called for group ${groupId} with filters:`, filters);
    await new Promise(resolve => setTimeout(resolve, 600));
    let groupSuggestions = mockMealSuggestionsData[groupId] || [];
    if (filters.cuisine) {
      groupSuggestions = groupSuggestions.filter(meal => meal.cuisine_type.toLowerCase() === filters.cuisine.toLowerCase());
    }
    if (filters.difficulty) {
      groupSuggestions = groupSuggestions.filter(meal => meal.difficulty.toLowerCase() === filters.difficulty.toLowerCase());
    }
    return [...groupSuggestions];
  },
  getMealDetails: async (mealId) => {
    console.log(`MOCK mealApi.getMealDetails called for meal ${mealId}`);
    await new Promise(resolve => setTimeout(resolve, 400));
    const details = mockMealDetailsData[mealId];
    if (details) {
      return { ...details };
    }
    throw new Error(`Meal details not found for ID: ${mealId}`);
  },
};
