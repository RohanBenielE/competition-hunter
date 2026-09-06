from tools import (
    search_competitions,
    fetch_competition,
    match_competition
)


# -----------------------------------
# ACTION EXECUTION
# -----------------------------------

def execute_action(name, arguments):

    if name == "search_competitions":

        return search_competitions(
            **arguments
        )

    elif name == "fetch_competition":

        return fetch_competition(
            **arguments
        )

    elif name == "match_competition":

        return match_competition(
            **arguments
        )

    else:

        return {
            "error": f"Unknown action: {name}"
        }