import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add publicRequests to initialState
content = re.sub(
    r'upcomingSessions: \[\]\n};',
    r'upcomingSessions: [],\n  publicRequests: []\n};',
    content
)

# 2. Add createPublicRequest to window.store
new_method = """  addFeedback(feedback) {
    this.state.feedbacks.unshift({ id: Date.now(), ...feedback });
    this.save();
  },
  createPublicRequest(req) {
    const newRequest = {
      requestId: 'req_' + Date.now(),
      userId: this.state.user.email,
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
  }"""
content = re.sub(
    r'  addFeedback\(feedback\) \{\n    this\.state\.feedbacks\.unshift\(\{ id: Date\.now\(\), \.\.\.feedback \}\);\n    this\.save\(\);\n  \}',
    new_method,
    content
)

# 3. Update window.openModal to handle createRequest
modal_new = """window.openModal = function(type, dataName, dataSkill, dataRole) {
  const modal = document.getElementById('global-modal');
  const body = document.getElementById('modal-body');
  modal.style.display = 'flex';
  
  if (type === 'createRequest') {
    body.innerHTML = `
      <h2 class="card-title" style="font-size: 1.5rem; margin-bottom: 1.5rem;">Post a Request</h2>
      <form onsubmit="event.preventDefault(); window.store.createPublicRequest({ needed: document.getElementById('req-needed').value, desc: document.getElementById('req-desc').value, offered: document.getElementById('req-offered').value, time: document.getElementById('req-time').value }); closeModal();" style="display: flex; flex-direction: column; gap: 1.25rem;">
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
        <button type="submit" class="btn btn-primary" style="margin-top: 0.5rem; width: 100%; font-size: 1.1rem; padding: 0.875rem;">Submit Request</button>
      </form>
    `;
  } else if (type === 'skill') {"""
content = content.replace("window.openModal = function(type, dataName, dataSkill, dataRole) {\n  const modal = document.getElementById('global-modal');\n  const body = document.getElementById('modal-body');\n  modal.style.display = 'flex';\n  \n  if (type === 'skill') {", modal_new)

# 4. Update Browse Skills to show publicRequests
browse_old = """<div class="card-grid">
  ${state.marketplaceSkills.length === 0 ? '<p style="color: #4B5563; font-style: italic;">No skills available in the marketplace yet.</p>' : ''}
  ${state.marketplaceSkills.map(skill => `"""

browse_new = """<div class="card-grid">
  ${(state.marketplaceSkills.length === 0 && (!state.publicRequests || state.publicRequests.length === 0)) ? '<p style="color: #4B5563; font-style: italic;">No skills or requests available in the marketplace yet.</p>' : ''}
  
  ${(state.publicRequests || []).filter(req => req.status === 'open').map(req => `
  <div class="card card-clickable" onclick="openModal('skill', '${req.userName}', '${req.skillNeeded}', 'Looking to Learn')">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge badge-primary">Looking to Learn</span>
      <span style="font-weight: bold; font-size: 0.8rem; color: #4B5563;">${new Date(req.createdAt).toLocaleDateString()}</span>
    </div>
    <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.5rem;">${req.skillNeeded}</h3>
    <p class="card-content" style="margin-bottom: 0.5rem; flex: 1;">${req.description}</p>
    <p style="font-size: 0.9rem; margin-bottom: 0.5rem; color: #4B5563;"><strong>Offering:</strong> ${req.skillOffered}</p>
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; margin-top: 1rem;">
      <div style="width: 28px; height: 28px; border-radius: 50%; background-color: #A78BFA; border: var(--border-width) solid var(--color-border);"></div>
      <span style="font-size: 0.95rem; font-weight: 600;">${req.userName}</span>
    </div>
    <div class="card-actions">
      <button class="btn btn-primary" style="flex: 1;" onclick="event.stopPropagation(); window.mockSendRequest('${req.userName}')">Offer Skill</button>
    </div>
  </div>
  `).join('')}

  ${state.marketplaceSkills.map(skill => `"""

if browse_old in content:
    content = content.replace(browse_old, browse_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Updated successfully")
