import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Update the search bar section in views['browse-skills']
search_old = """  <div style="display: flex; gap: 1rem;">
      <select class="input-field" style="padding: 0.5rem; font-size: 0.9rem; margin-bottom: 0;">
        <option>All Categories</option>
        <option>Programming</option>
        <option>Languages</option>
        <option>Design</option>
      </select>
      <button class="btn btn-primary" style="padding: 0.5rem 1rem;" onclick="alert('Searching database...')">Search</button>
  </div>"""

search_new = """  <div style="display: flex; gap: 1rem; width: 100%; max-width: 600px;">
      <input type="text" id="skill-search" class="input-field" placeholder="Search skills, users, or keywords..." style="margin-bottom: 0; flex: 1;" oninput="window.filterSkills()">
      <select id="skill-category" class="input-field" style="padding: 0.5rem; font-size: 0.9rem; margin-bottom: 0; width: 150px;" onchange="window.filterSkills()">
        <option>All Categories</option>
        <option>Programming</option>
        <option>Languages</option>
        <option>Design</option>
        <option>Academics</option>
      </select>
  </div>"""
content = content.replace(search_old, search_new)

# 2. Add id="browse-grid" and data-category attributes to cards
grid_old = """<div class="card-grid">"""
grid_new = """<div class="card-grid" id="browse-grid">"""
# Only replace the first occurrence which belongs to browse-skills since we split by views
content = content.replace(grid_old, grid_new, 1)

req_card_old = """  <div class="card card-clickable" ${req.userId === state.user.userId ? 'style="border-color: var(--color-primary); background-color: #FFF7ED;"' : ''} onclick="openModal('skill', '${req.userName}', '${req.skillNeeded}', 'Looking to Learn')">"""
req_card_new = """  <div class="card card-clickable" data-category="All Categories" ${req.userId === state.user.userId ? 'style="border-color: var(--color-primary); background-color: #FFF7ED;"' : ''} onclick="openModal('skill', '${req.userName}', '${req.skillNeeded}', 'Looking to Learn')">"""
content = content.replace(req_card_old, req_card_new)

skill_card_old = """  <div class="card card-clickable" ${skill.providerId === state.user.userId ? 'style="border-color: var(--color-primary); background-color: #FFF7ED;"' : ''} onclick="openModal('skill', '${skill.providerName}', '${skill.skillName}', '${skill.type}')">"""
skill_card_new = """  <div class="card card-clickable" data-category="${skill.category}" ${skill.providerId === state.user.userId ? 'style="border-color: var(--color-primary); background-color: #FFF7ED;"' : ''} onclick="openModal('skill', '${skill.providerName}', '${skill.skillName}', '${skill.type}')">"""
content = content.replace(skill_card_old, skill_card_new)


# 3. Append the window.filterSkills function
filter_fn = """
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
"""

content += filter_fn

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Implemented search bar functionality")
