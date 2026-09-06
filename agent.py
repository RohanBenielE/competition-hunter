from memory import get_user_profile

from dotenv import load_dotenv
import os
import json
from datetime import datetime

from openai import OpenAI

from actions import execute_action


# -----------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------

load_dotenv()


# -----------------------------------
# OPENROUTER CLIENT
# -----------------------------------

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# -----------------------------------
# TOOL DEFINITIONS
# -----------------------------------

tools = [

    {
        "type": "function",

        "function": {

            "name": "search_competitions",

            "description": """
Search the web for current and upcoming
competitions, hackathons, challenges,
and contests.
""",

            "parameters": {

                "type": "object",

                "properties": {

                    "query": {
                        "type": "string",
                        "description": "Search query for competitions"
                    }

                },

                "required": [
                    "query"
                ]
            }
        }
    },


    {
        "type": "function",

        "function": {

            "name": "fetch_competition",

            "description": """
Fetch and verify an individual competition page.
Extract useful details such as title, deadline,
eligibility, mode, description and expiry status.
""",

            "parameters": {

                "type": "object",

                "properties": {

                    "url": {
                        "type": "string",
                        "description": "URL of the competition page"
                    }

                },

                "required": [
                    "url"
                ]
            }
        }
    },


    {
        "type": "function",

        "function": {

            "name": "match_competition",

            "description": """
Calculate how well a competition matches
the user's skills, interests, experience level
and preference.
""",

            "parameters": {

                "type": "object",

                "properties": {

                    "user_skills": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },

                    "user_interests": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },

                    "experience_level": {
                        "type": "string"
                    },

                    "preference": {
                        "type": "string"
                    },

                    "competition_text": {
                        "type": "string"
                    },

                    "is_expired": {
                        "type": "boolean"
                    },

                    "deadline": {
                        "type": "string"
                    }
                },

                "required": [
                    "user_skills",
                    "user_interests",
                    "experience_level",
                    "preference",
                    "competition_text",
                    "is_expired",
                    "deadline"
                ]
            }
        }
    }
]


# -----------------------------------
# TOOL EXECUTION
# -----------------------------------

def execute_tool(name, arguments):

    return execute_action(
        name,
        arguments
    )


# -----------------------------------
# REACT AGENT
# -----------------------------------

def run_agent(user_profile, previous_profile=None):

    if previous_profile is None:
        previous_profile = get_user_profile()



    # -----------------------------------
    # SYSTEM PROMPT
    # -----------------------------------
        current_date = datetime.now().strftime("%Y-%m-%d")
    system_prompt = """
You are COMPETITION HUNTER, an Agentic AI
that finds current and upcoming competitions,
hackathons, contests and challenges.

Today's date is: {current_date}

You must use the ReAct process:

THINK → ACT → OBSERVE → THINK → ACT → FINAL

You have three tools:

1. search_competitions
2. fetch_competition
3. match_competition


IMPORTANT DATE RULES:

- Today's date is provided dynamically by the system.
- Use today's date as the reference when deciding
  whether a competition is current, upcoming, or expired.
- Only recommend competitions that are CURRENT
  or UPCOMING.
- Never recommend competitions whose deadline
  has already passed.
- Always verify the deadline using the actual
  competition page whenever possible.


IMPORTANT PAGE RULES:

- Prefer individual competition pages.
- Do NOT recommend a general listing page,
  search page, category page or collection page
  as the competition itself.
- Each recommended competition must represent
  a specific competition.


VERIFICATION PROCESS:

1. Search for competitions.
2. Examine the search results.
3. Fetch promising individual competition pages.
4. Check whether the competition is expired.
5. Match valid competitions against the user's profile.
6. Return the best matches.


MATCHING:

Consider:

- Skills
- Interests
- Experience level
- Online / Offline preference
- Competition deadline


MEMORY:

The user may have a previous remembered profile.

The current profile always has priority.

Use previous memory only as additional context
when the current profile does not contradict it.

FINAL RESPONSE:

Return ONLY verified current or upcoming
individual competitions.

For each competition provide:

- Competition name
- Organizer
- Deadline
- Mode
- Why it matches the user
- Match score
- Competition URL

STRICT FINAL CHECK:

Before recommending a competition:

1. Check its deadline against today's date.
2. Never recommend an expired competition.
3. Never recommend a competition marked
   "is_expired": true.
4. Never recommend a competition marked
   "blocked": true.
5. Never recommend a generic listing page,
   search page, category page or collection page.
6. Use the individual competition URL whenever
   one is available.
7. If the deadline is unknown, clearly say
   "Deadline: Not confirmed" instead of inventing
   a date.
"""

    # -----------------------------------
    # INITIAL USER MESSAGE
    # -----------------------------------

    user_message = f"""
Find CURRENT and UPCOMING competitions
for me.

MY CURRENT PROFILE:

Skills:
{', '.join(user_profile['skills'])}

Interests:
{', '.join(user_profile['interests'])}

Experience level:
{user_profile['experience_level']}

Preference:
{user_profile['preference']}


MY PREVIOUS REMEMBERED PROFILE:

Skills:
{', '.join(previous_profile.get('skills', [])) if previous_profile else 'None'}

Interests:
{', '.join(previous_profile.get('interests', [])) if previous_profile else 'None'}

Experience level:
{previous_profile.get('experience_level', 'None') if previous_profile else 'None'}

Preference:
{previous_profile.get('preference', 'None') if previous_profile else 'None'}


MEMORY INSTRUCTION:

Use the previous remembered profile as additional
context about my preferences.

The CURRENT profile has priority if it differs
from the previous remembered profile.

Do not assume that old preferences are still valid
when the current profile provides different values.
"""


    # -----------------------------------
    # MESSAGE HISTORY
    # -----------------------------------

    messages = [

        {
            "role": "system",
            "content": system_prompt
        },

        {
            "role": "user",
            "content": user_message
        }

    ]

        # -----------------------------------
    # REACT LOOP
    # -----------------------------------

    for step in range(10):

        print("\n🤖 THINKING...")

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        messages.append(
            assistant_message
        )


        # -----------------------------------
        # CHECK FOR TOOL CALLS
        # -----------------------------------

        if not assistant_message.tool_calls:

            print("\n🏆 FINAL RECOMMENDATIONS\n")

            print(
                assistant_message.content
            )

            return


        # -----------------------------------
        # EXECUTE TOOL CALLS
        # -----------------------------------

        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                f"\n🔧 TOOL CALL: {tool_name}"
            )

            print(
                "Arguments:",
                arguments
            )


            # -----------------------------------
            # HARD EXPIRY CHECK
            # -----------------------------------

                        # -----------------------------------
            # EXECUTE TOOL
            # -----------------------------------

            result = execute_tool(
                tool_name,
                arguments
            )


            # -----------------------------------
            # HARD EXPIRY PROTECTION
            # -----------------------------------

            if tool_name == "fetch_competition":

                if (
                    isinstance(result, dict)
                    and result.get("is_expired") is True
                ):

                    result["blocked"] = True

                    result["error"] = (
                        "This competition is expired. "
                        "Do NOT recommend it."
                    )


            # -----------------------------------
            # OBSERVE TOOL RESULT
            # -----------------------------------

            print("\n👀 OBSERVATION:")
            print(result)


            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                }
            )


    # -----------------------------------
    # MAXIMUM STEPS REACHED
    # -----------------------------------

    print(
        "\n⚠️ Agent reached the maximum number "
        "of reasoning steps."
    )


# -----------------------------------
# END OF AGENT
# -----------------------------------