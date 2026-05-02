import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add closePublicRequest to window.store
store_old = """    if(req && req.userId !== this.state.user.email) {
      req.status = 'accepted';
      req.acceptedBy = this.state.user.email;
      req.acceptedByName = this.state.user.name;
      this.save();
    }
  }
};"""

store_new = """    if(req && req.userId !== this.state.user.email) {
      req.status = 'accepted';
      req.acceptedBy = this.state.user.email;
      req.acceptedByName = this.state.user.name;
      this.save();
    }
  },
  closePublicRequest(requestId) {
    const req = this.state.publicRequests.find(r => r.requestId === requestId);
    if(req && req.userId === this.state.user.email) {
      req.status = 'closed';
      this.save();
    }
  }
};"""

content = content.replace(store_old, store_new)

# 2. Update Modal Submission UX
modal_old = """<form onsubmit="event.preventDefault(); window.store.createPublicRequest({ needed: document.getElementById('req-needed').value, desc: document.getElementById('req-desc').value, offered: document.getElementById('req-offered').value, time: document.getElementById('req-time').value }); closeModal();" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
modal_new = """<form onsubmit="event.preventDefault(); const btn = document.getElementById('submit-req-btn'); btn.disabled = true; btn.innerText = 'Saving...'; setTimeout(() => { window.store.createPublicRequest({ needed: document.getElementById('req-needed').value, desc: document.getElementById('req-desc').value, offered: document.getElementById('req-offered').value, time: document.getElementById('req-time').value }); alert('Request successfully created!'); closeModal(); }, 600);" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
content = content.replace(modal_old, modal_new)

modal_btn_old = """<button type="submit" class="btn btn-primary" style="margin-top: 0.5rem; width: 100%; font-size: 1.1rem; padding: 0.875rem;">Submit Request</button>"""
modal_btn_new = """<button type="submit" id="submit-req-btn" class="btn btn-primary" style="margin-top: 0.5rem; width: 100%; font-size: 1.1rem; padding: 0.875rem;">Submit Request</button>"""
content = content.replace(modal_btn_old, modal_btn_new)

# 3. Update 'My Open Requests' to 'My Posted Requests' with Badges and Close logic
requests_old = """<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">My Open Requests</h3>
<div class="card-grid" style="margin-bottom: 3rem;">
  ${(!state.publicRequests || state.publicRequests.filter(r => r.userId === state.user.email && r.status === 'open').length === 0) ? '<p style="color: #4B5563; font-style: italic;">You have no open requests.</p>' : ''}
  ${(state.publicRequests || []).filter(r => r.userId === state.user.email && r.status === 'open').map(req => `
  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge badge-primary">Looking to Learn</span>
      <span style="font-weight: bold; font-size: 0.8rem; color: #4B5563;">OPEN</span>
    </div>
    <div style="margin-top: 1rem;">
      <p style="margin: 0; font-size: 0.95rem; color: #4B5563;">Skill needed:</p>
      <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.2rem;">${req.skillNeeded}</h3>
      <div style="margin: 1rem 0; border-top: 2px dashed var(--color-border);"></div>
      <p style="margin: 0; font-size: 0.95rem; color: #4B5563;">Offering in return:</p>
      <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.2rem; color: var(--color-success);">${req.skillOffered}</h3>
    </div>
    <p class="card-content" style="margin-top: 1rem;">${req.description}</p>
    <div class="card-actions" style="margin-top: auto; display: flex; gap: 0.5rem; padding-top: 1rem;">
      <button class="btn btn-secondary" style="flex: 1; padding: 0.5rem; font-size: 0.95rem;" onclick="alert('Editing request...')">Edit</button>
      <button class="btn btn-danger" style="flex: 1; padding: 0.5rem; font-size: 0.95rem;" onclick="alert('Closing request...')">Close</button>
    </div>
  </div>
  `).join('')}
</div>"""

requests_new = """<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">My Posted Requests</h3>
<div class="card-grid" style="margin-bottom: 3rem;">
  ${(!state.publicRequests || state.publicRequests.filter(r => r.userId === state.user.email && r.status !== 'accepted').length === 0) ? '<p style="color: #4B5563; font-style: italic;">You have no posted requests.</p>' : ''}
  ${(state.publicRequests || []).filter(r => r.userId === state.user.email && r.status !== 'accepted').map(req => `
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
</div>"""
content = content.replace(requests_old, requests_new)


# 4. Highlight user's own requests in Browse Skills
browse_old = """${(state.publicRequests || []).filter(req => req.status === 'open').map(req => `
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
  `).join('')}"""

browse_new = """${(state.publicRequests || []).filter(req => req.status === 'open').map(req => `
  <div class="card card-clickable" ${req.userId === state.user.email ? 'style="border-color: var(--color-primary); background-color: #FFF7ED;"' : ''} onclick="openModal('skill', '${req.userName}', '${req.skillNeeded}', 'Looking to Learn')">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge" style="background-color: ${req.userId === state.user.email ? 'var(--color-primary)' : '#3B82F6'}; color: white;">${req.userId === state.user.email ? 'Your Request' : 'Looking to Learn'}</span>
      <span style="font-weight: bold; font-size: 0.8rem; color: #4B5563;">${new Date(req.createdAt).toLocaleDateString()}</span>
    </div>
    <h3 class="card-title" style="font-size: 1.25rem; margin-top: 0.5rem;">${req.skillNeeded}</h3>
    <p class="card-content" style="margin-bottom: 0.5rem; flex: 1;">${req.description}</p>
    <p style="font-size: 0.9rem; margin-bottom: 0.5rem; color: #4B5563;"><strong>Offering:</strong> ${req.skillOffered}</p>
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; margin-top: 1rem;">
      <div style="width: 28px; height: 28px; border-radius: 50%; background-color: #A78BFA; border: var(--border-width) solid var(--color-border);"></div>
      <span style="font-size: 0.95rem; font-weight: 600;">${req.userId === state.user.email ? 'You' : req.userName}</span>
    </div>
    <div class="card-actions">
      ${req.userId === state.user.email 
        ? `<button class="btn btn-secondary" style="flex: 1;" onclick="event.stopPropagation(); window.location.hash='#/requests'">Manage</button>`
        : `<button class="btn btn-primary" style="flex: 1;" onclick="event.stopPropagation(); window.mockSendRequest('${req.userName}')">Offer Skill</button>`}
    </div>
  </div>
  `).join('')}"""
  
content = content.replace(browse_old, browse_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Updated UX enhancements")
