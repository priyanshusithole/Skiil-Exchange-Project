import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

view_old = """<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">My Requests</h3>
<div class="card-grid" style="margin-bottom: 3rem;">
  ${(!state.publicRequests || state.publicRequests.filter(r => r.userId === state.user.email).length === 0) ? '<p style="color: #4B5563; font-style: italic;">You haven\\'t created any requests yet.</p>' : ''}
  ${(state.publicRequests || []).filter(r => r.userId === state.user.email).map(req => `
  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge badge-primary">Looking to Learn</span>
      <span style="font-weight: bold; font-size: 0.8rem; color: #4B5563;">${req.status.toUpperCase()}</span>
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
</div>

<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">Available Requests</h3>
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

view_new = """<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">My Exchanges</h3>
<div class="card-grid" style="margin-bottom: 3rem;">
  ${(!state.publicRequests || state.publicRequests.filter(r => r.status === 'accepted' && (r.userId === state.user.email || r.acceptedBy === state.user.email)).length === 0) ? '<p style="color: #4B5563; font-style: italic;">You have no active exchanges.</p>' : ''}
  ${(state.publicRequests || []).filter(r => r.status === 'accepted' && (r.userId === state.user.email || r.acceptedBy === state.user.email)).map(req => `
  <div class="card" style="border-color: var(--color-success); background-color: #F8FAFFC0;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <span class="badge badge-success">Active Exchange</span>
      <span style="font-weight: bold; font-size: 0.8rem; color: #4B5563;">Matched</span>
    </div>
    <div style="margin-top: 1rem;">
      <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
        <span style="font-size: 0.95rem; font-weight: 600;">Partner: ${req.userId === state.user.email ? req.acceptedByName : req.userName}</span>
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

<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">My Open Requests</h3>
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
</div>

<h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">Available Requests</h3>
<div class="card-grid">
  ${(!state.publicRequests || state.publicRequests.filter(r => r.userId !== state.user.email && (r.status === 'open' || (r.status === 'accepted' && r.acceptedBy !== state.user.email))).length === 0) ? '<p style="color: #4B5563; font-style: italic;">No open requests available from other students.</p>' : ''}
  ${(state.publicRequests || []).filter(r => r.userId !== state.user.email && (r.status === 'open' || (r.status === 'accepted' && r.acceptedBy !== state.user.email))).map(req => `
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
</div>`;"""

content = content.replace(view_old, view_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Updated Exchanges view!")
