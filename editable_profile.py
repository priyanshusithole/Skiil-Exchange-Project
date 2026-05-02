import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Update views.profile to use openModal('editProfile')
profile_old = """  <button class="btn btn-secondary" onclick="alert('Edit profile form opened.')">Edit Profile</button>"""
profile_new = """  <button class="btn btn-secondary" onclick="openModal('editProfile')">Edit Profile</button>"""
content = content.replace(profile_old, profile_new)

# 2. Add updateProfile logic to window.store
store_old = """  acceptPublicRequest(requestId) {"""
store_new = """  updateProfile(data) {
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
  acceptPublicRequest(requestId) {"""
content = content.replace(store_old, store_new)

# 3. Add editProfile to openModal
modal_old = """  if (type === 'createRequest') {"""
modal_new = """  if (type === 'editProfile') {
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
  } else if (type === 'createRequest') {"""
content = content.replace(modal_old, modal_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Implemented Editable Profile Modal")
