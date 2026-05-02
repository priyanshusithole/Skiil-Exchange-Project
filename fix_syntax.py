import codecs

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace("views.dashboard = (state => `", "views.dashboard = (state) => `")
content = content.replace("views.dashboard = (state=> `", "views.dashboard = (state) => `")

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Fixed syntax error")
