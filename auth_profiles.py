import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Update initialState
state_old = """const initialState = {
  isLoggedIn: false,
  user: {
    name: 'New Student',
    major: 'Undeclared Major',
    email: 'student@university.edu',
    joinDate: 'Just Now',
    initials: 'NS'
  },
  mySkills: [],"""

state_new = """const initialState = {
  isLoggedIn: false,
  user: null,
  mySkills: [],"""

content = content.replace(state_old, state_new)

# 2. Update store methods (login, signup)
store_old = """  login() {
    this.state.isLoggedIn = true;
    this.save();
    window.location.hash = '#/dashboard';
  },
  logout() {"""

store_new = """  login(email) {
    const name = email.split('@')[0];
    this.state.user = {
      name: name,
      major: 'Student',
      email: email,
      joinDate: new Date().toLocaleDateString(),
      initials: name.substring(0,2).toUpperCase()
    };
    this.state.isLoggedIn = true;
    this.save();
    window.location.hash = '#/dashboard';
  },
  signup(name, email) {
    this.state.user = {
      name: name,
      major: 'Student',
      email: email,
      joinDate: new Date().toLocaleDateString(),
      initials: name.substring(0,2).toUpperCase()
    };
    this.state.isLoggedIn = true;
    this.save();
    window.location.hash = '#/dashboard';
  },
  logout() {"""

content = content.replace(store_old, store_new)


# 3. Update login and signup forms
login_old = """<form onsubmit="event.preventDefault(); window.store.login();" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
login_new = """<form onsubmit="event.preventDefault(); window.store.login(document.getElementById('email').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
content = content.replace(login_old, login_new)

signup_old = """<form onsubmit="event.preventDefault(); window.store.login();" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
signup_new = """<form onsubmit="event.preventDefault(); window.store.signup(document.getElementById('fullname').value, document.getElementById('email').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
content = content.replace(signup_old, signup_new)


# 4. Update Feedback select options
feedback_old = """        <select id="exchange-partner" class="input-field" required>
          <option value="">Select a recent partner...</option>
          <option value="1">Emma W. (Conversational Spanish)</option>
          <option value="2">Marcus T. (Python Programming)</option>
        </select>"""

feedback_new = """        <select id="exchange-partner" class="input-field" required>
          <option value="">Select a recent partner...</option>
          ${(state.publicRequests || []).filter(r => r.status === 'accepted' && (r.userId === state.user.email || r.acceptedBy === state.user.email)).map(r => `
            <option value="${r.requestId}">${r.userId === state.user.email ? r.acceptedByName : r.userName} (${r.skillNeeded} ↔ ${r.skillOffered})</option>
          `).join('')}
        </select>"""
content = content.replace(feedback_old, feedback_new)


# Also update the Feedback form submission to use actual partner name
feedback_submit_old = """<form onsubmit="event.preventDefault(); window.store.addFeedback({ author: 'You', skill: 'Recent Session', stars: document.getElementById('rating').options[document.getElementById('rating').selectedIndex].text.split(' ')[0], text: document.getElementById('comment').value, color: 'var(--color-primary)' }); this.reset();" style="display: flex; flex-direction: column; gap: 1.25rem;">"""

feedback_submit_new = """<form onsubmit="event.preventDefault(); const sel = document.getElementById('exchange-partner'); window.store.addFeedback({ author: 'You', skill: sel.options[sel.selectedIndex].text, stars: document.getElementById('rating').options[document.getElementById('rating').selectedIndex].text.split(' ')[0], text: document.getElementById('comment').value, color: 'var(--color-primary)' }); this.reset();" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
content = content.replace(feedback_submit_old, feedback_submit_new)


with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Removed all hardcoded user data")
