import streamlit as st
import numpy as np
import random
import time
import os
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(page_title="AMAGF Governance Control Room", layout="wide")

st.title("AMAGF – Agentic Military AI Governance Framework")

# --------------------------------------------------
# GEMINI SETUP
# --------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-flash"

model = genai.GenerativeModel(MODEL_NAME)

# --------------------------------------------------
# EMBEDDING MODEL (for IAS)
# --------------------------------------------------

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------------------------------
# SIDEBAR PROMPT CONTROL
# --------------------------------------------------

st.sidebar.header("Mission Prompt Control")

mission_prompts = [
    "Monitor the river and report suspicious activity",
    "Secure the border area and detect threats",
    "Surveil enemy movement near the checkpoint",
    "Coordinate drones for disaster response",
    "Search for hostile vehicles in the region"
]

selected_prompt = st.sidebar.selectbox("Mission Scenario", mission_prompts)

custom_prompt = st.sidebar.text_area("Or Enter Custom Mission Command")

if custom_prompt.strip() != "":
    HUMAN_COMMAND = custom_prompt
else:
    HUMAN_COMMAND = selected_prompt

st.sidebar.success(f"Active Command:\n{HUMAN_COMMAND}")

# --------------------------------------------------
# DRONE AGENT
# --------------------------------------------------

class DroneAgent:

    def __init__(self, agent_id):

        self.agent_id = agent_id
        self.belief = ""
        self.confidence = round(random.uniform(0.6,0.9),2)

    def reason(self, command):

        try:

            prompt = f"""
            You are autonomous drone agent {self.agent_id}.

            Interpret the command and explain your operational belief.

            Command: {command}

            Give a short interpretation.
            """

            response = model.generate_content(prompt)

            self.belief = response.text[:200]

        except:

            self.belief = "LLM error"

        return self.belief

# --------------------------------------------------
# SWARM
# --------------------------------------------------

class DroneSwarm:

    def __init__(self,n_agents=8):

        self.agents = [DroneAgent(i) for i in range(n_agents)]

    def run_reasoning(self,command):

        beliefs = []

        for agent in self.agents:

            belief = agent.reason(command)

            beliefs.append(belief)

        return beliefs

# --------------------------------------------------
# IAS (Interpretive Alignment Score)
# --------------------------------------------------

def compute_IAS(command,beliefs):

    cmd_vec = embed_model.encode([command])

    distances = []

    for belief in beliefs:

        vec = embed_model.encode([belief])

        sim = cosine_similarity(cmd_vec,vec)[0][0]

        d = 1 - sim

        distances.append(d)

    IAS = 1 - np.mean(distances)

    return max(0,min(IAS,1))

# --------------------------------------------------
# CIR (Correction Impact Ratio)
# --------------------------------------------------

def compute_CIR():

    delta_actual = random.uniform(0.2,1.2)

    delta_intended = random.uniform(0.5,1.0)

    CIR = delta_actual / delta_intended

    return CIR

# --------------------------------------------------
# EDI (Epistemic Divergence)
# --------------------------------------------------

def compute_EDI():

    return random.uniform(0,0.6)

# --------------------------------------------------
# IRREVERSIBILITY MODEL
# --------------------------------------------------

action_scores = {
    "scan_area":0.1,
    "deploy_drone":0.3,
    "track_target":0.4,
    "lock_weapon":0.8
}

I_B = 2.0

def compute_irreversibility():

    actions = random.choices(list(action_scores.values()),k=5)

    I_C = sum(actions)

    return I_C

# --------------------------------------------------
# SYNCHRONIZATION FRESHNESS
# --------------------------------------------------

SF_MAX = 30

def compute_SF():

    return random.randint(0,40)

# --------------------------------------------------
# SWARM COHERENCE
# --------------------------------------------------

def compute_SCS():

    coherent = random.randint(4,8)

    return coherent/8

# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

def normalize_metrics(IAS,CIR,EDI,I_C,SF,SCS):

    n1 = IAS
    n2 = min(CIR,1)
    n3 = 1-EDI
    n4 = max(0,1 - I_C/I_B)
    n5 = max(0,1 - SF/SF_MAX)
    n6 = SCS

    return [n1,n2,n3,n4,n5,n6]

# --------------------------------------------------
# GOVERNANCE POLICY
# --------------------------------------------------

def governance_state(CQS):

    if CQS > 0.8:
        return "Normal Operation"

    elif CQS > 0.6:
        return "Elevated Monitoring"

    elif CQS > 0.4:
        return "Restricted Actions"

    elif CQS > 0.2:
        return "Minimal Autonomy"

    else:
        return "Safe Mode"

# --------------------------------------------------
# BELIEF RESET
# --------------------------------------------------

def belief_reset(belief,command,lam=0.6):

    return f"Reset towards operator command: {command}"

# --------------------------------------------------
# RUN SIMULATION
# --------------------------------------------------

if st.button("Run Mission Simulation"):

    swarm = DroneSwarm()

    with st.spinner("Drone swarm reasoning..."):

        beliefs = swarm.run_reasoning(HUMAN_COMMAND)

    # METRICS

    IAS = compute_IAS(HUMAN_COMMAND,beliefs)

    CIR = compute_CIR()

    EDI = compute_EDI()

    I_C = compute_irreversibility()

    SF = compute_SF()

    SCS = compute_SCS()

    normalized = normalize_metrics(IAS,CIR,EDI,I_C,SF,SCS)

    CQS = min(normalized)

    state = governance_state(CQS)

    # --------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------

    st.header("Governance Metrics")

    c1,c2,c3 = st.columns(3)

    c1.metric("IAS",round(IAS,3))
    c2.metric("CIR",round(CIR,3))
    c3.metric("EDI",round(EDI,3))

    c4,c5,c6 = st.columns(3)

    c4.metric("Irreversibility Used",round(I_C,3))
    c5.metric("Sync Freshness",SF)
    c6.metric("Swarm Coherence",round(SCS,3))

    st.subheader("Control Quality Score")

    st.metric("CQS",round(CQS,3))

    st.subheader("Governance State")

    st.success(state)

    # --------------------------------------------------
    # DRONE BELIEFS
    # --------------------------------------------------

    st.subheader("Drone Beliefs")

    for agent in swarm.agents:

        st.write(
            f"Drone {agent.agent_id} | Confidence: {agent.confidence} | Belief: {agent.belief}"
        )

    # --------------------------------------------------
    # CORRECTIVE GOVERNANCE
    # --------------------------------------------------

    if CQS < 0.4:

        st.warning("Corrective governance activated")

        corrected = []

        for belief in beliefs:

            corrected.append(belief_reset(belief,HUMAN_COMMAND))

        st.write("Beliefs reset toward operator command")
