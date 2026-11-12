SYSTEM_PROMPT = (
    "You are Atlas, a practical travel-planning assistant. "
    "Use the supplied travel notes for facts about places. "
    "Do not invent prices, opening hours, availability or specific venue names "
    "that are not in the notes. If the notes lack something, say it needs to be "
    "checked. Give a clear day-by-day plan with a short reason for each day, "
    "matching the traveller's interests, budget and pace."
)

REVISE_PROMPT = (
    SYSTEM_PROMPT
    + " You will be given an existing itinerary and a requested change. "
    "Apply only the requested change and keep the traveller's original "
    "destination, number of days, budget, interests and pace. "
    "Return the full updated itinerary."
)


def format_notes(notes: list[dict]) -> str:
    return "\n".join(
        f"- [{n['id']}] {n.get('text') or n.get('description', '')}" for n in notes
    ) or "No matching travel notes were found."


def trip_request(destination, days, budget, interests, pace, extra) -> str:
    return (
        f"Create a {days}-day itinerary for {destination}. "
        f"Budget: {budget or 'not specified'}. "
        f"Interests: {interests or 'not specified'}. "
        f"Pace: {pace}. Extra preferences: {extra or 'none'}."
    )


def itinerary_user_message(request: str, notes: list[dict]) -> str:
    return f"Travel request: {request}\n\nTravel notes:\n{format_notes(notes)}"


def revise_user_message(request: str, itinerary: str, change: str, notes: list[dict]) -> str:
    return (
        f"Original request: {request}\n\n"
        f"Travel notes:\n{format_notes(notes)}\n\n"
        f"Current itinerary:\n{itinerary}\n\n"
        f"Requested change: {change}"
    )