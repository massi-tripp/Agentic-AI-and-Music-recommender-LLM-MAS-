# Agentic-AI-and-Music-recommender-LLM-MAS-
This project implements a multi-agent system (MAS) for the diffusion and recommendation of music tracks. Each agent represents a user with a personalized taste profile (e.g., energy, danceability, valence, acousticness, tempo) and interacts asynchronously within a small-world social graph. Agents share songs, evaluate proposals, and adopt tracks under attention budget constraints, generating diffusion cascades and possible viral trends.

The design strictly follows the principles of classical MAS rather than building an LLM-centric orchestration. Key features include:

- Asynchronous dynamics: agents act on independent Poisson clocks.

- Structured environment: state is symbolic and auditable (adoptions, trust, saturation, history).

- Communication protocols: ACL-style messages with structured payloads.

- Metrics and reproducibility: adoption counts, Gini index, Herfindahl, ECDF exposure, cascade depth and virality, logged in JSON Lines and analyzed via Python scripts.

- Petri Net modeling: to verify safety properties and attention flow (Att–Inbox–Feed).

The LLM is used in-the-loop as a service, not as the system’s core state. It supports agents in two tasks:

1) Persuasive pitches: generating short textual claims with structured persuasion coefficients.

2) Targeting policies (optional): suggesting the next recipient of a proposal based on a structured snapshot of the local state.

We evaluate two scenarios (with and without LLM) across different network sizes. Results show a trade-off:

LLM runs achieve higher fairness and lower exposure before adoption but at the cost of significantly lower throughput due to latency and conservative gating.

Non-LLM runs generate larger cascades and higher volume, but also more inequality in adoption distribution.

This project demonstrates how to design a MAS that respects theoretical constraints from Agentic AI literature (authentic sociality, structured states, true asynchrony, reproducible metrics), offering a methodologically sound foundation for future extensions such as adaptive policies (bandits/RL), richer network topologies, and stress-test scenarios.

How to Run:
1. Clone the repository
git clone https://github.com/your-username/music-mas-llm.git
cd music-mas-llm

2. Install dependencies

We recommend using Python 3.10+ with a virtual environment:

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Configure experiment

Edit the configuration file base.yaml to set parameters such as:

n_agents (number of agents)

poisson_rate (activity rate)

attention_budget

song_csv_path (dataset path, e.g. Spotify Tracks Dataset)

llm_backend (e.g., Ollama model or disabled for no-LLM runs)

4. Run simulations

Without LLM:

python run simulation.py --config base.yaml --disable-llm


With LLM:

python run simulation.py --config base.yaml --enable-llm

5. Analyze results

All logs are stored in logs/ as JSON Lines. To generate plots and metrics:

python make_figures.py --logfile logs/run_x.jsonl
(you can also run metrics_advanced.py for some more metrics)

This will produce:

Efficiency plots (propose/adopt counts)

Lorenz curves and Gini index

Exposure distributions (ECDF)

Top-5 most adopted tracks
