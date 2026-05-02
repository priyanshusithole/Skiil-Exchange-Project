import codecs

with codecs.open('app.js', 'r', 'utf-8') as f:
    content = f.read()

old_add_skill = """  addMySkill(skill) {
    this.state.mySkills.push({ id: Date.now(), ...skill });
    this.save();
  },"""

new_add_skill = """  addMySkill(skill) {
    const newSkill = { id: Date.now(), ...skill };
    this.state.mySkills.unshift(newSkill);
    
    // If the user is offering a skill, publish it to the marketplace so others can see it!
    if (skill.type === 'Offering') {
      if(!this.state.marketplaceSkills) this.state.marketplaceSkills = [];
      this.state.marketplaceSkills.unshift({
        id: Date.now(),
        providerName: this.state.user.name,
        skillName: skill.name,
        category: skill.category,
        type: 'Offering',
        desc: skill.desc,
        color: '#10B981' // Success Green
      });
    }
    
    this.save();
  },"""

content = content.replace(old_add_skill, new_add_skill)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(content)
print("Updated addMySkill to publish to marketplace")
