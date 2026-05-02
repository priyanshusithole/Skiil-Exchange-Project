import codecs

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# Replace all occurrences of the image source with a query string for cache busting
content = content.replace('src="login_bg.png"', 'src="login_bg.png?v=2"')

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)

print("Applied cache-busting to login_bg.png")
