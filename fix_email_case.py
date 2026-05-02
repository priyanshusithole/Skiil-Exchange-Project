import codecs

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# Make login case-insensitive and whitespace-trimmed
login_old = """  login(email, password) {
    if(!this.state.users) this.state.users = [];
    
    // Simulate password hashing for authentication check
    const hashedPassword = btoa(password); 
    const existingUser = this.state.users.find(u => u.email === email && u.password === hashedPassword);"""

login_new = """  login(email, password) {
    email = email.toLowerCase().trim();
    if(!this.state.users) this.state.users = [];
    
    // Simulate password hashing for authentication check
    const hashedPassword = btoa(password); 
    const existingUser = this.state.users.find(u => u.email.toLowerCase() === email && u.password === hashedPassword);"""

content = content.replace(login_old, login_new)

# Make signup case-insensitive and whitespace-trimmed
signup_old = """  signup(name, email, password) {
    if(!this.state.users) this.state.users = [];
    const existingUser = this.state.users.find(u => u.email === email);"""

signup_new = """  signup(name, email, password) {
    email = email.toLowerCase().trim();
    if(!this.state.users) this.state.users = [];
    const existingUser = this.state.users.find(u => u.email.toLowerCase() === email);"""

content = content.replace(signup_old, signup_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Added case-insensitive email handling")
