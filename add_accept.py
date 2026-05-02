import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add acceptPublicRequest to window.store
store_old = """    window.location.hash = '#/browse-skills';
  }
};"""

store_new = """    window.location.hash = '#/browse-skills';
  },
  acceptPublicRequest(requestId) {
    const req = this.state.publicRequests.find(r => r.requestId === requestId);
    if(req && req.userId !== this.state.user.email) {
      req.status = 'accepted';
      req.acceptedBy = this.state.user.email;
      req.acceptedByName = this.state.user.name;
      this.save();
    }
  }
};"""

content = content.replace(store_old, store_new)

# 2. Update Available Requests logic in views.requests
view_old = """<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">Available Requests</h3>
<div class="card-grid">
  ${(!state.publicRequests || state.publicRequests.filter(r => r.userId !== state.user.email && r.status === 'open').length === 0) ? '<p style="color: #4B5563; font-style: italic;">No open requests available from other students.</p>' : ''}
  ${(state.publicRequests || []).filter(r => r.userId !== state.user.email && r.status === 'open').map(req => `
  <div class="card" style="border-color: #A78BFA;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge" style="background-color: #A78BFA; color: white;">Open Request</span>
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
      <div style="width: 28px; height: 28px; border-radius: 50%; background-color: #A78BFA; border: var(--border-width) solid var(--color-border);"></div>
      <span style="font-size: 0.95rem; font-weight: 600;">${req.userName}</span>
    </div>
    <div class="card-actions" style="margin-top: auto; display: flex;">
      <button class="btn btn-primary" style="flex: 1; padding: 0.75rem;" onclick="window.mockSendRequest('${req.userName}')">Offer to Help</button>
    </div>
  </div>
  `).join('')}
</div>`;"""

view_new = """<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">Available Requests</h3>
<div class="card-grid">
  ${(!state.publicRequests || state.publicRequests.filter(r => r.userId !== state.user.email).length === 0) ? '<p style="color: #4B5563; font-style: italic;">No requests available from other students.</p>' : ''}
  ${(state.publicRequests || []).filter(r => r.userId !== state.user.email).map(req => `
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
        : `<button class="btn btn-secondary" style="flex: 1; padding: 0.75rem;" disabled>Accepted by ${req.acceptedBy === state.user.email ? 'You' : (req.acceptedByName || 'someone')}</button>`
      }
    </div>
  </div>
  `).join('')}
</div>`;"""

content = content.replace(view_old, view_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Updated Accept Request logic!")
