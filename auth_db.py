import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add users array to initialState
state_old = """const initialState = {
  isLoggedIn: false,
  user: null,
  mySkills: [],"""
  
state_new = """const initialState = {
  isLoggedIn: false,
  user: null,
  users: [],
  mySkills: [],"""
content = content.replace(state_old, state_new)

# 2. Update store methods (login, signup)
store_old = """  login(email) {
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
  },"""

store_new = """  login(email, password) {
    if(!this.state.users) this.state.users = [];
    const existingUser = this.state.users.find(u => u.email === email && u.password === password);
    if (!existingUser) {
      alert("Invalid email or password. Please try again.");
      return;
    }
    
    this.state.user = {
      name: existingUser.name,
      major: 'Student',
      email: existingUser.email,
      joinDate: existingUser.joinDate,
      initials: existingUser.name.substring(0,2).toUpperCase()
    };
    this.state.isLoggedIn = true;
    this.save();
    window.location.hash = '#/dashboard';
  },
  signup(name, email, password) {
    if(!this.state.users) this.state.users = [];
    const existingUser = this.state.users.find(u => u.email === email);
    if (existingUser) {
      alert("An account with this email already exists. Please log in.");
      return;
    }
    
    const joinDate = new Date().toLocaleDateString();
    this.state.users.push({ name, email, password, joinDate });
    
    this.state.user = {
      name: name,
      major: 'Student',
      email: email,
      joinDate: joinDate,
      initials: name.substring(0,2).toUpperCase()
    };
    this.state.isLoggedIn = true;
    this.save();
    window.location.hash = '#/dashboard';
  },"""
content = content.replace(store_old, store_new)

# 3. Update forms to pass passwords
login_old = """<form onsubmit="event.preventDefault(); window.store.login(document.getElementById('email').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
login_new = """<form onsubmit="event.preventDefault(); window.store.login(document.getElementById('email').value, document.getElementById('password').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
content = content.replace(login_old, login_new)

signup_old = """<form onsubmit="event.preventDefault(); window.store.signup(document.getElementById('fullname').value, document.getElementById('email').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
signup_new = """<form onsubmit="event.preventDefault(); window.store.signup(document.getElementById('fullname').value, document.getElementById('email').value, document.getElementById('password').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">"""
content = content.replace(signup_old, signup_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Updated Auth system")
