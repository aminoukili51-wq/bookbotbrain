from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import os

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
print("ENV TEST:", os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# -----------------------------
# Enable CORS (frontend fix)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # laat alle websites toe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Data Models
# -----------------------------
class Score(BaseModel):
    team_goals: int
    opponent_goals: int

class Shots(BaseModel):
    player: int
    team: int
    opponents: int

class BoostUsage(BaseModel):
    average: float
    wasted: float
    big_pads_taken: int
    small_pads_taken: int

class Positioning(BaseModel):
    time_in_attack: float
    time_in_defense: float
    third_man_time: float
    double_commits: int
    back_post_rotations: float

class Speed(BaseModel):
    slow_speed: float
    medium_speed: float
    supersonic: float

class Pressure(BaseModel):
    offense_time: float
    defense_time: float
    demos_taken: int
    demos_given: int

class Mistakes(BaseModel):
    overcommits: int
    missed_boosts: int
    bad_challenges: int

class GameStats(BaseModel):
    game_length: int
    score: Score
    shots: Shots
    boost_usage: BoostUsage
    positioning: Positioning
    speed: Speed
    pressure: Pressure
    mistakes: Mistakes

# -----------------------------
# AI Feedback Generator
# -----------------------------
def generate_ai_feedback(stats, win_chance):
    prompt = f"""
    Jij bent een professionele Rocket League coach.
    Hier zijn de stats van een speler:

    {stats}

    De berekende win chance was: {round(win_chance * 100)}%.

    Geef in het Nederlands:
    - 3 sterke punten
    - 3 verbeterpunten
    - 2 tips voor de volgende match
    Hou het kort en duidelijk.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content

# -----------------------------
# API Endpoint
# -----------------------------
@app.post("/analyze")
def analyze_game(stats: GameStats):
    try:
        win_chance = (
            (stats.score.team_goals - stats.score.opponent_goals) * 0.1 +
            (stats.shots.player / max(stats.shots.opponents, 1)) * 0.3 +
            (1 - stats.boost_usage.wasted) * 0.2 +
            stats.positioning.back_post_rotations * 0.2 +
            (1 - stats.mistakes.overcommits * 0.05)
        )

        win_chance = max(0, min(win_chance, 1))

        feedback = generate_ai_feedback(stats.dict(), win_chance)

        return {
            "win_chance": round(win_chance * 100),
            "feedback": feedback
        }

    except Exception as e:
        return {"error": str(e)}
