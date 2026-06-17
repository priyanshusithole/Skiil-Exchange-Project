// Initialize Firebase
if (typeof firebaseConfig === 'undefined') {
  console.error("Firebase configuration is missing! Please create a config.js file using config.example.js as a template.");
  document.addEventListener('DOMContentLoaded', () => {
    const appEl = document.getElementById('app');
    if (appEl) {
      appEl.innerHTML = `
        <div style="padding: 2rem; max-width: 600px; margin: 2rem auto; text-align: center; border: 3px solid #EF4444; border-radius: 12px; background-color: #FEF2F2; font-family: 'Inter', sans-serif;">
          <h2 style="color: #DC2626; font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem;">CONFIGURATION MISSING</h2>
          <p style="color: #991B1B; font-weight: 600; margin-bottom: 1.5rem;">The Firebase configuration file (<code>config.js</code>) is missing or could not be loaded.</p>
          <div style="text-align: left; background: white; padding: 1rem; border: 2px solid #000; border-radius: 6px; box-shadow: 2px 2px 0 #000;">
            <p style="margin: 0 0 0.5rem 0; font-weight: 700;">To fix this:</p>
            <ol style="margin: 0; padding-left: 1.25rem; font-size: 0.95rem; line-height: 1.5;">
              <li>Duplicate <code>config.example.js</code> and rename it to <code>config.js</code>.</li>
              <li>Open <code>config.js</code> and enter your Firebase API key and details.</li>
              <li>Refresh this page.</li>
            </ol>
          </div>
        </div>`;
    }
  });
  throw new Error("Firebase configuration (firebaseConfig) not found. See config.example.js.");
}

if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}
const database = firebase.database();

const initialState = {
  isLoggedIn: false,
  user: null,
  users: [],
  mySkills: [],
  marketplaceSkills: [],
  suggestedMatches: [],
  requests: [],
  feedbacks: [],
  upcomingSessions: [],
  publicRequests: []
};

let savedSession = null;
try {
  const raw = localStorage.getItem('skillExchangeSession');
  if (raw && raw !== 'undefined') {
    savedSession = JSON.parse(raw);
  }
} catch(e) {
  console.error("Failed to parse local session:", e);
}

window.store = {
  state: { ...initialState, ...(savedSession || {}) },
  save() {
    // Keep user's bio/skills updated in the global users array before saving
    if (this.state.user && this.state.users) {
      const dbIdx = this.state.users.findIndex(u => u.userId === this.state.user.userId);
      if (dbIdx > -1) {
        this.state.users[dbIdx].bio = this.state.user.bio;
        this.state.users[dbIdx].skillsOffered = this.state.user.skillsOffered;
        this.state.users[dbIdx].skillsWanted = this.state.user.skillsWanted;
      }
    }
    
    // Save personal session locally (login state)
    const sessionData = {
      isLoggedIn: this.state.isLoggedIn,
      user: this.state.user,
      mySkills: this.state.mySkills,
      requests: this.state.requests,
      upcomingSessions: this.state.upcomingSessions
    };
    localStorage.setItem('skillExchangeSession', JSON.stringify(sessionData));
    
    // Sync global data to Firebase
    database.ref('/').set({
      users: this.state.users || [],
      marketplaceSkills: this.state.marketplaceSkills || [],
      publicRequests: this.state.publicRequests || [],
      feedbacks: this.state.feedbacks || []
    }).catch(error => {
      console.error("Firebase Sync Failed:", error);
      alert("Firebase Sync Failed: " + error.message + "\nYour changes were not saved to the backend database.");
    });
    
    window.router(); // Re-render current view on state change
  },
  reset() {
    this.state = JSON.parse(JSON.stringify(initialState));
    this.save();
  },
  login(email, password) {
    email = email.toLowerCase().trim();
    if(!this.state.users) this.state.users = [];
    
    // Simulate password hashing for authentication check
    const hashedPassword = btoa(password); 
    const existingUser = this.state.users.find(u => u.email.toLowerCase() === email && u.password === hashedPassword);
    if (!existingUser) {
      alert("Invalid email or password. Please try again.");
      return;
    }
    
    this.state.user = {
      userId: existingUser.userId,
      name: existingUser.name,
      major: 'Student',
      email: existingUser.email,
      bio: existingUser.bio || '',
      skillsOffered: existingUser.skillsOffered || [],
      skillsWanted: existingUser.skillsWanted || [],
      joinDate: new Date(existingUser.createdAt).toLocaleDateString(),
      initials: existingUser.name.substring(0,2).toUpperCase()
    };
    this.state.isLoggedIn = true;
    this.save();
    window.location.hash = '#/dashboard';
  },
  signup(name, email, password) {
    email = email.toLowerCase().trim();
    if(!this.state.users) this.state.users = [];
    const existingUser = this.state.users.find(u => u.email.toLowerCase() === email);
    if (existingUser) {
      alert("An account with this email already exists. Please log in.");
      return;
    }
    
    const userId = 'usr_' + Date.now();
    const hashedPassword = btoa(password); // Simulated hashing
    const createdAt = new Date().toISOString();
    
    // Push new user following exact database model
    this.state.users.push({
      userId: userId,
      name: name,
      email: email,
      password: hashedPassword,
      bio: '',
      skillsOffered: [],
      skillsWanted: [],
      createdAt: createdAt
    });
    
    this.state.user = {
      userId: userId,
      name: name,
      major: 'Student',
      email: email,
      bio: '',
      skillsOffered: [],
      skillsWanted: [],
      joinDate: new Date(createdAt).toLocaleDateString(),
      initials: name.substring(0,2).toUpperCase()
    };
    this.state.isLoggedIn = true;
    this.save();
    window.location.hash = '#/dashboard';
  },
  logout() {
    this.state.isLoggedIn = false;
    this.state.user = null; // Clear the active session
    this.save();
    window.location.hash = '#/login';
  },
  addMySkill(skill) {
    const newSkill = { id: Date.now(), ...skill };
    
    if(!this.state.user.skillsOffered) this.state.user.skillsOffered = [];
    if(!this.state.user.skillsWanted) this.state.user.skillsWanted = [];
    
    if (skill.type.includes('Offer')) {
      this.state.user.skillsOffered.unshift(newSkill);
      // Publish to global marketplace
      if(!this.state.marketplaceSkills) this.state.marketplaceSkills = [];
      this.state.marketplaceSkills.unshift({
        id: newSkill.id,
        providerId: this.state.user.userId,
        providerName: this.state.user.name,
        skillName: skill.name,
        category: skill.category,
        type: skill.type,
        desc: skill.desc,
        color: '#10B981' // Success Green
      });
    } else {
      this.state.user.skillsWanted.unshift(newSkill);
    }
    this.save();
  },
  deleteMySkill(id) {
    // Access control: Ensure user owns the marketplace skill before deleting
    if (this.state.marketplaceSkills) {
      const mkSkill = this.state.marketplaceSkills.find(s => s.id === id);
      if (mkSkill && mkSkill.providerId !== this.state.user.userId) {
         console.error("Unauthorized: Cannot delete a skill you do not own.");
         return; // Block deletion
      }
      // Authorized: Remove from global marketplace
      this.state.marketplaceSkills = this.state.marketplaceSkills.filter(s => s.id !== id);
    }

    if (this.state.user.skillsOffered) this.state.user.skillsOffered = this.state.user.skillsOffered.filter(s => s.id !== id);
    if (this.state.user.skillsWanted) this.state.user.skillsWanted = this.state.user.skillsWanted.filter(s => s.id !== id);
    this.save();
  },
  addRequest(req) {
    this.state.requests.unshift({ id: Date.now(), ...req });
    this.save();
  },
  resolveRequest(id, status) {
    const req = this.state.requests.find(r => r.id === id);
    if(req) {
      req.status = status;
      req.isPast = true;
      req.time = 'Just Now';
      this.save();
    }
  },
  addFeedback(feedback) {
    this.state.feedbacks.unshift({ id: Date.now(), ...feedback });
    this.save();
  },
  createPublicRequest(req) {
    const newRequest = {
      requestId: 'req_' + Date.now(),
      userId: this.state.user.userId,
      userName: this.state.user.name,
      skillNeeded: req.needed,
      skillOffered: req.offered,
      description: req.desc + (req.time ? ' | Preferred time: ' + req.time : ''),
      status: 'open',
      createdAt: new Date().toISOString()
    };
    if (!this.state.publicRequests) this.state.publicRequests = [];
    this.state.publicRequests.unshift(newRequest);
    this.state.mySkills.unshift({
      id: Date.now(),
      name: req.needed,
      category: 'Requested',
      type: 'Looking to Learn',
      desc: req.desc
    });
    this.save();
    window.location.hash = '#/browse-skills';
  },
  updateProfile(data) {
    if (data.name) {
      this.state.user.name = data.name;
      this.state.user.initials = data.name.substring(0,2).toUpperCase();
      
      // Update users database table exactly
      const dbIdx = this.state.users.findIndex(u => u.userId === this.state.user.userId);
      if (dbIdx > -1) {
         this.state.users[dbIdx].name = data.name;
      }
    }
    if (data.bio !== undefined) {
      this.state.user.bio = data.bio;
    }
    this.save();
  },
  acceptPublicRequest(requestId) {
    const req = this.state.publicRequests.find(r => r.requestId === requestId);
    if(req && req.userId !== this.state.user.userId) {
      req.status = 'accepted';
      req.acceptedBy = this.state.user.userId;
      req.acceptedByName = this.state.user.name;
      this.save();
    }
  },
  closePublicRequest(requestId) {
    const req = this.state.publicRequests.find(r => r.requestId === requestId);
    if(req && req.userId === this.state.user.userId) {
      req.status = 'closed';
      this.save();
    }
  }
};

// Sync from Firebase
database.ref('/').on('value', (snapshot) => {
  const data = snapshot.val();
  if (data) {
    window.store.state.users = data.users || [];
    window.store.state.marketplaceSkills = data.marketplaceSkills || [];
    window.store.state.publicRequests = data.publicRequests || [];
    window.store.state.feedbacks = data.feedbacks || [];
    window.router();
  } else {
    // If Firebase is completely empty, initialize it with any legacy local state we had
    let legacyState = null;
    try { legacyState = JSON.parse(localStorage.getItem('skillExchangeState')); } catch(e){}
    if(legacyState && legacyState.users && legacyState.users.length > 0) {
      window.store.state.users = legacyState.users || [];
      window.store.state.marketplaceSkills = legacyState.marketplaceSkills || [];
      window.store.state.publicRequests = legacyState.publicRequests || [];
      window.store.state.feedbacks = legacyState.feedbacks || [];
      window.store.save(); // Pushes legacy to Firebase
    }
  }
}, (error) => {
  console.error("Firebase Read Error:", error);
  alert("Firebase Connection Error: " + error.message + "\nPlease make sure your Firebase Realtime Database Security Rules are set to public.");
});

const views = {};

views.login = (state) => `
<div style="display: flex; min-height: 100vh; font-family: 'Inter', sans-serif; position: relative; overflow: hidden; background-color: #FDF0D5;">
  <div style="position: absolute; inset: 0; background-image: radial-gradient(#EACD9B 25%, transparent 25%), radial-gradient(#EACD9B 25%, transparent 25%); background-position: 0 0, 10px 10px; background-size: 20px 20px; z-index: 0;"></div>
  
  <div class="split-left" style="flex: 1; position: relative; z-index: 1; display: none;">
    <img src="login_bg.png?v=2" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: left center; -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,1) 60%, rgba(0,0,0,0) 100%); mask-image: linear-gradient(to right, rgba(0,0,0,1) 60%, rgba(0,0,0,0) 100%);" alt="Skill Exchange">
    <div style="position: absolute; top: 1.5rem; left: 1.5rem; background: rgba(250, 237, 223, 0.95); border: 3px solid #000; border-radius: 8px; padding: 1rem; box-shadow: 3px 3px 0 #000; max-width: 280px;">
      <h1 style="font-size: 1.35rem; font-weight: 900; margin-bottom: 0.35rem; text-transform: uppercase; color: #F59E0B; text-shadow: 1px 1px 0 #000; line-height: 1.1;">Student Skill Exchange</h1>
      <p style="font-weight: 800; color: #000; margin: 0; font-size: 0.85rem; text-transform: uppercase;">Trade knowledge. Grow together.</p>
    </div>
  </div>
  
  <div style="flex: 1; display: flex; align-items: center; justify-content: center; padding: 2rem; max-width: 600px; z-index: 1;">
    <div style="width: 100%; max-width: 450px; background: rgba(255, 255, 255, 0.25); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.6); border-radius: 16px; padding: 2.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
      <h2 style="font-size: 2.5rem; font-weight: 900; color: #F59E0B; margin-bottom: 0.5rem; text-transform: uppercase; text-shadow: 1px 1px 0 #000;">SECURE PORTAL</h2>
      <p style="font-weight: 600; margin-bottom: 2rem; color: #4B5563;">Enter your credentials to access the student dashboard</p>
      
      <form onsubmit="event.preventDefault(); window.store.login(document.getElementById('email').value, document.getElementById('password').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="email" style="font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #000;">University Email</label>
          <input type="email" id="email" class="input-field" placeholder="student@university.edu" required style="width: 100%; padding: 0.875rem; font-size: 1rem; font-weight: 600; background: rgba(255, 255, 255, 0.4); border: 3px solid #000; border-radius: 6px; outline: none; box-shadow: 2px 2px 0 #000; box-sizing: border-box; color: #000;">
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="password" style="font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #000;">Password</label>
          <input type="password" id="password" class="input-field" placeholder="••••••••" required style="width: 100%; padding: 0.875rem; font-size: 1rem; font-weight: 600; background: rgba(255, 255, 255, 0.4); border: 3px solid #000; border-radius: 6px; outline: none; box-shadow: 2px 2px 0 #000; box-sizing: border-box; color: #000;">
        </div>
        <button type="submit" class="btn" style="width: 100%; padding: 1rem; font-size: 1.1rem; font-weight: 900; background-color: #F59E0B; color: #000; border: 3px solid #000; border-radius: 6px; cursor: pointer; text-transform: uppercase; margin-top: 1rem; box-shadow: 3px 3px 0 #000; transition: transform 0.1s;">Log In</button>
      </form>
      <p style="text-align: center; margin-top: 2rem; font-size: 0.95rem; font-weight: 600;">
        Don't have an account? <a href="#/signup" style="color: #F59E0B; font-weight: 900; text-decoration: none; text-shadow: 0.5px 0.5px 0 #000;">SIGN UP</a>
      </p>
    </div>
  </div>
</div>`;

views.signup = (state) => `
<div style="display: flex; min-height: 100vh; font-family: 'Inter', sans-serif; position: relative; overflow: hidden; background-color: #FDF0D5;">
  <div style="position: absolute; inset: 0; background-image: radial-gradient(#EACD9B 25%, transparent 25%), radial-gradient(#EACD9B 25%, transparent 25%); background-position: 0 0, 10px 10px; background-size: 20px 20px; z-index: 0;"></div>
  
  <div class="split-left" style="flex: 1; position: relative; z-index: 1; display: none;">
    <img src="login_bg.png?v=2" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: left center; -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,1) 60%, rgba(0,0,0,0) 100%); mask-image: linear-gradient(to right, rgba(0,0,0,1) 60%, rgba(0,0,0,0) 100%);" alt="Skill Exchange">
    <div style="position: absolute; top: 1.5rem; left: 1.5rem; background: rgba(250, 237, 223, 0.95); border: 3px solid #000; border-radius: 8px; padding: 1rem; box-shadow: 3px 3px 0 #000; max-width: 280px;">
      <h1 style="font-size: 1.35rem; font-weight: 900; margin-bottom: 0.35rem; text-transform: uppercase; color: #F59E0B; text-shadow: 1px 1px 0 #000; line-height: 1.1;">Student Skill Exchange</h1>
      <p style="font-weight: 800; color: #000; margin: 0; font-size: 0.85rem; text-transform: uppercase;">Join the community today.</p>
    </div>
  </div>
  
  <div style="flex: 1; display: flex; align-items: center; justify-content: center; padding: 2rem; max-width: 600px; z-index: 1;">
    <div style="width: 100%; max-width: 450px; background: rgba(255, 255, 255, 0.25); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.6); border-radius: 16px; padding: 2.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
      <h2 style="font-size: 2.5rem; font-weight: 900; color: #F59E0B; margin-bottom: 0.5rem; text-transform: uppercase; text-shadow: 1px 1px 0 #000;">NEW ACCOUNT</h2>
      <p style="font-weight: 600; margin-bottom: 2rem; color: #4B5563;">Enter your details to join the marketplace</p>
      
      <form onsubmit="event.preventDefault(); window.store.signup(document.getElementById('fullname').value, document.getElementById('email').value, document.getElementById('password').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="fullname" style="font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #000;">Full Name</label>
          <input type="text" id="fullname" class="input-field" placeholder="e.g. John Doe" required style="width: 100%; padding: 0.875rem; font-size: 1rem; font-weight: 600; background: rgba(255, 255, 255, 0.4); border: 3px solid #000; border-radius: 6px; outline: none; box-shadow: 2px 2px 0 #000; box-sizing: border-box; color: #000;">
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="email" style="font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #000;">University Email</label>
          <input type="email" id="email" class="input-field" placeholder="student@university.edu" required style="width: 100%; padding: 0.875rem; font-size: 1rem; font-weight: 600; background: rgba(255, 255, 255, 0.4); border: 3px solid #000; border-radius: 6px; outline: none; box-shadow: 2px 2px 0 #000; box-sizing: border-box; color: #000;">
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="password" style="font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #000;">Password</label>
          <input type="password" id="password" class="input-field" placeholder="Create a password" required style="width: 100%; padding: 0.875rem; font-size: 1rem; font-weight: 600; background: rgba(255, 255, 255, 0.4); border: 3px solid #000; border-radius: 6px; outline: none; box-shadow: 2px 2px 0 #000; box-sizing: border-box; color: #000;">
        </div>
        <button type="submit" class="btn" style="width: 100%; padding: 1rem; font-size: 1.1rem; font-weight: 900; background-color: #F59E0B; color: #000; border: 3px solid #000; border-radius: 6px; cursor: pointer; text-transform: uppercase; margin-top: 1rem; box-shadow: 3px 3px 0 #000; transition: transform 0.1s;">Sign Up</button>
      </form>
      <p style="text-align: center; margin-top: 2rem; font-size: 0.95rem; font-weight: 600;">
        Already have an account? <a href="#/login" style="color: #F59E0B; font-weight: 900; text-decoration: none; text-shadow: 0.5px 0.5px 0 #000;">LOG IN</a>
      </p>
    </div>
  </div>
</div>`;

views.dashboard = (state) => `
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; border-bottom: var(--border-width) solid var(--color-border); padding-bottom: 1rem;">
  <div>
    <h2 style="font-size: 2rem; margin-bottom: 0.25rem;">Dashboard</h2>
    <p style="color: #4B5563; font-size: 1rem; margin: 0;">Welcome back, ${state.user.name.split(' ')[0]}! Here's what's happening today.</p>
  </div>
  <div style="display: flex; gap: 1rem;">
    <button class="btn btn-secondary" onclick="openModal('createRequest')">Create Request</button>
    <button class="btn btn-primary" onclick="window.location.hash='#/my-skills'; setTimeout(()=>document.getElementById('skill-name').focus(), 100)">Offer a Skill</button>
  </div>
</div>

<div class="card-grid" id="browse-grid">
  <div class="card" style="border-color: var(--color-primary);">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge badge-primary">Next Session</span>
    </div>
    ${state.upcomingSessions.length > 0 ? `
    <h3 class="card-title" style="font-size: 1.2rem;">${state.upcomingSessions[0].title}</h3>
    <p class="card-content">Study session with ${state.upcomingSessions[0].partner}.<br><strong>${state.upcomingSessions[0].time}</strong></p>
    <div class="card-actions">
      <button class="btn btn-primary" style="flex: 1;" onclick="alert('Launching Zoom session...')">Join Link</button>
    </div>
    ` : '<p class="card-content" style="margin-top:1rem; color:#4B5563;">No upcoming sessions scheduled.</p>'}
  </div>

  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge badge-neutral">New Match</span>
    </div>
    ${state.suggestedMatches.length > 0 ? `
    <h3 class="card-title" style="font-size: 1.2rem;">${state.suggestedMatches[0].teaching}</h3>
    <p class="card-content">${state.suggestedMatches[0].name} wants to trade ${state.suggestedMatches[0].wanting} for your skills.</p>
    <div class="card-actions">
      <button class="btn btn-primary" style="flex: 1;" onclick="window.location.hash='#/requests'">View Request</button>
    </div>
    ` : '<p class="card-content" style="margin-top:1rem; color:#4B5563;">No new matches available yet.</p>'}
  </div>
  
  <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge badge-success">Active</span>
    </div>
    <h3 class="card-title" style="font-size: 1.2rem;">Your Stats</h3>
    <ul style="list-style: none; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; color: #4B5563; margin-top: 0.5rem;">
      <li><strong>${(state.user.skillsOffered || []).length}</strong> Active Offers</li>
      <li><strong>${state.requests.filter(r=>r.status==='Pending').length}</strong> Pending Requests</li>
      <li><strong>0</strong> Hours Exchanged</li>
    </ul>
  </div>
</div>

<div style="margin-top: 3.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem;">
    <h3 style="font-size: 1.75rem; margin: 0;">Suggested Matches</h3>
    <span class="badge badge-primary" style="padding: 0.4rem 0.8rem;">High Compatibility</span>
  </div>
  
  <div class="card-grid">
    ${state.suggestedMatches.length === 0 ? '<p style="color: #4B5563; font-style: italic;">No suggested matches available yet.</p>' : ''}
    ${state.suggestedMatches.map(match => `
    <div class="card card-clickable" ${match.id === 1 ? 'style="border-color: var(--color-primary);"' : ''} onclick="openModal('profile', '${match.name}', '${match.major}')">
      <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
        <div style="width: 48px; height: 48px; border-radius: 50%; background-color: ${match.color}; border: var(--border-width) solid var(--color-border);"></div>
        <div>
          <h3 class="card-title" style="font-size: 1.2rem; margin-bottom: 0.1rem;">${match.name}</h3>
          <span style="font-size: 0.9rem; color: #4B5563;">${match.major}</span>
        </div>
      </div>
      <div style="display: flex; flex-direction: column; gap: 1rem; flex: 1;">
        <div>
          <p style="margin: 0 0 0.4rem 0; font-size: 0.95rem; color: #4B5563; font-weight: 600;">Can teach you:</p>
          <span class="badge badge-success" style="font-size: 0.9rem;">${match.teaching}</span>
        </div>
        <div style="border-top: 2px dashed var(--color-border); margin: 0.25rem 0;"></div>
        <div>
          <p style="margin: 0 0 0.4rem 0; font-size: 0.95rem; color: #4B5563; font-weight: 600;">Wants to learn:</p>
          <span class="badge badge-primary" style="font-size: 0.9rem;">${match.wanting}</span>
        </div>
      </div>
      <div class="card-actions" style="margin-top: 1.5rem;">
        <button class="btn btn-primary" style="flex: 1; padding: 0.75rem;" onclick="event.stopPropagation(); window.mockSendRequest('${match.name}')">Send Request</button>
      </div>
    </div>
    `).join('')}
  </div>
</div>`;

views['browse-skills'] = (state) => `
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; border-bottom: var(--border-width) solid var(--color-border); padding-bottom: 1rem;">
  <div>
    <h2 style="font-size: 2rem; margin-bottom: 0.25rem;">Browse Skills</h2>
    <p style="color: #4B5563; font-size: 1rem; margin: 0;">Find students offering skills you want or looking for skills you have.</p>
  </div>
  <div style="display: flex; gap: 1rem; width: 100%; max-width: 600px;">
      <input type="text" id="skill-search" class="input-field" placeholder="Search skills, users, or keywords..." style="margin-bottom: 0; flex: 1;" oninput="window.filterSkills()">
      <select id="skill-category" class="input-field" style="padding: 0.5rem; font-size: 0.9rem; margin-bottom: 0; width: 150px;" onchange="window.filterSkills()">
        <option>All Categories</option>
        <option>Programming</option>
        <option>Languages</option>
        <option>Design</option>
        <option>Academics</option>
      </select>
  </div>
</div>

<div class="card-grid">
  ${(state.marketplaceSkills.length === 0 && (!state.publicRequests || state.publicRequests.length === 0)) ? '<p style="color: #4B5563; font-style: italic;">No skills or requests available in the marketplace yet.</p>' : ''}
  
  ${(state.publicRequests || []).filter(req => req.status === 'open').map(req => `
  <div class="card card-clickable" data-category="All Categories" ${req.userId === state.user.userId ? 'style="border-color: var(--color-primary); background-color: #FFF7ED;"' : ''} onclick="openModal('skill', '${req.userName}', '${req.skillNeeded}', 'Looking to Learn')">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge" style="background-color: ${req.userId === state.user.userId ? 'var(--color-primary)' : '#3B82F6'}; color: white;">${req.userId === state.user.userId ? 'Your Request' : 'Looking to Learn'}</span>
      <span style="font-weight: bold; font-size: 0.8rem; color: #4B5563;">${new Date(req.createdAt).toLocaleDateString()}</span>
    </div>
    <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.5rem;">${req.skillNeeded}</h3>
    <p class="card-content" style="margin-bottom: 0.5rem; flex: 1;">${req.description}</p>
    <p style="font-size: 0.9rem; margin-bottom: 0.5rem; color: #4B5563;"><strong>Offering:</strong> ${req.skillOffered}</p>
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; margin-top: 1rem;">
      <div style="width: 28px; height: 28px; border-radius: 50%; background-color: #A78BFA; border: var(--border-width) solid var(--color-border);"></div>
      <span style="font-size: 0.95rem; font-weight: 600;">${req.userId === state.user.userId ? 'You' : req.userName}</span>
    </div>
    <div class="card-actions">
      ${req.userId === state.user.userId 
        ? `<button class="btn btn-secondary" style="flex: 1;" onclick="event.stopPropagation(); window.location.hash='#/requests'">Manage</button>`
        : `<button class="btn btn-primary" style="flex: 1;" onclick="event.stopPropagation(); window.mockSendRequest('${req.userName}')">Offer Skill</button>`}
    </div>
  </div>
  `).join('')}

  ${state.marketplaceSkills.map(skill => `
  <div class="card card-clickable" data-category="${skill.category}" ${skill.providerId === state.user.userId ? 'style="border-color: var(--color-primary); background-color: #FFF7ED;"' : ''} onclick="openModal('skill', '${skill.providerName}', '${skill.skillName}', '${skill.type}')">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge" style="background-color: ${skill.providerId === state.user.userId ? 'var(--color-primary)' : (skill.type.includes('Offer') ? 'var(--color-success)' : 'var(--color-primary)')}; color: white;">${skill.providerId === state.user.userId ? 'Your Skill' : skill.type}</span>
      <span style="font-weight: bold; font-size: 0.9rem; color: #4B5563; border: var(--border-width) solid var(--color-border); padding: 0.2rem 0.5rem; border-radius: 4px; background: var(--color-bg);">${skill.category}</span>
    </div>
    <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.5rem;">${skill.skillName}</h3>
    <p class="card-content" style="margin-bottom: 0.5rem; flex: 1;">${skill.desc}</p>
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; margin-top: 1rem;">
      <div style="width: 28px; height: 28px; border-radius: 50%; background-color: ${skill.color}; border: var(--border-width) solid var(--color-border);"></div>
      <span style="font-size: 0.95rem; font-weight: 600;">${skill.providerName}</span>
    </div>
    <div class="card-actions">
      ${skill.providerId === state.user.userId 
        ? `<button class="btn btn-secondary" style="flex: 1;" onclick="event.stopPropagation(); window.location.hash='#/my-skills'">Manage</button>`
        : `<button class="btn btn-primary" style="flex: 1;" onclick="event.stopPropagation(); window.mockSendRequest('${skill.providerName}')">${skill.type.includes('Offer') ? 'Request Trade' : 'Offer Skill'}</button>`}
    </div>
  </div>
  `).join('')}
</div>`;

views['my-skills'] = (state) => `
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; border-bottom: var(--border-width) solid var(--color-border); padding-bottom: 1rem;">
  <div>
    <h2 style="font-size: 2rem; margin-bottom: 0.25rem;">My Skills</h2>
    <p style="color: #4B5563; font-size: 1rem; margin: 0;">Manage the skills you are offering or looking to learn.</p>
  </div>
</div>

<div style="display: grid; grid-template-columns: minmax(300px, 350px) 1fr; gap: 2.5rem; align-items: start;">
  <div class="card" style="position: sticky; top: 2rem;">
    <h3 class="card-title" style="margin-bottom: 1.5rem; font-size: 1.5rem;">Add New Skill</h3>
    <form onsubmit="event.preventDefault(); window.store.addMySkill({ name: document.getElementById('skill-name').value, category: document.getElementById('category').options[document.getElementById('category').selectedIndex].text, type: document.getElementById('type').options[document.getElementById('type').selectedIndex].text, desc: document.getElementById('description').value }); this.reset();" style="display: flex; flex-direction: column; gap: 1.25rem;">
      <div class="input-group" style="margin-bottom: 0;">
        <label class="input-label" for="skill-name">Skill Name</label>
        <input type="text" id="skill-name" class="input-field" placeholder="e.g. Python Programming" required>
      </div>
      <div class="input-group" style="margin-bottom: 0;">
        <label class="input-label" for="category">Category</label>
        <select id="category" class="input-field" required>
          <option value="">Select category...</option>
          <option value="programming">Programming</option>
          <option value="languages">Languages</option>
          <option value="design">Design</option>
          <option value="academics">Academics</option>
        </select>
      </div>
      <div class="input-group" style="margin-bottom: 0;">
        <label class="input-label" for="type">Type</label>
        <select id="type" class="input-field" required>
          <option value="offer">Offering</option>
          <option value="learn">Looking to Learn</option>
          <option value="collab">Project Collaboration</option>
          <option value="study">Study Partner Needed</option>
          <option value="mentor">Mentorship Offered</option>
          <option value="mentee">Seeking Mentorship</option>
        </select>
      </div>
      <div class="input-group" style="margin-bottom: 0;">
        <label class="input-label" for="description">Description</label>
        <textarea id="description" class="input-field" rows="4" placeholder="Briefly describe your experience or what you need..." required></textarea>
      </div>
      <button type="submit" class="btn btn-primary" style="margin-top: 0.5rem; width: 100%; font-size: 1.1rem; padding: 0.875rem;">Save Skill</button>
    </form>
  </div>

  <div>
    <h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">Your Existing Skills</h3>
    <div class="card-grid" style="grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));">
      ${(!state.user.skillsOffered?.length && !state.user.skillsWanted?.length) ? '<p style="color: #4B5563;">No skills added yet.</p>' : [...(state.user.skillsOffered||[]), ...(state.user.skillsWanted||[])].map(skill => `
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <span class="badge" style="background-color: ${skill.providerId === state.user.userId ? 'var(--color-primary)' : (skill.type.includes('Offer') ? 'var(--color-success)' : 'var(--color-primary)')}; color: white;">${skill.providerId === state.user.userId ? 'Your Skill' : skill.type}</span>
          <span style="font-weight: bold; font-size: 0.9rem; color: #4B5563; border: var(--border-width) solid var(--color-border); padding: 0.2rem 0.5rem; border-radius: 4px; background: var(--color-bg);">${skill.category}</span>
        </div>
        <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.5rem;">${skill.name}</h3>
        <p class="card-content" style="margin-bottom: 1.5rem; flex: 1;">${skill.desc}</p>
        <div class="card-actions" style="margin-top: auto; display: flex; gap: 0.5rem;">
          <button class="btn btn-secondary" style="flex: 1; padding: 0.5rem; font-size: 0.95rem;" onclick="alert('Opening edit modal...')">Edit</button>
          <button class="btn btn-danger" style="flex: 1; padding: 0.5rem; font-size: 0.95rem;" onclick="if(confirm('Are you sure you want to delete this skill?')) { window.store.deleteMySkill(${skill.id}); }">Delete</button>
        </div>
      </div>
      `).join('')}
    </div>
  </div>
</div>`;

views.requests = (state) => `
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; border-bottom: var(--border-width) solid var(--color-border); padding-bottom: 1rem;">
  <div>
    <h2 style="font-size: 2rem; margin-bottom: 0.25rem;">Exchange Requests</h2>
    <p style="color: #4B5563; font-size: 1rem; margin: 0;">Manage your posted requests and explore opportunities from others.</p>
  </div>
  <div style="display: flex; gap: 1rem;">
    <button class="btn btn-primary" onclick="openModal('createRequest')">Create Request</button>
  </div>
</div>

<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">My Exchanges</h3>
<div class="card-grid" style="margin-bottom: 3rem;">
  ${(!state.publicRequests || state.publicRequests.filter(r => r.status === 'accepted' && (r.userId === state.user.userId || r.acceptedBy === state.user.userId)).length === 0) ? '<p style="color: #4B5563; font-style: italic;">You have no active exchanges.</p>' : ''}
  ${(state.publicRequests || []).filter(r => r.status === 'accepted' && (r.userId === state.user.userId || r.acceptedBy === state.user.userId)).map(req => `
  <div class="card" style="border-color: var(--color-success); background-color: #F8FAFFC0;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge badge-success">Active Exchange</span>
      <span style="font-weight: bold; font-size: 0.8rem; color: #4B5563;">Matched</span>
    </div>
    <div style="margin-top: 1rem;">
      <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
        <span style="font-size: 0.95rem; font-weight: 600;">Partner: ${req.userId === state.user.userId ? req.acceptedByName : req.userName}</span>
      </div>
      <p style="margin: 0; font-size: 0.95rem; color: #4B5563;">Skills involved:</p>
      <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.2rem;">${req.skillNeeded} ↔ ${req.skillOffered}</h3>
    </div>
    <div class="card-actions" style="margin-top: auto; display: flex; gap: 0.5rem; padding-top: 1rem;">
      <button class="btn btn-primary" style="flex: 1; padding: 0.5rem; font-size: 0.95rem;" onclick="alert('Launching Chat...')">Message</button>
      <button class="btn btn-secondary" style="flex: 1; padding: 0.5rem; font-size: 0.95rem;" onclick="alert('Marking as Complete...')">Complete</button>
    </div>
  </div>
  `).join('')}
</div>

<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">My Posted Requests</h3>
<div class="card-grid" style="margin-bottom: 3rem;">
  ${(!state.publicRequests || state.publicRequests.filter(r => r.userId === state.user.userId && r.status !== 'accepted').length === 0) ? '<p style="color: #4B5563; font-style: italic;">You have no posted requests.</p>' : ''}
  ${(state.publicRequests || []).filter(r => r.userId === state.user.userId && r.status !== 'accepted').map(req => `
  <div class="card" style="opacity: ${req.status === 'closed' ? '0.6' : '1'}; border-color: ${req.status === 'closed' ? '#E5E7EB' : 'var(--color-border)'};">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge" style="background-color: ${req.status === 'open' ? 'var(--color-primary)' : '#9CA3AF'}; color: white;">${req.status.toUpperCase()}</span>
      <span style="font-weight: bold; font-size: 0.8rem; color: #4B5563;">${new Date(req.createdAt).toLocaleDateString()}</span>
    </div>
    <div style="margin-top: 1rem;">
      <p style="margin: 0; font-size: 0.95rem; color: #4B5563;">Skill needed:</p>
      <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.2rem; color: ${req.status === 'closed' ? '#9CA3AF' : 'var(--color-text)'};">${req.skillNeeded}</h3>
      <div style="margin: 1rem 0; border-top: 2px dashed var(--color-border);"></div>
      <p style="margin: 0; font-size: 0.95rem; color: #4B5563;">Offering in return:</p>
      <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.2rem; color: ${req.status === 'closed' ? '#9CA3AF' : 'var(--color-success)'};">${req.skillOffered}</h3>
    </div>
    <p class="card-content" style="margin-top: 1rem;">${req.description}</p>
    <div class="card-actions" style="margin-top: auto; display: flex; gap: 0.5rem; padding-top: 1rem;">
      ${req.status === 'open' ? `
      <button class="btn btn-secondary" style="flex: 1; padding: 0.5rem; font-size: 0.95rem;" onclick="alert('Editing request...')">Edit</button>
      <button class="btn btn-danger" style="flex: 1; padding: 0.5rem; font-size: 0.95rem;" onclick="if(confirm('Are you sure you want to close this request?')) window.store.closePublicRequest('${req.requestId}')">Close</button>
      ` : `
      <button class="btn btn-secondary" style="flex: 1; padding: 0.5rem; font-size: 0.95rem;" disabled>Request Closed</button>
      `}
    </div>
  </div>
  `).join('')}
</div>

<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">Available Requests</h3>
<div class="card-grid">
  ${(!state.publicRequests || state.publicRequests.filter(r => r.userId !== state.user.userId && (r.status === 'open' || (r.status === 'accepted' && r.acceptedBy !== state.user.userId))).length === 0) ? '<p style="color: #4B5563; font-style: italic;">No open requests available from other students.</p>' : ''}
  ${(state.publicRequests || []).filter(r => r.userId !== state.user.userId && (r.status === 'open' || (r.status === 'accepted' && r.acceptedBy !== state.user.userId))).map(req => `
  <div class="card" style="border-color: ${req.status === 'accepted' ? 'var(--color-success)' : '#A78BFA'}; opacity: ${req.status === 'accepted' ? '0.85' : '1'};">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge" style="background-color: ${req.status === 'accepted' ? 'var(--color-success)' : '#A78BFA'}; color: white;">${req.status === 'accepted' ? 'Accepted' : 'Open Request'}</span>
      <span style="font-weight: bold; font-size: 0.8rem; color: #4B5563;">${new Date(req.createdAt).toLocaleDateString()}</span>
    </div>
    <div style="margin-top: 1rem;">
      <p style="margin: 0; font-size: 0.95rem; color: #4B5563;">They need:</p>
      <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.2rem;">${req.skillNeeded}</h3>
      <div style="margin: 1rem 0; border-top: 2px dashed var(--color-border);"></div>
      <p style="margin: 0; font-size: 0.95rem; color: #4B5563;">They are offering:</p>
      <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.2rem;">${req.skillOffered}</h3>
    </div>
    <p class="card-content" style="margin-top: 1rem; margin-bottom: 1.5rem;">${req.description}</p>
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
      <div style="width: 28px; height: 28px; border-radius: 50%; background-color: ${req.status === 'accepted' ? 'var(--color-success)' : '#A78BFA'}; border: var(--border-width) solid var(--color-border);"></div>
      <span style="font-size: 0.95rem; font-weight: 600;">${req.userName}</span>
    </div>
    <div class="card-actions" style="margin-top: auto; display: flex;">
      ${req.status === 'open' 
        ? `<button class="btn btn-primary" style="flex: 1; padding: 0.75rem;" onclick="window.store.acceptPublicRequest('${req.requestId}')">Accept Request</button>`
        : `<button class="btn btn-secondary" style="flex: 1; padding: 0.75rem;" disabled>Accepted by ${req.acceptedByName || 'someone'}</button>`
      }
    </div>
  </div>
  `).join('')}
</div>`;

views.profile = (state) => `
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; border-bottom: var(--border-width) solid var(--color-border); padding-bottom: 1rem;">
  <div>
    <h2 style="font-size: 2rem; margin-bottom: 0.25rem;">My Profile</h2>
    <p style="color: #4B5563; font-size: 1rem; margin: 0;">Manage your personal information and public profile view.</p>
  </div>
  <button class="btn btn-secondary" onclick="openModal('editProfile')">Edit Profile</button>
</div>

<div style="display: flex; flex-direction: column; gap: 2rem; max-width: 900px;">
  <div class="card" style="padding: 2.5rem;">
    <div style="display: flex; align-items: center; gap: 2.5rem;">
      <div style="width: 120px; height: 120px; border-radius: 50%; background-color: var(--color-primary); border: var(--border-width) solid var(--color-border); display: flex; align-items: center; justify-content: center; font-size: 3rem; font-weight: bold; color: var(--color-text);">
        ${state.user.initials}
      </div>
      <div style="flex: 1;">
        <h3 style="font-size: 2.2rem; margin-bottom: 0.5rem; margin-top: 0;">${state.user.name}</h3>
        <p style="font-size: 1.15rem; color: #4B5563; margin-bottom: 0.5rem;">${state.user.major}</p>
        <div style="display: flex; gap: 3rem; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px dashed var(--color-border);">
          <div>
            <p style="margin: 0; font-size: 0.95rem; font-weight: bold;">University Email</p>
            <p style="margin: 0; color: #4B5563; font-size: 1.05rem;">${state.user.email}</p>
          </div>
          <div>
            <p style="margin: 0; font-size: 0.95rem; font-weight: bold;">Member Since</p>
            <p style="margin: 0; color: #4B5563; font-size: 1.05rem;">${state.user.joinDate}</p>
          </div>
        </div>
        <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px dashed var(--color-border);">
          <p style="margin: 0; font-size: 0.95rem; font-weight: bold; margin-bottom: 0.5rem;">Bio</p>
          <p style="margin: 0; color: #4B5563; font-size: 1.05rem; line-height: 1.5;">${state.user.bio || 'No bio added yet. Tell others about yourself!'}</p>
        </div>
      </div>
    </div>
  </div>

  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem;">
    <div class="card">
      <h3 class="card-title" style="margin-bottom: 1.5rem; border-bottom: 2px solid var(--color-border); padding-bottom: 0.75rem;">Skills I Offer</h3>
      <div style="display: flex; flex-wrap: wrap; gap: 0.75rem;">
        ${(state.user.skillsOffered || []).map(s=> `<span class="badge badge-success" style="font-size: 1rem; padding: 0.6rem 1rem;">${s.name}</span>`).join('')}
        ${(!state.user.skillsOffered || state.user.skillsOffered.length === 0) ? '<p style="color: #4B5563;">No skills offered yet.</p>' : ''}
      </div>
    </div>
    <div class="card">
      <h3 class="card-title" style="margin-bottom: 1.5rem; border-bottom: 2px solid var(--color-border); padding-bottom: 0.75rem;">Skills I Want to Learn</h3>
      <div style="display: flex; flex-wrap: wrap; gap: 0.75rem;">
        ${(state.user.skillsWanted || []).map(s=> `<span class="badge badge-primary" style="font-size: 1rem; padding: 0.6rem 1rem;">${s.name}</span>`).join('')}
        ${(!state.user.skillsWanted || state.user.skillsWanted.length === 0) ? '<p style="color: #4B5563;">No requested skills yet.</p>' : ''}
      </div>
    </div>
  </div>
</div>`;

views.feedback = (state) => `
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; border-bottom: var(--border-width) solid var(--color-border); padding-bottom: 1rem;">
  <div>
    <h2 style="font-size: 2rem; margin-bottom: 0.25rem;">Feedback & Ratings</h2>
    <p style="color: #4B5563; font-size: 1rem; margin: 0;">Rate your recent exchanges and see what others say about you.</p>
  </div>
</div>

<div style="display: grid; grid-template-columns: minmax(350px, 400px) 1fr; gap: 2.5rem; align-items: start;">
  <div class="card" style="position: sticky; top: 2rem;">
    <h3 class="card-title" style="margin-bottom: 1.5rem; font-size: 1.5rem;">Leave a Review</h3>
    <form onsubmit="event.preventDefault(); const sel = document.getElementById('exchange-partner'); window.store.addFeedback({ author: 'You', skill: sel.options[sel.selectedIndex].text, stars: document.getElementById('rating').options[document.getElementById('rating').selectedIndex].text.split(' ')[0], text: document.getElementById('comment').value, color: 'var(--color-primary)' }); this.reset();" style="display: flex; flex-direction: column; gap: 1.25rem;">
      <div class="input-group" style="margin-bottom: 0;">
        <label class="input-label" for="exchange-partner">Exchange Partner</label>
        <select id="exchange-partner" class="input-field" required>
          <option value="">Select a user...</option>
          ${(state.users || []).filter(u => u.userId !== state.user.userId).map(u => `
            <option value="${u.userId}">${u.name}</option>
          `).join('')}
        </select>
      </div>
      <div class="input-group" style="margin-bottom: 0;">
        <label class="input-label" for="rating">Rating</label>
        <select id="rating" class="input-field" style="font-size: 1.1rem;" required>
          <option value="5">⭐⭐⭐⭐⭐ Excellent</option>
          <option value="4">⭐⭐⭐⭐ Good</option>
          <option value="3">⭐⭐⭐ Average</option>
          <option value="2">⭐⭐ Fair</option>
          <option value="1">⭐ Poor</option>
        </select>
      </div>
      <div class="input-group" style="margin-bottom: 0;">
        <label class="input-label" for="comment">Comment</label>
        <textarea id="comment" class="input-field" rows="4" placeholder="How was the exchange? Was it helpful?" required></textarea>
      </div>
      <button type="submit" class="btn btn-primary" style="margin-top: 0.5rem; width: 100%; font-size: 1.1rem; padding: 0.875rem;">Submit Review</button>
    </form>
  </div>

  <div>
    <h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">Received Feedback</h3>
    <div style="display: flex; flex-direction: column; gap: 1.5rem;">
      ${state.feedbacks.length === 0 ? '<p style="color: #4B5563;">No feedback received yet.</p>' : ''}
      ${state.feedbacks.map(fb => `
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
          <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 48px; height: 48px; border-radius: 50%; background-color: ${fb.color}; border: var(--border-width) solid var(--color-border);"></div>
            <div>
              <h3 style="margin: 0; font-size: 1.15rem;">${fb.author}</h3>
              <span style="font-size: 0.9rem; color: #4B5563;">For ${fb.skill}</span>
            </div>
          </div>
          <div style="font-size: 1.5rem; letter-spacing: 2px;">${fb.stars}</div>
        </div>
        <p class="card-content" style="margin: 0; font-size: 1.05rem; color: var(--color-text); line-height: 1.6;">${fb.text}</p>
      </div>
      `).join('')}
    </div>
  </div>
</div>`;

function getLayout(content, activeRoute, state) {
  return `
  <nav class="top-navbar">
    <a href="#/dashboard" class="logo">Skill Exchange</a>
    <div class="user-actions" style="display: flex; align-items: center; gap: 0.75rem;">
      <div style="width: 32px; height: 32px; border-radius: 50%; background-color: var(--color-primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.9rem; border: var(--border-width) solid var(--color-border);">${state.user.initials}</div>
      <span class="profile-name" style="margin-right: 0.5rem;">${state.user.name}</span>
      <button onclick="window.store.logout()" class="btn btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.9rem;">Logout</button>
    </div>
  </nav>
  
  <div class="main-container">
    <aside class="sidebar">
      <ul class="nav-menu">
        <li class="nav-item ${activeRoute === '/dashboard' ? 'active' : ''}"><a href="#/dashboard">Dashboard</a></li>
        <li class="nav-item ${activeRoute === '/browse-skills' ? 'active' : ''}"><a href="#/browse-skills">Browse Skills</a></li>
        <li class="nav-item ${activeRoute === '/my-skills' ? 'active' : ''}"><a href="#/my-skills">My Skills</a></li>
        <li class="nav-item ${activeRoute === '/requests' ? 'active' : ''}"><a href="#/requests">Requests</a></li>
        <li class="nav-item ${activeRoute === '/profile' ? 'active' : ''}"><a href="#/profile">My Profile</a></li>
        <li class="nav-item ${activeRoute === '/feedback' ? 'active' : ''}"><a href="#/feedback">Feedback</a></li>
      </ul>
    </aside>
    <main class="content-area page-transition">${content}</main>
  </div>
  `;
}

window.router = function() {
  const hash = window.location.hash || '#/dashboard';
  const appDiv = document.getElementById('app');
  const route = hash.replace('#', '');
  const state = window.store.getState();
  
  if (!state.isLoggedIn && route !== '/login' && route !== '/signup') {
    window.location.hash = '#/login';
    return;
  }
  
  if (route === '/login') {
    appDiv.innerHTML = views.login(state);
  } else if (route === '/signup') {
    appDiv.innerHTML = views.signup(state);
  } else {
    const routeKey = route.replace('/', '');
    const renderFn = views[routeKey];
    if (renderFn) {
      appDiv.innerHTML = getLayout(renderFn(state), route, state);
    } else {
      appDiv.innerHTML = getLayout('<h2>Page Not Found</h2>', route, state);
    }
  }
};

window.store.getState = function() { return this.state; };

window.mockSendRequest = function(name) {
  alert('Exchange request sent to ' + name + '!');
  window.store.addRequest({ status: 'Pending', time: 'Just Now', theyWant: 'Requested Exchange', weWant: 'Your Skill', partner: 'To: ' + name, color: 'var(--color-primary)' });
  window.location.hash = '#/requests';
};

window.openModal = function(type, dataName, dataSkill, dataRole) {
  const modal = document.getElementById('global-modal');
  const body = document.getElementById('modal-body');
  modal.style.display = 'flex';
  
  if (type === 'editProfile') {
    body.innerHTML = `
      <h2 class="card-title" style="font-size: 1.5rem; margin-bottom: 1.5rem;">Edit Profile</h2>
      <form onsubmit="event.preventDefault(); const btn = document.getElementById('save-profile-btn'); btn.disabled = true; btn.innerText = 'Saving...'; setTimeout(() => { window.store.updateProfile({ name: document.getElementById('edit-name').value, bio: document.getElementById('edit-bio').value }); closeModal(); }, 400);" style="display: flex; flex-direction: column; gap: 1.25rem;">
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="edit-name">Full Name</label>
          <input type="text" id="edit-name" class="input-field" value="${window.store.state.user.name}" required>
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="edit-email">University Email (Read Only)</label>
          <input type="email" id="edit-email" class="input-field" value="${window.store.state.user.email}" disabled style="background-color: #F3F4F6;">
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="edit-bio">Bio</label>
          <textarea id="edit-bio" class="input-field" rows="4" placeholder="Tell others about yourself!">${window.store.state.user.bio || ''}</textarea>
        </div>
        <button type="submit" id="save-profile-btn" class="btn btn-primary" style="margin-top: 0.5rem; width: 100%; font-size: 1.1rem; padding: 0.875rem;">Save Changes</button>
      </form>
      <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px dashed var(--color-border); text-align: center;">
        <p style="margin: 0; color: #4B5563; font-size: 0.95rem;">To manage your offered and requested skills, please visit the <a href="#/my-skills" onclick="closeModal()" style="color: var(--color-primary); font-weight: bold; text-decoration: none;">My Skills</a> tab.</p>
      </div>
    `;
  } else if (type === 'createRequest') {
    body.innerHTML = `
      <h2 class="card-title" style="font-size: 1.5rem; margin-bottom: 1.5rem;">Post a Request</h2>
      <form onsubmit="event.preventDefault(); const btn = document.getElementById('submit-req-btn'); btn.disabled = true; btn.innerText = 'Saving...'; setTimeout(() => { window.store.createPublicRequest({ needed: document.getElementById('req-needed').value, desc: document.getElementById('req-desc').value, offered: document.getElementById('req-offered').value, time: document.getElementById('req-time').value }); alert('Request successfully created!'); closeModal(); }, 600);" style="display: flex; flex-direction: column; gap: 1.25rem;">
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="req-needed">Skill Needed</label>
          <input type="text" id="req-needed" class="input-field" placeholder="What do you want to learn?" required>
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="req-offered">Skill Offered in Return</label>
          <input type="text" id="req-offered" class="input-field" placeholder="What can you teach them?" required>
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="req-time">Preferred Time (Optional)</label>
          <input type="text" id="req-time" class="input-field" placeholder="e.g. Weekends, Evenings">
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="req-desc">Description</label>
          <textarea id="req-desc" class="input-field" rows="3" placeholder="Provide more details..." required></textarea>
        </div>
        <button type="submit" id="submit-req-btn" class="btn btn-primary" style="margin-top: 0.5rem; width: 100%; font-size: 1.1rem; padding: 0.875rem;">Submit Request</button>
      </form>
    `;
  } else if (type === 'skill') {
    body.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; padding-right: 2rem;">
        <span class="badge badge-${dataRole === 'Offering' ? 'success' : 'primary'}">${dataRole}</span>
      </div>
      <h2 class="card-title" style="font-size: 1.5rem; margin-bottom: 0.5rem;">${dataSkill}</h2>
      <p style="color: #4B5563; line-height: 1.6; margin-bottom: 1.5rem;">
        This is a detailed view for ${dataSkill}. The user ${dataName} is ${dataRole.toLowerCase()} this skill and is looking for a partner.
      </p>
      <button class="btn btn-primary" style="width: 100%;" onclick="mockSendRequest('${dataName}'); closeModal();">Request Exchange</button>
    `;
  } else if (type === 'profile') {
    body.innerHTML = `
      <div style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 1.5rem; padding-right: 2rem;">
        <div style="width: 80px; height: 80px; border-radius: 50%; background-color: #3B82F6; border: var(--border-width) solid var(--color-border);"></div>
        <div>
          <h2 style="margin: 0; font-size: 1.75rem;">${dataName}</h2>
          <span style="font-size: 1rem; color: #4B5563;">${dataSkill}</span>
        </div>
      </div>
      <button class="btn btn-primary" style="width: 100%;" onclick="mockSendRequest('${dataName}'); closeModal();">Connect</button>
    `;
  }
};

window.closeModal = function() { document.getElementById('global-modal').style.display = 'none'; };

window.addEventListener('click', (e) => {
  const modal = document.getElementById('global-modal');
  if (e.target === modal) closeModal();
});

window.addEventListener('hashchange', router);
window.addEventListener('DOMContentLoaded', router);

// Execute immediately in case DOMContentLoaded already fired
router();

window.filterSkills = function() {
  const query = document.getElementById('skill-search').value.toLowerCase();
  const category = document.getElementById('skill-category').value;
  
  const cards = document.querySelectorAll('#browse-grid .card');
  cards.forEach(card => {
    const text = card.innerText.toLowerCase();
    const matchesQuery = text.includes(query);
    const cardCategory = card.getAttribute('data-category') || 'All Categories';
    const matchesCat = category === 'All Categories' || cardCategory === category;
    
    if (matchesQuery && matchesCat) {
      card.style.display = '';
    } else {
      card.style.display = 'none';
    }
  });
};
