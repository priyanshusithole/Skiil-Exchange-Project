import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Remove the destructive "Reset Data" button from the Requests page
reset_btn_old = """  <div style="display: flex; gap: 1rem;">
    <button class="btn btn-primary" onclick="openModal('createRequest')">Create Request</button>
    <button class="btn btn-secondary" onclick="window.store.reset()">Reset Data</button>
  </div>"""

reset_btn_new = """  <div style="display: flex; gap: 1rem;">
    <button class="btn btn-primary" onclick="openModal('createRequest')">Create Request</button>
  </div>"""
content = content.replace(reset_btn_old, reset_btn_new)

# 2. Update logout() to properly clear the active session user
logout_old = """  logout() {
    this.state.isLoggedIn = false;
    this.save();
    window.location.hash = '#/login';
  },"""

logout_new = """  logout() {
    this.state.isLoggedIn = false;
    this.state.user = null; // Clear the active session
    this.save();
    window.location.hash = '#/login';
  },"""
content = content.replace(logout_old, logout_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Removed Reset Data button and fixed logout clearing")
