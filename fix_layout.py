import codecs

# 1. Update index.html to add the media query
with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

style_old = "<style>"
style_new = "<style>\n    @media(min-width: 768px) { .split-left { display: block !important; } }\n"
content = content.replace(style_old, style_new)

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)

# 2. Update app.js to use the class and remove invalid inline CSS
with codecs.open('app.js', 'r', 'utf-8') as f:
    app_content = f.read()

old_div_login = """<div style="flex: 1; position: relative; border-right: 5px solid #000; overflow: hidden; display: none; @media(min-width: 768px){display: block;}">"""
new_div_login = """<div class="split-left" style="flex: 1; position: relative; border-right: 5px solid #000; overflow: hidden; display: none;">"""
app_content = app_content.replace(old_div_login, new_div_login)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(app_content)

print("Fixed layout bug")
