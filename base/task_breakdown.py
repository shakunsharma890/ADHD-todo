"""
task_breakdown.py
------------------
Generates 3-7 small, concrete, ADHD-friendly subtasks for a given task.

Design philosophy (ADHD-friendly breakdown rules):
    - Every step should be small enough to start in under 2 minutes
      (reduces task paralysis / activation energy).
    - Steps are concrete physical/digital actions ("Open PowerPoint"),
      never vague intentions ("Work on it", "Think about it").
    - Steps follow a natural sequence: gather -> prepare -> do -> check/save.
    - We never return more than 7 steps (overwhelm) or fewer than 3
      (not enough scaffolding).

Strategy:
    1. Try to match the task text against a bank of keyword -> step-template
       rules (specific, high quality breakdowns for common task types).
    2. If no keyword matches, fall back to a generic but still concrete
       breakdown template for the predicted category.
    3. As a last resort (totally unknown category), use a universal generic
       breakdown template.

This module has ZERO dependency on the ML model — it only needs the raw task
text and (optionally) the predicted category, so it can be unit tested and
reused independently of the classifier.
"""

import re
from typing import List, Optional


# ---------------------------------------------------------------------------
# 1. KEYWORD-SPECIFIC BREAKDOWN RULES
# ---------------------------------------------------------------------------
# Each rule: (list of trigger keywords, function that returns step list).
# Rules are checked in order; the first match wins.
# `{task}` placeholders let templates reference the user's literal wording.

def _presentation_steps(task: str) -> List[str]:
    return [
        "Gather lecture notes / source material",
        "Create a rough presentation outline",
        "Design the presentation slides",
        "Add diagrams, examples, or screenshots",
        "Practice presenting it once out loud",
    ]


def _assignment_report_steps(task: str) -> List[str]:
    return [
        "Open the assignment brief and re-read the requirements",
        "List out the sections / questions you need to cover",
        "Write a rough draft for the first section",
        "Fill in the remaining sections one at a time",
        "Proofread once and check formatting",
        "Submit the assignment before the deadline",
    ]


def _exam_viva_steps(task: str) -> List[str]:
    return [
        "Gather the relevant notes or textbook chapters",
        "List the topics most likely to be asked",
        "Skim through one topic at a time",
        "Write or say a 2-minute summary for each topic",
        "Do a quick self-test on the weakest topic",
    ]


def _doctor_appt_steps(task: str) -> List[str]:
    return [
        "Find the clinic / doctor's contact number",
        "Call or open the booking app",
        "Pick a date and time that works",
        "Confirm the appointment",
        "Add it to your calendar with a reminder",
    ]


def _gym_workout_steps(task: str) -> List[str]:
    return [
        "Lay out your workout clothes and shoes",
        "Fill your water bottle",
        "Leave for the gym / unroll the mat at home",
        "Do a 5 minute warm-up",
        "Complete the planned workout",
    ]


def _meds_steps(task: str) -> List[str]:
    return [
        "Find the medication / prescription",
        "Check the dosage instructions",
        "Take it with water",
        "Set a reminder for the next dose",
    ]


def _shopping_buy_steps(task: str) -> List[str]:
    return [
        "Write down exactly what you need to buy",
        "Decide where to buy it (store or app)",
        "Add the items to your cart or bag",
        "Complete the purchase or checkout",
        "Put the items away once you're back",
    ]


def _bug_fix_deploy_steps(task: str) -> List[str]:
    return [
        "Open the issue / ticket and re-read the description",
        "Reproduce the problem locally",
        "Identify the likely cause in the code",
        "Write and test a fix",
        "Commit the change with a clear message",
        "Deploy / push and verify it works",
    ]


def _meeting_steps(task: str) -> List[str]:
    return [
        "Check the meeting time and link/location",
        "Skim the agenda or last meeting's notes",
        "Jot down 1-2 talking points",
        "Join a couple minutes early",
        "Write down any action items during the meeting",
    ]


def _docs_report_steps(task: str) -> List[str]:
    return [
        "Open the existing document",
        "List the sections that need updates",
        "Update the first outdated section",
        "Update the remaining sections",
        "Save and share the updated version",
    ]


def _call_text_steps(task: str) -> List[str]:
    return [
        "Find their contact in your phone",
        "Think of one thing you want to say or ask",
        "Send the text or make the call",
        "Note down anything you need to follow up on",
    ]


def _plan_event_steps(task: str) -> List[str]:
    return [
        "Decide on a rough date and budget",
        "List 2-3 ideas for what to do",
        "Check who needs to be invited or involved",
        "Book / arrange the main thing (venue, cake, tickets)",
        "Send out the invite or confirm plans",
    ]


def _clean_room_steps(task: str) -> List[str]:
    return [
        "Set a 10-minute timer",
        "Pick up clothes and put them in the laundry basket",
        "Clear surfaces (desk, bed, floor) into one pile",
        "Sort the pile into keep / put-away / trash",
        "Put away the 'keep' items",
    ]


def _bill_payment_steps(task: str) -> List[str]:
    return [
        "Open the billing app or website",
        "Check the exact amount due",
        "Choose the payment method",
        "Complete the payment",
        "Save or screenshot the confirmation",
    ]


def _bank_finance_check_steps(task: str) -> List[str]:
    return [
        "Open your banking app",
        "Log in / authenticate",
        "Check the balance or relevant statement",
        "Note down anything that needs follow-up",
    ]


def _laundry_steps(task: str) -> List[str]:
    return [
        "Gather dirty clothes into the laundry basket",
        "Sort into colors / whites if needed",
        "Start the washing machine or head to the laundromat",
        "Hang or transfer clothes to the dryer",
        "Fold and put away once dry",
    ]


def _dishes_kitchen_steps(task: str) -> List[str]:
    return [
        "Clear food scraps into the trash",
        "Rinse the dishes",
        "Wash with soap, one item at a time",
        "Rinse and place in the drying rack",
        "Wipe down the counter",
    ]


def _wardrobe_declutter_steps(task: str) -> List[str]:
    return [
        "Set a 15-minute timer",
        "Take everything out of one section/shelf",
        "Sort into keep / donate / trash piles",
        "Put the 'keep' pile back neatly",
        "Bag up the 'donate' pile for drop-off",
    ]

def _repair_steps(task: str):

    return [

        "Identify what is not working",

        "Check for simple fixes first",

        "Search for possible solutions",

        "Decide if professional repair is needed",

        "Take the item for repair or fix it",

        "Test it after the repair",

    ]
def _singing_steps(task):

    return [

        "Do a 5-minute vocal warm-up",

        "Practice one song or exercise",

        "Work on the most difficult section",

        "Sing the full piece once",

        "Record yourself and listen back",

    ]
def _dance_steps(task: str):

    return [

        "Do a quick body warm-up",

        "Review the choreography once",

        "Practice the hardest section",

        "Run the full routine",

        "Record and review your performance",

    ]
def _coding_steps(task: str):
    return [
        "Open the project",
        "Identify the next feature or bug",
        "Write a small piece of code",
        "Test the change",
        "Save and commit your work",
    ]
def _music_steps(task: str):

    return [

        "Open your DAW",

        "Listen to the latest version",

        "Work on one section only",

        "Export a draft",

        "Take notes for the next session",

    ]
def _acting_steps(task: str):

    return [

        "Read the scene once",

        "Highlight key emotions",

        "Practice the lines aloud",

        "Perform the scene fully",

        "Record and review your performance",

    ]
import re

def _water_steps(task):

    match = re.search(r'(\d+(?:\.\d+)?)', task)

    liters = match.group(1) if match else "2"

    return [
        "Fill a water bottle",
        "Drink the first glass of water",
        "Keep the bottle nearby",
        "Drink water throughout the day",
        f"Finish the {liters}-liter goal before bedtime",
    ]
def _instrument_steps(task):

    return [

        "Take out the instrument",

        "Do a 5-minute warm-up exercise",

        "Practice scales or fundamentals",

        "Work on one difficult section",

        "Play the full piece once",

        "Put the instrument away",

    ]
KEYWORD_RULES = [
    (["presentation", "ppt", "slides", "slide deck"], _presentation_steps),
    (["assignment", "report", "thesis", "essay", "research paper", "asgn"], _assignment_report_steps),
    (["exam", "viva", "quiz", "test prep", "revise", "revision"], _exam_viva_steps),
    (["doctor", "dentist", "physio", "clinic", "checkup", "chkup", "appt", "appointment", "vaccine", "vaccination"], _doctor_appt_steps),
    (["gym", "workout", "yoga", "exercise"], _gym_workout_steps),
    (["meds", "medication", "prescription", "vitamins", "pills"], _meds_steps),
    (["buy", "order", "purchase", "groceries", "shopping"], _shopping_buy_steps),
    (["fix", "bug", "deploy", "issue", "ticket", "error"], _bug_fix_deploy_steps),
    (["meeting", "standup", "call with", "1:1", "demo"], _meeting_steps),
    (["docs", "documentation", "update api"], _docs_report_steps),
    (["call mom", "call dad", "text", "msg", "message", "call grandma", "reply"], _call_text_steps),
    (["birthday", "plan trip", "plan a trip", "surprise", "anniversary", "plan birthday"], _plan_event_steps),
    (["clean room", "clean my room", "declutter phone", "tidy room"], _clean_room_steps),
    (["bill", "wifi bill", "electricity bill", "emi", "premium", "rent"], _bill_payment_steps),
    (["bank balance", "bank account", "credit score", "salary", "investment", "itr", "tax"], _bank_finance_check_steps),
    (["laundry", "wash clothes", "dry clean"], _laundry_steps),
    (["dishes", "wash dishes", "kitchen counter", "fridge"], _dishes_kitchen_steps),
    (["wardrobe", "closet", "declutter"], _wardrobe_declutter_steps),
    (["repair", "fix laptop", "broken laptop", "repair laptop"], _repair_steps),
    (["sing", "singing", "vocal practice"], _singing_steps),
    (["dance", "dancing", "choreography"], _dance_steps),
    (["code", "coding", "programming", "project","python","api","feature","project","django","java","c++","c","bug","HTML","CSS","A.I.",], _coding_steps),
    (["music", "produce", "beat", "mix", "master"], _music_steps),
    (["acting", "rehearse", "scene", "monologue"], _acting_steps),
    (["water", "hydration", "drink water"], _water_steps),
    (["guitar", "piano", "violin", "drums"], _instrument_steps),
]


# ---------------------------------------------------------------------------
# 2. CATEGORY-LEVEL FALLBACK TEMPLATES
# ---------------------------------------------------------------------------
# Used when no keyword rule matches. Still concrete, just more generic.

CATEGORY_FALLBACKS = {
    "Study": lambda task: [
        f"Gather the materials needed for '{task}'",
        "Break the topic into 2-3 smaller chunks",
        "Spend 10 minutes on the first chunk",
        "Take a short break, then continue with the next chunk",
        "Do a quick review of what you covered",
    ],
    "Health": lambda task: [
        f"Decide what's needed to do '{task}'",
        "Set a specific time today to do it",
        "Prepare anything required (booking, equipment, supplies)",
        "Do the task",
        "Set a reminder if it needs to be repeated",
    ],
    "Shopping": lambda task: [
        "Write down exactly what you want to buy",
        "Decide where to buy it from",
        "Make the purchase",
        "Put the item(s) away when you get them",
    ],
    "Professional": lambda task: [
        f"Re-read what '{task}' actually requires",
        "Break it into the first concrete sub-step",
        "Block 25 minutes to work on it",
        "Do the first sub-step",
        "Note what's left for next time",
    ],
    "Personal": lambda task: [
        f"Decide the smallest first step for '{task}'",
        "Set aside a few minutes today for it",
        "Do that first step",
        "Note anything to follow up on",
    ],
    "Finance": lambda task: [
        "Open the relevant app, site, or document",
        "Check the exact amount / numbers involved",
        "Take the required action (pay, transfer, review)",
        "Save a confirmation or note the result",
    ],
    "Household": lambda task: [
        "Set a 10-minute timer",
        f"Do the first small part of '{task}'",
        "Keep going until the timer ends",
        "Put away anything used",
    ],
}

UNIVERSAL_FALLBACK = lambda task: [
    f"Decide the very first physical step for '{task}'",
    "Set a timer for 10-15 minutes",
    "Do just that first step",
    "Check what's left and decide the next step",
    "Mark it done or schedule the remainder",
]


# ---------------------------------------------------------------------------
# 3. PUBLIC API
# ---------------------------------------------------------------------------
def generate_breakdown(task: str, category: Optional[str] = None) -> List[str]:
    """
    Generate 3-7 ADHD-friendly subtasks for the given task.

    Args:
        task: Raw task text as entered by the user, e.g. "Prepare compiler
              design presentation".
        category: Predicted category (e.g. "Study"). Used only as a fallback
              when no keyword rule matches.

    Returns:
        A list of 3-7 short, actionable step strings.
    """
    text = task.lower()

    for keywords, step_fn in KEYWORD_RULES:
        if any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in keywords):
            steps = step_fn(task)
            return _clamp_steps(steps)

    if category and category in CATEGORY_FALLBACKS:
        steps = CATEGORY_FALLBACKS[category](task)
        return _clamp_steps(steps)

    return _clamp_steps(UNIVERSAL_FALLBACK(task))


def _clamp_steps(steps: List[str]) -> List[str]:
    """Ensure the step count always stays within the 3-7 ADHD-friendly range."""
    if len(steps) < 3:
        steps = steps + ["Review and confirm the task is complete"]
    return steps[:7]


# ---------------------------------------------------------------------------
# Quick manual test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tests = [
        ("Prepare compiler design presentation", "Study"),
        ("pay credit card bill asap", "Finance"),
        ("buy milk n eggs", "Shopping"),
        ("client meeting 3pm tmrw", "Professional"),
        ("clean the bathroom", "Household"),
        ("call mom", "Personal"),
        ("blood test next week", "Health"),
        ("some totally novel task xyz", "Personal"),
    ]
    for task, cat in tests:
        print(f"\nTask: {task}  (category: {cat})")
        for i, step in enumerate(generate_breakdown(task, cat), 1):
            print(f"  {i}. {step}")
