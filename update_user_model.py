import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

store_old = """  login(email, password) {
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

store_new = """  login(email, password) {
    if(!this.state.users) this.state.users = [];
    
    // Simulate password hashing for authentication check
    const hashedPassword = btoa(password); 
    const existingUser = this.state.users.find(u => u.email === email && u.password === hashedPassword);
    if (!existingUser) {
      alert("Invalid email or password. Please try again.");
      return;
    }
    
    this.state.user = {
      userId: existingUser.userId,
      name: existingUser.name,
      major: 'Student',
      email: existingUser.email,
      joinDate: new Date(existingUser.createdAt).toLocaleDateString(),
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
    
    const userId = 'usr_' + Date.now();
    const hashedPassword = btoa(password); // Simulated hashing
    const createdAt = new Date().toISOString();
    
    // Push new user following exact database model
    this.state.users.push({
      userId: userId,
      name: name,
      email: email,
      password: hashedPassword,
      bio: '',
      skillsOffered: [],
      skillsWanted: [],
      createdAt: createdAt
    });
    
    this.state.user = {
      userId: userId,
      name: name,
      major: 'Student',
      email: email,
      joinDate: new Date(createdAt).toLocaleDateString(),
      initials: name.substring(0,2).toUpperCase()
    };
    this.state.isLoggedIn = true;
    this.save();
    window.location.hash = '#/dashboard';
  },"""

content = content.replace(store_old, store_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Updated Auth system with strict user model")
