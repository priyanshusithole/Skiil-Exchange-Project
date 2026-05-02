import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add small avatar to Navbar and rename Profile to My Profile in Sidebar
nav_old = """    <div class="user-actions">
      <span class="profile-name">${state.user.name}</span>
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
        <li class="nav-item ${activeRoute === '/profile' ? 'active' : ''}"><a href="#/profile">Profile</a></li>"""

nav_new = """    <div class="user-actions" style="display: flex; align-items: center; gap: 0.75rem;">
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
        <li class="nav-item ${activeRoute === '/profile' ? 'active' : ''}"><a href="#/profile">My Profile</a></li>"""
content = content.replace(nav_old, nav_new)

# 2. Highlight user's own skills in Browse Skills page
browse_old = """  ${state.marketplaceSkills.map(skill => `
  <div class="card card-clickable" onclick="openModal('skill', '${skill.providerName}', '${skill.skillName}', '${skill.type}')">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">"""

browse_new = """  ${state.marketplaceSkills.map(skill => `
  <div class="card card-clickable" ${skill.providerId === state.user.userId ? 'style="border-color: var(--color-primary); background-color: #FFF7ED;"' : ''} onclick="openModal('skill', '${skill.providerName}', '${skill.skillName}', '${skill.type}')">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">"""
content = content.replace(browse_old, browse_new)

# 3. Update the Marketplace skill rendering to show "Your Skill" badge and "Manage" button if it's theirs
badge_old = """      <span class="badge badge-${skill.type === 'Offering' ? 'success' : 'primary'}">${skill.type}</span>"""
badge_new = """      <span class="badge" style="background-color: ${skill.providerId === state.user.userId ? 'var(--color-primary)' : (skill.type === 'Offering' ? 'var(--color-success)' : 'var(--color-primary)')}; color: white;">${skill.providerId === state.user.userId ? 'Your Skill' : skill.type}</span>"""
content = content.replace(badge_old, badge_new)

actions_old = """    <div class="card-actions">
      <button class="btn btn-primary" style="flex: 1;" onclick="event.stopPropagation(); window.mockSendRequest('${skill.providerName}')">${skill.type === 'Offering' ? 'Request Trade' : 'Offer Skill'}</button>
    </div>"""
actions_new = """    <div class="card-actions">
      ${skill.providerId === state.user.userId 
        ? `<button class="btn btn-secondary" style="flex: 1;" onclick="event.stopPropagation(); window.location.hash='#/my-skills'">Manage</button>`
        : `<button class="btn btn-primary" style="flex: 1;" onclick="event.stopPropagation(); window.mockSendRequest('${skill.providerName}')">${skill.type === 'Offering' ? 'Request Trade' : 'Offer Skill'}</button>`}
    </div>"""
content = content.replace(actions_old, actions_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Implemented profile UX enhancements")
