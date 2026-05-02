import codecs

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

signup_old = """  <form onsubmit="event.preventDefault(); window.store.login(document.getElementById('email').value, document.getElementById('password').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">
    <div class="input-group" style="margin-bottom: 0;">
      <label class="input-label" for="fullname">Full Name</label>"""

signup_new = """  <form onsubmit="event.preventDefault(); window.store.signup(document.getElementById('fullname').value, document.getElementById('email').value, document.getElementById('password').value);" style="display: flex; flex-direction: column; gap: 1.25rem;">
    <div class="input-group" style="margin-bottom: 0;">
      <label class="input-label" for="fullname">Full Name</label>"""

# Replace ONLY the one in views.signup by matching the surrounding context
content = content.replace(signup_old, signup_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Fixed signup form submission bug")
