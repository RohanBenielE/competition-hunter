from agent import run_agent


# -----------------------------------
# GET USER PROFILE
# -----------------------------------

print("=" * 50)
print("🏆 COMPETITION HUNTER")
print("=" * 50)

print("\nLet's find competitions that match you!\n")


skills_input = input(
    "💻 What are your skills? (comma separated)\n> "
)

interests_input = input(
    "\n🎯 What are your interests? (comma separated)\n> "
)

experience_level = input(
    "\n📚 What is your experience level? "
    "(Beginner / Intermediate / Advanced)\n> "
)

preference = input(
    "\n🌐 What is your preference? "
    "(Online / Offline / Any)\n> "
)


# -----------------------------------
# CONVERT INPUT TO LISTS
# -----------------------------------

user_skills = [
    skill.strip()
    for skill in skills_input.split(",")
    if skill.strip()
]

user_interests = [
    interest.strip()
    for interest in interests_input.split(",")
    if interest.strip()
]


# -----------------------------------
# USER PROFILE
# -----------------------------------

user_profile = {
    "skills": user_skills,
    "interests": user_interests,
    "experience_level": experience_level.strip(),
    "preference": preference.strip()
}


# -----------------------------------
# DISPLAY PROFILE
# -----------------------------------

print("\n" + "=" * 50)
print("👤 YOUR PROFILE")
print("=" * 50)

print("Skills:", ", ".join(user_skills))
print("Interests:", ", ".join(user_interests))
print("Experience:", experience_level)
print("Preference:", preference)


# -----------------------------------
# START AGENT
# -----------------------------------

print("\n" + "=" * 50)
print("🤖 SEARCHING FOR YOUR BEST COMPETITIONS...")
print("=" * 50)

run_agent(user_profile)