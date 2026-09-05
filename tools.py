from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import re
from datetime import datetime


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# TAVILY CLIENT
# ==========================================

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


# ==========================================
# CURRENT DATE
# ==========================================

CURRENT_DATE = datetime(2026, 9, 5)


# ==========================================
# 1. SEARCH COMPETITIONS
# ==========================================

def search_competitions(query: str, max_results: int = 5):

    """
    Search for individual current/upcoming
    competition and hackathon pages.
    """

    improved_query = f"""
    {query}

    current upcoming 2026 hackathon competition
    registration open
    applications open
    deadline
    official competition page

    IMPORTANT:
    Find individual competition pages.

    Do NOT return:
    - hackathon listing pages
    - article pages
    - blog posts
    - GitHub lists
    - Facebook groups
    - social media posts
    - "top hackathons" pages
    - "upcoming hackathons" list pages
    - directories
    - category pages
    """

    try:

        response = tavily.search(
            query=improved_query,
            search_depth="advanced",
            max_results=max_results
        )

    except Exception as e:

        return {
            "error": str(e),
            "results": []
        }


    results = []

    seen_urls = set()


    # ======================================
    # BLOCKED URL PATTERNS
    # ======================================

    blocked_url_patterns = [

        "/c/",
        "/category/",
        "/categories/",
        "/tag/",
        "/tags/",
        "/blog/",
        "/blogs/",
        "/articles/",
        "/article/",
        "/news/",
        "/hackathons",
        "/hackathon-list",
        "/top-hackathons",
        "/best-hackathons",

        "allhackathons.com",
        "facebook.com",
        "instagram.com",
        "linkedin.com",
        "youtube.com",

    ]


    # ======================================
    # BLOCKED CONTENT SIGNALS
    # ======================================

    listing_phrases = [

        "top hackathons",
        "top upcoming hackathons",
        "upcoming hackathons",
        "list of hackathons",
        "list of competitions",
        "hackathons in india",
        "hackathons and competitions",
        "centralized list",
        "complete list",
        "directory of",
        "collection of hackathons",
        "best hackathons",
        "hackathons you should",
        "hackathons to participate",
        "multiple hackathons",
        "various hackathons",
        "hackathon calendar"

    ]


    # ======================================
    # PROCESS RESULTS
    # ======================================

    for result in response.get("results", []):

        url = result.get(
            "url",
            ""
        )

        title = result.get(
            "title",
            ""
        )

        content = result.get(
            "content",
            ""
        )


        if not url:
            continue


        # ==================================
        # DUPLICATES
        # ==================================

        if url in seen_urls:
            continue


        url_lower = url.lower()

        title_lower = title.lower()

        content_lower = content.lower()


        # ==================================
        # BLOCK BAD URLS
        # ==================================

        if any(
            pattern in url_lower
            for pattern in blocked_url_patterns
        ):

            continue


        # ==================================
        # BLOCK LISTING CONTENT
        # ==================================

        combined_text = (
            title_lower
            + " "
            + content_lower
        )


        if any(
            phrase in combined_text
            for phrase in listing_phrases
        ):

            continue


        # ==================================
        # REQUIRE COMPETITION SIGNAL
        # ==================================

        competition_words = [

            "hackathon",
            "competition",
            "challenge",
            "contest"

        ]


        if not any(
            word in combined_text
            for word in competition_words
        ):

            continue


        # ==================================
        # ADD VALID RESULT
        # ==================================

        seen_urls.add(url)


        results.append({

            "title": title,

            "url": url,

            "content": content

        })


    return results

    """
    Search for individual current/upcoming
    competition and hackathon pages.
    """

    improved_query = f"""
    {query}

    current upcoming 2026 hackathon competition
    registration open
    applications open
    deadline
    official competition page

    IMPORTANT:
    Find individual competition pages.
    Do NOT return general hackathon listing pages,
    category pages, article lists, directories,
    or "top hackathons" pages.
    """

    try:

        response = tavily.search(
            query=improved_query,
            search_depth="advanced",
            max_results=max_results
        )

    except Exception as e:

        return {
            "error": str(e),
            "results": []
        }


    results = []

    seen_urls = set()


    # ======================================
    # PAGES WE DON'T WANT
    # ======================================

    blocked_patterns = [

        "/c/",
        "/category/",
        "/categories/",
        "/tag/",
        "/tags/",
        "/blog/",
        "/blogs/",
        "/articles/",
        "/article/",
        "/news/",
        "/hackathons",
        "/hackathon-list",
        "/top-hackathons",
        "/best-hackathons",
        "allhackathons.com"

    ]


    # ======================================
    # PROCESS RESULTS
    # ======================================

    for result in response.get("results", []):

        url = result.get(
            "url",
            ""
        )

        title = result.get(
            "title",
            ""
        )

        content = result.get(
            "content",
            ""
        )


        if not url:
            continue


        # ==================================
        # REMOVE DUPLICATES
        # ==================================

        if url in seen_urls:
            continue


        # ==================================
        # REMOVE LISTING / ARTICLE PAGES
        # ==================================

        url_lower = url.lower()

        blocked = any(
            pattern in url_lower
            for pattern in blocked_patterns
        )

        if blocked:
            continue


        # ==================================
        # REQUIRE COMPETITION SIGNAL
        # ==================================

        combined_text = (
            title + " " + content
        ).lower()


        competition_words = [

            "hackathon",
            "competition",
            "challenge",
            "contest"

        ]


        if not any(
            word in combined_text
            for word in competition_words
        ):
            continue


        seen_urls.add(url)


        results.append({

            "title": title,

            "url": url,

            "content": content

        })


    return results


# ==========================================
# 2. DATE PARSER
# ==========================================

def parse_date(date_string):

    formats = [

        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y-%m-%d"

    ]


    cleaned = date_string.strip()


    for fmt in formats:

        try:

            return datetime.strptime(
                cleaned,
                fmt
            )

        except ValueError:

            continue


    return None


# ==========================================
# 3. FETCH COMPETITION
# ==========================================

def fetch_competition(url: str):

    try:

        response = requests.get(

            url,

            timeout=10,

            headers={
                "User-Agent": "Mozilla/5.0"
            }

        )

        response.raise_for_status()


        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        # ==================================
        # REMOVE UNNECESSARY HTML
        # ==================================

        for element in soup(
            [
                "script",
                "style",
                "nav",
                "footer"
            ]
        ):

            element.decompose()


        # ==================================
        # EXTRACT PAGE TEXT
        # ==================================

        text = soup.get_text(
            separator=" ",
            strip=True
        )


        text = text[:12000]


        lower_text = text.lower()


        # ==================================
        # DATE PATTERNS
        # ==================================

        date_patterns = [

            r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",

            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}\b",

            r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",

            r"\b\d{1,2}/\d{1,2}/\d{4}\b",

            r"\b\d{4}-\d{2}-\d{2}\b"

        ]


        # ==================================
        # FIND ALL DATES
        # ==================================

        all_dates = []


        for pattern in date_patterns:

            matches = re.findall(

                pattern,

                text,

                flags=re.IGNORECASE

            )


            all_dates.extend(matches)


        all_dates = list(
            dict.fromkeys(all_dates)
        )


        # ==================================
        # DEADLINE KEYWORDS
        # ==================================

        deadline_keywords = [

            "deadline",
            "registration closes",
            "registration close",
            "applications close",
            "application closes",
            "application close",
            "submission deadline",
            "last date to register",
            "last date for registration",
            "register by",
            "submit by",
            "registration deadline"

        ]


        deadline_candidates = []


        # ==================================
        # SEARCH FOR DATES NEAR DEADLINE
        # ==================================

        for keyword in deadline_keywords:

            start = 0


            while True:

                index = lower_text.find(
                    keyword,
                    start
                )


                if index == -1:
                    break


                context = text[
                    max(0, index - 100):
                    min(len(text), index + 250)
                ]


                for date_pattern in date_patterns:

                    matches = re.findall(

                        date_pattern,

                        context,

                        flags=re.IGNORECASE

                    )


                    for match in matches:

                        if match not in deadline_candidates:

                            deadline_candidates.append(
                                match
                            )


                start = index + len(keyword)


        # ==================================
        # PARSE DEADLINE
        # ==================================

        deadline = None


        for candidate in deadline_candidates:

            parsed = parse_date(candidate)


            if parsed:

                deadline = parsed

                break


        # ==================================
        # EXPIRED WORDS
        # ==================================

        expired_words = [

            "registration closed",
            "applications closed",
            "registration has closed",
            "applications have closed",
            "deadline has passed",
            "event has ended",
            "event ended",
            "past event",
            "competition ended",
            "hackathon ended"

        ]


        explicitly_expired = any(

            word in lower_text

            for word in expired_words

        )


        # ==================================
        # DETERMINE EXPIRY
        # ==================================

        is_expired = explicitly_expired


        if deadline and deadline < CURRENT_DATE:

            is_expired = True


        # ==================================
        # RETURN RESULT
        # ==================================

        return {

            "url": url,

            "content": text,

            "found_dates": all_dates,

            "deadline":
                deadline.strftime("%Y-%m-%d")
                if deadline
                else None,

            "is_expired": is_expired,

            "explicitly_expired":
                explicitly_expired

        }


    except Exception as e:

        return {

            "url": url,

            "content": "",

            "found_dates": [],

            "deadline": None,

            "is_expired": True,

            "explicitly_expired": True,

            "error": str(e)

        }


# ==========================================
# 4. MATCH COMPETITION
# ==========================================

def match_competition(

    user_skills: list,

    user_interests: list,

    experience_level: str,

    preference: str,

    competition_text: str,

    is_expired: bool = False,

    deadline: str = None

):


    # ======================================
    # HARD EXPIRY PROTECTION
    # ======================================

    if is_expired:

        return {

            "score": 0,

            "matched_skills": [],

            "matched_interests": [],

            "reasons": [],

            "blocked": True,

            "block_reason":
                "Competition is expired.",

            "deadline": deadline

        }


    # ======================================
    # NORMAL MATCHING
    # ======================================

    text = competition_text.lower()


    score = 0

    reasons = []


    # ======================================
    # 1. SKILLS — 40 POINTS
    # ======================================

    matched_skills = []


    for skill in user_skills:

        skill_lower = skill.lower().strip()


        if skill_lower in text:

            matched_skills.append(skill)


    if user_skills:

        skill_score = int(

            (

                len(matched_skills)

                /

                len(user_skills)

            ) * 40

        )


        score += skill_score


    if matched_skills:

        reasons.append(

            "Matching skills: "

            + ", ".join(matched_skills)

        )


    # ======================================
    # 2. INTERESTS — 25 POINTS
    # ======================================

    matched_interests = []


    for interest in user_interests:

        interest_lower = (
            interest.lower().strip()
        )


        if interest_lower in text:

            matched_interests.append(
                interest
            )


    if user_interests:

        interest_score = int(

            (

                len(matched_interests)

                /

                len(user_interests)

            ) * 25

        )


        score += interest_score


    if matched_interests:

        reasons.append(

            "Matching interests: "

            + ", ".join(matched_interests)

        )


    # ======================================
    # 3. EXPERIENCE — 20 POINTS
    # ======================================

    level = experience_level.lower()


    if level in text:

        score += 20


        reasons.append(

            f"Suitable for "
            f"{experience_level} level"

        )


    elif level == "beginner":

        beginner_words = [

            "beginner",
            "student",
            "students",
            "all levels",
            "novice",
            "no experience",
            "first-time"

        ]


        if any(

            word in text

            for word in beginner_words

        ):

            score += 15


            reasons.append(

                "Appears suitable for "
                "beginners/students"

            )


    # ======================================
    # 4. PARTICIPATION — 15 POINTS
    # ======================================

    pref = preference.lower()


    if pref == "any":

        score += 15


        reasons.append(

            "No participation "
            "mode restriction"

        )


    elif pref in text:

        score += 15


        reasons.append(

            f"Matches preference: "
            f"{preference}"

        )


    # ======================================
    # FINAL RESULT
    # ======================================

    return {

        "score": min(score, 100),

        "matched_skills":
            matched_skills,

        "matched_interests":
            matched_interests,

        "reasons":
            reasons,

        "blocked": False,

        "deadline":
            deadline

    }