# 🛰️ OrbitGuard — Space Debris Detection & Collision Avoidance AI

**AI-2 · ONE HACK 2026 · Team AURONYX**

Live Demo: [orbitguard-ai2.streamlit.app](https://orbitguard-ai2-dacgx3lfcdq5dctmcp9on6.streamlit.app)

---

## 👥 Team

**Team Name:** AURONYX

| Name | Role |
|---|---|
| **Kalyani Kriti** (Team Lead) | Maneuver logic, visualization, demo & presentation |
| Chetan Prasad | Data pipeline, propagation, risk-scoring engine |

---

## 📌 Problem Statement

**AI-2: Space Debris Detection & Collision Avoidance AI**
*Aerospace / Orbital Mechanics + AI*

The growing debris field in Earth orbit creates real collision risk for active satellites. Assessing that risk requires physics-based orbit propagation as a baseline, with an additional layer to flag genuinely dangerous close approaches and suggest a response — not just raw trajectory math.

---

## 🚀 What We Built

OrbitGuard is an end-to-end AI-assisted system that:

1. **Ingests real orbital data** — pulls live TLE (Two-Line Element) data from CelesTrak's public feed for 5 tracked objects (defunct calibration spheres and test satellites — genuine debris-class objects, not just active satellites).
2. **Propagates trajectories** — uses SGP4, the industry-standard propagation model, via the Skyfield library, to project each object's position over a 72-hour window sampled every 2 minutes.
3. **Detects and scores conjunctions** — checks every pair of tracked objects for close approaches, and computes a risk score combining normalized miss-distance and relative velocity, classified into LOW / MEDIUM / HIGH / CRITICAL tiers.
4. **Recommends an avoidance maneuver** — for the highest-risk conjunction, searches across radial and along-track burn directions, 3 delta-v magnitudes, and 3 lead times using the Clohessy-Wiltshire relative-motion equations, and selects the candidate that maximizes resulting miss-distance.
5. **Visualizes everything live** — an interactive dashboard with an animated 3D orbital theater (play/pause), a ranked conjunction risk table, before/after maneuver impact cards, and a distance-over-time chart with threshold and closest-approach markers.

---

## 🧠 Tech Stack

- **Python 3**
- **Streamlit** — interactive dashboard / demo interface
- **Skyfield** (SGP4 propagation)
- **NumPy** — orbital mechanics calculations
- **Pandas** — risk table data handling
- **Plotly** — 3D orbital visualization & 2D distance charts
- **CelesTrak** — public, live TLE data source

---

## 📊 Core Methodology

### Risk Score
```
risk_score = 0.7 × (1 − miss_distance / threshold) + 0.3 × min(1, relative_speed / 15)
```
A screening heuristic — **not** a certified probability of collision. A rigorous probability-of-collision (Pc) calculation would require position-covariance data that public TLEs do not provide. We chose transparency over a falsely precise-looking number.

### Maneuver Model
Uses the **Clohessy-Wiltshire equations** — the standard model for relative motion between nearby orbiting objects — to evaluate the effect of a small impulsive delta-v burn applied before closest approach. We search across:
- Direction: radial / along-track
- Sign: outward / inward (or forward / backward)
- Delta-v: 1, 3, 5 m/s
- Lead time: 15, 30, 60 minutes before closest approach

...and select whichever candidate produces the largest increase in miss-distance. Propellant cost is estimated using the Tsiolkovsky rocket equation, assuming a ~100 kg satellite with 230s specific impulse.

---

## ⚠️ Known Limitations

We believe an honest limitations statement is more valuable than an overconfident claim:

- **Risk score is a heuristic**, not a certified probability of collision (Pc).
- **Maneuver model is simplified** (CW relative-motion equations), not a full numerical re-propagation with thrust integrated into SGP4.
- **Assumes the flagged object is maneuverable** — for real uncontrolled debris, the maneuver would need to be applied to the other, controllable object in the pair.
- **SGP4 accuracy degrades** the further propagation moves from the TLE epoch; our 72-hour window is chosen to stay within SGP4's reasonable-accuracy range.
- **Currently tracks 5 fixed objects** rather than the full ~16,000+ object catalog, due to the 8-hour hackathon scope. The pairwise conjunction check is O(n²), so scaling further would need a coarse pre-filter (e.g. orbital-shell binning) before fine-grained distance checks.

---

## 🖥️ Running Locally

```bash
git clone https://github.com/<your-username>/orbitguard-ai2.git
cd orbitguard-ai2

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 📁 Repository Structure

```
orbitguard-ai2/
├── app.py                 # Main Streamlit application
├── tle_active.txt          # Cached TLE data snapshot from CelesTrak
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 📖 Data Source & Attribution

- **TLE data:** [CelesTrak](https://celestrak.org) (public, active-satellites group)
- **Propagation:** SGP4 via [Skyfield](https://rhodesmill.org/skyfield/)
- **Maneuver model:** Clohessy-Wiltshire relative motion equations

---

Built for **ONE HACK 2026**, Hackers Cult × NSUT Delhi.
