import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Update createPublicRequest
content = content.replace("userId: this.state.user.email,", "userId: this.state.user.userId,")

# 2. Update accept/close logic
content = content.replace("req.userId !== this.state.user.email", "req.userId !== this.state.user.userId")
content = content.replace("req.userId === this.state.user.email", "req.userId === this.state.user.userId")
content = content.replace("req.acceptedBy = this.state.user.email", "req.acceptedBy = this.state.user.userId")

# 3. Update view rendering logic in browse-skills and requests
content = content.replace("r.userId === state.user.email", "r.userId === state.user.userId")
content = content.replace("r.userId !== state.user.email", "r.userId !== state.user.userId")
content = content.replace("r.acceptedBy === state.user.email", "r.acceptedBy === state.user.userId")
content = content.replace("r.acceptedBy !== state.user.email", "r.acceptedBy !== state.user.userId")
content = content.replace("req.userId === state.user.email", "req.userId === state.user.userId")
content = content.replace("req.acceptedBy === state.user.email", "req.acceptedBy === state.user.userId")

# 4. Attach providerId when adding skill to marketplace
marketplace_old = """      this.state.marketplaceSkills.unshift({
        id: Date.now(),
        providerName: this.state.user.name,"""
marketplace_new = """      this.state.marketplaceSkills.unshift({
        id: Date.now(),
        providerId: this.state.user.userId,
        providerName: this.state.user.name,"""
content = content.replace(marketplace_old, marketplace_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Updated database relational linkages")
