import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

new_views = """views.login = (state) => `
<div style="display: flex; min-height: 100vh; background-color: #FAEDDF; font-family: 'Inter', sans-serif;">
  <div style="flex: 1; position: relative; border-right: 5px solid #000; overflow: hidden; display: none; @media(min-width: 768px){display: block;}">
    <img src="login_bg.png" style="width: 100%; height: 100%; object-fit: cover;" alt="Skill Exchange">
    <div style="position: absolute; bottom: 2rem; left: 2rem; right: 2rem; background: rgba(250, 237, 223, 0.95); border: 4px solid #000; border-radius: 8px; padding: 1.5rem; box-shadow: 4px 4px 0 #000;">
      <h1 style="font-size: 1.75rem; font-weight: 900; margin-bottom: 0.5rem; text-transform: uppercase; color: #F59E0B; text-shadow: 1px 1px 0 #000;">Student Skill Exchange</h1>
      <p style="font-weight: 700; color: #000; margin: 0; font-size: 1.1rem; text-transform: uppercase;">Trade knowledge. Grow together.</p>
    </div>
  </div>
  
  <div style="flex: 1; display: flex; align-items: center; justify-content: center; padding: 2rem; max-width: 600px;">
    <div style="width: 100%; max-width: 400px;">
      <h2 style="font-size: 2.5rem; font-weight: 900; color: #F59E0B; margin-bottom: 0.5rem; text-transform: uppercase; text-shadow: 1px 1px 0 #000;">SECURE PORTAL</h2>
      <p style="font-weight: 600; margin-bottom: 2rem; color: #4B5563;">Enter your credentials to access the student dashboard</p>
      
      <form onsubmit="event.preventDefault(); window.store.login(document.getElementById('email').value, document.getElementById('password').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="email" style="font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #000;">University Email</label>
          <input type="email" id="email" class="input-field" placeholder="student@university.edu" required style="width: 100%; padding: 0.875rem; font-size: 1rem; font-weight: 600; background: #EBF1FF; border: 3px solid #000; border-radius: 6px; outline: none; box-shadow: 2px 2px 0 #000; box-sizing: border-box; color: #000;">
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="password" style="font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #000;">Password</label>
          <input type="password" id="password" class="input-field" placeholder="••••••••" required style="width: 100%; padding: 0.875rem; font-size: 1rem; font-weight: 600; background: #EBF1FF; border: 3px solid #000; border-radius: 6px; outline: none; box-shadow: 2px 2px 0 #000; box-sizing: border-box; color: #000;">
        </div>
        <button type="submit" class="btn" style="width: 100%; padding: 1rem; font-size: 1.1rem; font-weight: 900; background-color: #F59E0B; color: #000; border: 3px solid #000; border-radius: 6px; cursor: pointer; text-transform: uppercase; margin-top: 1rem; box-shadow: 3px 3px 0 #000; transition: transform 0.1s;">Log In</button>
      </form>
      <p style="text-align: center; margin-top: 2rem; font-size: 0.95rem; font-weight: 600;">
        Don't have an account? <a href="#/signup" style="color: #F59E0B; font-weight: 900; text-decoration: none; text-shadow: 0.5px 0.5px 0 #000;">SIGN UP</a>
      </p>
    </div>
  </div>
</div>`;

views.signup = (state) => `
<div style="display: flex; min-height: 100vh; background-color: #FAEDDF; font-family: 'Inter', sans-serif;">
  <div style="flex: 1; position: relative; border-right: 5px solid #000; overflow: hidden; display: none; @media(min-width: 768px){display: block;}">
    <img src="login_bg.png" style="width: 100%; height: 100%; object-fit: cover;" alt="Skill Exchange">
    <div style="position: absolute; bottom: 2rem; left: 2rem; right: 2rem; background: rgba(250, 237, 223, 0.95); border: 4px solid #000; border-radius: 8px; padding: 1.5rem; box-shadow: 4px 4px 0 #000;">
      <h1 style="font-size: 1.75rem; font-weight: 900; margin-bottom: 0.5rem; text-transform: uppercase; color: #F59E0B; text-shadow: 1px 1px 0 #000;">Student Skill Exchange</h1>
      <p style="font-weight: 700; color: #000; margin: 0; font-size: 1.1rem; text-transform: uppercase;">Join the community today.</p>
    </div>
  </div>
  
  <div style="flex: 1; display: flex; align-items: center; justify-content: center; padding: 2rem; max-width: 600px;">
    <div style="width: 100%; max-width: 400px;">
      <h2 style="font-size: 2.5rem; font-weight: 900; color: #F59E0B; margin-bottom: 0.5rem; text-transform: uppercase; text-shadow: 1px 1px 0 #000;">NEW ACCOUNT</h2>
      <p style="font-weight: 600; margin-bottom: 2rem; color: #4B5563;">Enter your details to join the marketplace</p>
      
      <form onsubmit="event.preventDefault(); window.store.signup(document.getElementById('fullname').value, document.getElementById('email').value, document.getElementById('password').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="fullname" style="font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #000;">Full Name</label>
          <input type="text" id="fullname" class="input-field" placeholder="e.g. John Doe" required style="width: 100%; padding: 0.875rem; font-size: 1rem; font-weight: 600; background: #EBF1FF; border: 3px solid #000; border-radius: 6px; outline: none; box-shadow: 2px 2px 0 #000; box-sizing: border-box; color: #000;">
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="email" style="font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #000;">University Email</label>
          <input type="email" id="email" class="input-field" placeholder="student@university.edu" required style="width: 100%; padding: 0.875rem; font-size: 1rem; font-weight: 600; background: #EBF1FF; border: 3px solid #000; border-radius: 6px; outline: none; box-shadow: 2px 2px 0 #000; box-sizing: border-box; color: #000;">
        </div>
        <div class="input-group" style="margin-bottom: 0;">
          <label class="input-label" for="password" style="font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #000;">Password</label>
          <input type="password" id="password" class="input-field" placeholder="Create a password" required style="width: 100%; padding: 0.875rem; font-size: 1rem; font-weight: 600; background: #EBF1FF; border: 3px solid #000; border-radius: 6px; outline: none; box-shadow: 2px 2px 0 #000; box-sizing: border-box; color: #000;">
        </div>
        <button type="submit" class="btn" style="width: 100%; padding: 1rem; font-size: 1.1rem; font-weight: 900; background-color: #F59E0B; color: #000; border: 3px solid #000; border-radius: 6px; cursor: pointer; text-transform: uppercase; margin-top: 1rem; box-shadow: 3px 3px 0 #000; transition: transform 0.1s;">Sign Up</button>
      </form>
      <p style="text-align: center; margin-top: 2rem; font-size: 0.95rem; font-weight: 600;">
        Already have an account? <a href="#/login" style="color: #F59E0B; font-weight: 900; text-decoration: none; text-shadow: 0.5px 0.5px 0 #000;">LOG IN</a>
      </p>
    </div>
  </div>
</div>`;
"""

pattern = re.compile(r"views\.login = \(state\) => `[\s\S]*?views\.dashboard = \(state\)", re.MULTILINE)
content = pattern.sub(new_views + "\nviews.dashboard = (state", content)

# Inject media query for handling the layout on smaller screens safely without breaking HTML
if "<style>" in content:
    content = content.replace("<style>", "<style>\n    @media(min-width: 768px) { .split-left { display: block !important; } }\n")

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Implemented retro login design")
