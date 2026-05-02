import codecs
import re

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Update addMySkill to share the same ID for marketplace
addskill_old = """      this.state.marketplaceSkills.unshift({
        id: Date.now(),
        providerId: this.state.user.userId,
        providerName: this.state.user.name,"""

addskill_new = """      this.state.marketplaceSkills.unshift({
        id: newSkill.id,
        providerId: this.state.user.userId,
        providerName: this.state.user.name,"""

content = content.replace(addskill_old, addskill_new)

# 2. Update deleteMySkill to include access control on marketplace array
deleteskill_old = """  deleteMySkill(id) {
    if (this.state.user.skillsOffered) this.state.user.skillsOffered = this.state.user.skillsOffered.filter(s => s.id !== id);
    if (this.state.user.skillsWanted) this.state.user.skillsWanted = this.state.user.skillsWanted.filter(s => s.id !== id);
    this.save();
  },"""

deleteskill_new = """  deleteMySkill(id) {
    // Access control: Ensure user owns the marketplace skill before deleting
    if (this.state.marketplaceSkills) {
      const mkSkill = this.state.marketplaceSkills.find(s => s.id === id);
      if (mkSkill && mkSkill.providerId !== this.state.user.userId) {
         console.error("Unauthorized: Cannot delete a skill you do not own.");
         return; // Block deletion
      }
      // Authorized: Remove from global marketplace
      this.state.marketplaceSkills = this.state.marketplaceSkills.filter(s => s.id !== id);
    }

    if (this.state.user.skillsOffered) this.state.user.skillsOffered = this.state.user.skillsOffered.filter(s => s.id !== id);
    if (this.state.user.skillsWanted) this.state.user.skillsWanted = this.state.user.skillsWanted.filter(s => s.id !== id);
    this.save();
  },"""

content = content.replace(deleteskill_old, deleteskill_new)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Updated access controls and data isolation")
