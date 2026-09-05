from dotenv import load_dotenv
import os
import json
from openai import OpenAI

from tools import (
    search_competitions,
    fetch_competition,
    match_competition
)

load_dotenv()



client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)



tools = [

    {
        "type": "function",
        "function": {
            "name": "search_competitions",
            "description": """
Search the web for current and upcoming
hackathons and competitions.
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description":
                        "Search query for relevant current competitions."
                    },
                    "max_results": {
                        "type": "integer",
                        "description":
                        "Maximum number of search results.",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "fetch_competition",
            "description": """
Open an individual competition webpage.

The tool returns:
- webpage content
- detected dates
- detected deadline
- whether the competition appears expired

IMPORTANT:
If is_expired is true, do NOT recommend
the competition.
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description":
                        "URL of the individual competition webpage."
                    }
                },
                "required": ["url"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "match_competition",
            "description": """
Calculate how well a CURRENT competition
matches the user's profile.
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
    "type": "boolean",
    "description":
    "Whether fetch_competition verified that this competition is expired."
},

"deadline": {
    "type": "string",
    "description":
    "Verified competition deadline returned by fetch_competition. Use null if not verified."
}
                },
                "required": [
                    "user_skills",
                    "user_interests",
                    "experience_level",
                    "preference",
                    "competition_text"
                ]
            }
        }
    }
]


# ==========================================
# TOOL EXECUTOR
# ==========================================

def execute_tool(name, arguments):

    # --------------------------------------
    # SEARCH TOOL
    # --------------------------------------

    if name == "search_competitions":

        return search_competitions(
            **arguments
        )


    # --------------------------------------
    # FETCH TOOL
    # --------------------------------------

    elif name == "fetch_competition":

        return fetch_competition(
            **arguments
        )


    # --------------------------------------
    # MATCH TOOL
    # --------------------------------------

    elif name == "match_competition":

        return match_competition(
            **arguments
        )


    # --------------------------------------
    # UNKNOWN TOOL
    # --------------------------------------

    else:

        return {
            "error": f"Unknown tool: {name}"
        }

# ==========================================
# REACT AGENT
# ==========================================

def run_agent(user_profile):

    messages = [

        {
            "role": "system",

            "content": """
You are Competition Hunter.

CURRENT DATE:
September 5, 2026.

Your job is to find CURRENT and UPCOMING
competitions and hackathons that match
the user's profile.

==========================================
STRICT DATE RULES
==========================================

1. Never recommend an expired competition.

2. Never recommend an event whose verified
   deadline is before September 5, 2026.

3. If fetch_competition returns:

   is_expired = true

   immediately reject that competition.

4. Do NOT call match_competition for an
   expired competition.

5. A competition with an old deadline must
   NOT be recommended even if its webpage
   still says "registration open".

6. Prefer competitions with deadlines after
   September 5, 2026.

7. If the deadline cannot be verified,
   clearly say "Deadline not verified".

==========================================
COMPETITION PAGE RULE
==========================================

A search result is NOT automatically a
competition page.

You MUST verify that the URL belongs to
the individual competition before recommending
that competition.

==========================================
LISTING PAGE RULE
==========================================

A page containing multiple competitions,
hackathons, articles, directories, or lists
is NOT an individual competition.

Examples:

"Top 20 Hackathons"

"Upcoming Hackathons in India"

"2026 Upcoming Hackathons"

"AI Hackathons"

are listing/article pages.

DO NOT recommend these pages directly.

==========================================
INDIVIDUAL URL RULE
==========================================

Every recommended competition MUST have
its own individual competition URL.

If multiple competitions are mentioned on
one listing page, you MUST NOT give the same
listing URL to all of them.

Instead:

1. Identify the competition name.

2. Search again for that specific competition.

3. Find its individual official competition page.

4. Fetch that individual page.

5. Verify its information.

6. Only then match and recommend it.

==========================================
VERIFICATION RULE
==========================================

A competition can ONLY be recommended if:

- Its individual page was fetched.
- The fetched page contains information
  about that specific competition.
- Its deadline/status is verified when possible.
- Its URL is the individual competition URL.

If you cannot find an individual page,
DO NOT recommend the competition.

==========================================
TOOLS
==========================================

1. search_competitions

Search the web for current competitions.

2. fetch_competition

Open an individual competition page and
retrieve its actual information.

This tool also returns:

- deadline
- found dates
- is_expired

3. match_competition

Calculate compatibility with the user.

==========================================
REACT PROCESS
==========================================

THINK
↓
ACT
↓
OBSERVE
↓
THINK
↓
ACT
↓
OBSERVE
↓
FINAL

==========================================
NORMAL WORKFLOW
==========================================

1. Search for relevant current competitions.

2. Review the search results.

3. Reject obvious listing, category,
   directory, and article pages.

4. If a useful competition is mentioned
   inside a listing page, search specifically
   for that competition's individual page.

5. Select individual competition pages.

6. Fetch each individual page.

7. Inspect the returned:

   deadline
   is_expired
   content

8. Reject expired competitions.

9. Only call match_competition for
   verified non-expired competitions.

10. You MUST call match_competition for
    EVERY verified non-expired competition
    before recommending it.

11. Never recommend a competition if its
    match score has not been calculated.

12. Never recommend a competition if its
    individual page was not fetched.

13. Compare the match scores.

14. Recommend the strongest CURRENT
    competitions based on the scores.

==========================================
FINAL RESPONSE
==========================================

For each recommendation provide:

🏆 Competition name

📊 Match score

🎯 Why it matches

📅 Deadline

🌐 Online / Offline / Hybrid

🔗 Competition URL

Do not invent information.

Do not recommend expired competitions.

Do not recommend competitions just because
they appeared in search results.
"""
        },

        {
            "role": "user",

            "content": f"""
Find CURRENT and UPCOMING competitions
for me.

My profile:

Skills:
{', '.join(user_profile['skills'])}

Interests:
{', '.join(user_profile['interests'])}

Experience level:
{user_profile['experience_level']}

Preference:
{user_profile['preference']}
"""
        }

    ]


    # ======================================
    # REACT LOOP
    # ======================================

    while True:

        print("\n🤖 THINKING...")

        response = client.chat.completions.create(

            model="openai/gpt-4o-mini",

            messages=messages,

            tools=tools,

            tool_choice="auto"
        )

        message = response.choices[0].message

        messages.append(message)


        # ==================================
        # FINAL ANSWER
        # ==================================

        if not message.tool_calls:

            print(
                "\n🏆 FINAL RECOMMENDATIONS\n"
            )

            print(message.content)

            break


        # ==================================
        # TOOL CALLS
        # ==================================

        for tool_call in message.tool_calls:

            tool_name = (
                tool_call.function.name
            )

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                f"🔧 TOOL CALL: {tool_name}"
            )

            print(
                f"📦 ARGUMENTS: {arguments}"
            )


            # Execute tool
            result = execute_tool(
                tool_name,
                arguments
            )

            # --------------------------------------
            # HARD EXPIRY GATE
            # --------------------------------------

            if tool_name == "fetch_competition":

                if result.get("is_expired"):

                    print("🚫 BLOCKED — EXPIRED COMPETITION")

                    result["blocked"] = True
                    result["block_reason"] = (
            "Competition is expired and must not be recommended."
        )

                else:

                 result["blocked"] = False

            # ----------------------------------
            # SHOW EXPIRY INFORMATION
            # ----------------------------------

            if tool_name == "fetch_competition":

                if result.get("is_expired"):

                    print(
                        "❌ EXPIRED — REJECTED"
                    )

                else:

                    print(
                        "✅ APPEARS CURRENT"
                    )

                print(
                    "📅 Detected deadline:",
                    result.get("deadline")
                )


            print(
                "👀 OBSERVATION RECEIVED"
            )


            # Send observation back to LLM
            messages.append(
                {
                    "role": "tool",

                    "tool_call_id":
                    tool_call.id,

                    "content":
                    json.dumps(result)
                }
            )