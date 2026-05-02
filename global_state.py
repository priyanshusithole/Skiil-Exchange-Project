import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Update save() to sync to DB
save_old = """  save() {
    localStorage.setItem('skillExchangeState', JSON.stringify(this.state));
    window.router(); // Re-render current view on state change
  },"""
save_new = """  save() {
    if (this.state.user && this.state.users) {
      const dbIdx = this.state.users.findIndex(u => u.userId === this.state.user.userId);
      if (dbIdx > -1) {
        this.state.users[dbIdx].bio = this.state.user.bio;
        this.state.users[dbIdx].skillsOffered = this.state.user.skillsOffered;
        this.state.users[dbIdx].skillsWanted = this.state.user.skillsWanted;
      }
    }
    localStorage.setItem('skillExchangeState', JSON.stringify(this.state));
    window.router(); // Re-render current view on state change
  },"""
content = content.replace(save_old, save_new)

# 2. Update login() and signup() user models
login_user_old = """    this.state.user = {
      userId: existingUser.userId,
      name: existingUser.name,
      major: 'Student',
      email: existingUser.email,
      joinDate: new Date(existingUser.createdAt).toLocaleDateString(),
      initials: existingUser.name.substring(0,2).toUpperCase()
    };"""
login_user_new = """    this.state.user = {
      userId: existingUser.userId,
      name: existingUser.name,
      major: 'Student',
      email: existingUser.email,
      bio: existingUser.bio || '',
      skillsOffered: existingUser.skillsOffered || [],
      skillsWanted: existingUser.skillsWanted || [],
      joinDate: new Date(existingUser.createdAt).toLocaleDateString(),
      initials: existingUser.name.substring(0,2).toUpperCase()
    };"""
content = content.replace(login_user_old, login_user_new)

signup_user_old = """    this.state.user = {
      userId: userId,
      name: name,
      major: 'Student',
      email: email,
      joinDate: new Date(createdAt).toLocaleDateString(),
      initials: name.substring(0,2).toUpperCase()
    };"""
signup_user_new = """    this.state.user = {
      userId: userId,
      name: name,
      major: 'Student',
      email: email,
      bio: '',
      skillsOffered: [],
      skillsWanted: [],
      joinDate: new Date(createdAt).toLocaleDateString(),
      initials: name.substring(0,2).toUpperCase()
    };"""
content = content.replace(signup_user_old, signup_user_new)

# 3. Update addMySkill and deleteMySkill
skills_old = """  addMySkill(skill) {
    const newSkill = { id: Date.now(), ...skill };
    this.state.mySkills.unshift(newSkill);
    
    // If the user is offering a skill, publish it to the marketplace so others can see it!
    if (skill.type === 'Offering') {
      if(!this.state.marketplaceSkills) this.state.marketplaceSkills = [];
      this.state.marketplaceSkills.unshift({
        id: Date.now(),
        providerName: this.state.user.name,
        skillName: skill.name,
        category: skill.category,
        type: 'Offering',
        desc: skill.desc,
        color: '#10B981' // Success Green
      });
    }
    
    this.save();
  },
  deleteMySkill(id) {
    this.state.mySkills = this.state.mySkills.filter(s => s.id !== id);
    this.save();
  },"""
skills_new = """  addMySkill(skill) {
    const newSkill = { id: Date.now(), ...skill };
    
    if(!this.state.user.skillsOffered) this.state.user.skillsOffered = [];
    if(!this.state.user.skillsWanted) this.state.user.skillsWanted = [];
    
    if (skill.type === 'Offering') {
      this.state.user.skillsOffered.unshift(newSkill);
      // Publish to global marketplace
      if(!this.state.marketplaceSkills) this.state.marketplaceSkills = [];
      this.state.marketplaceSkills.unshift({
        id: Date.now(),
        providerName: this.state.user.name,
        skillName: skill.name,
        category: skill.category,
        type: 'Offering',
        desc: skill.desc,
        color: '#10B981' // Success Green
      });
    } else {
      this.state.user.skillsWanted.unshift(newSkill);
    }
    this.save();
  },
  deleteMySkill(id) {
    if (this.state.user.skillsOffered) this.state.user.skillsOffered = this.state.user.skillsOffered.filter(s => s.id !== id);
    if (this.state.user.skillsWanted) this.state.user.skillsWanted = this.state.user.skillsWanted.filter(s => s.id !== id);
    this.save();
  },"""
content = content.replace(skills_old, skills_new)


# 4. Update views.dashboard
dash_old = """      <li><strong>${state.mySkills.filter(s=>s.type==='Offering').length}</strong> Active Offers</li>"""
dash_new = """      <li><strong>${(state.user.skillsOffered || []).length}</strong> Active Offers</li>"""
content = content.replace(dash_old, dash_new)

# 5. Update views['my-skills']
myskills_old = """${state.mySkills.length === 0 ? '<p style="color: #4B5563;">No skills added yet.</p>' : state.mySkills.map(skill => `"""
myskills_new = """${(!state.user.skillsOffered?.length && !state.user.skillsWanted?.length) ? '<p style="color: #4B5563;">No skills added yet.</p>' : [...(state.user.skillsOffered||[]), ...(state.user.skillsWanted||[])].map(skill => `"""
content = content.replace(myskills_old, myskills_new)

# 6. Update views.profile
profile_old = """        <div style="display: flex; gap: 3rem; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px dashed var(--color-border);">
          <div>
            <p style="margin: 0; font-size: 0.95rem; font-weight: bold;">University Email</p>
            <p style="margin: 0; color: #4B5563; font-size: 1.05rem;">${state.user.email}</p>
          </div>
          <div>
            <p style="margin: 0; font-size: 0.95rem; font-weight: bold;">Member Since</p>
            <p style="margin: 0; color: #4B5563; font-size: 1.05rem;">${state.user.joinDate}</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem;">
    <div class="card">
      <h3 class="card-title" style="margin-bottom: 1.5rem; border-bottom: 2px solid var(--color-border); padding-bottom: 0.75rem;">Skills I Offer</h3>
      <div style="display: flex; flex-wrap: wrap; gap: 0.75rem;">
        ${state.mySkills.filter(s=>s.type==='Offering').map(s=> `<span class="badge badge-success" style="font-size: 1rem; padding: 0.6rem 1rem;">${s.name}</span>`).join('')}
        ${state.mySkills.filter(s=>s.type==='Offering').length === 0 ? '<p style="color: #4B5563;">No skills offered yet.</p>' : ''}
      </div>
    </div>
    <div class="card">
      <h3 class="card-title" style="margin-bottom: 1.5rem; border-bottom: 2px solid var(--color-border); padding-bottom: 0.75rem;">Skills I Want to Learn</h3>
      <div style="display: flex; flex-wrap: wrap; gap: 0.75rem;">
        ${state.mySkills.filter(s=>s.type==='Looking to Learn').map(s=> `<span class="badge badge-primary" style="font-size: 1rem; padding: 0.6rem 1rem;">${s.name}</span>`).join('')}
        ${state.mySkills.filter(s=>s.type==='Looking to Learn').length === 0 ? '<p style="color: #4B5563;">No requested skills yet.</p>' : ''}
      </div>
    </div>
  </div>"""

profile_new = """        <div style="display: flex; gap: 3rem; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px dashed var(--color-border);">
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
  </div>"""

content = content.replace(profile_old, profile_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Updated Global user data context")
