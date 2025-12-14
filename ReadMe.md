# ⚽ LaLiga Monte Carlo Predictor

**Author:** Carlos Torregrosa Alcayde 
**Project:** Heuristics 
**Date:** 2025

---

## 📖 Project Overview
This project applies **Data Science**, **Discrete-Event Simulation (DES)**, and **Monte Carlo methods** to predict the final outcomes of the LaLiga season.

Unlike standard predictions that rely on averages, this application simulates the remaining matches of the season **2,000 times** ("parallel universes") to quantify risk. It allows us to answer probabilistic questions such as:
* *"What is the exact probability of Levante avoiding relegation?"*
* *"How likely is Valencia C.F. to qualify for Europe?"*

## 🚀 Live Demo
https://montecarlo-laligapredictions-efdqsrx9jffcsn6d34kpc5.streamlit.app/

## 📊 Key Features
* **Stochastic Simulation:** The season is modeled matchday-by-matchday using `SimPy`. Every game is treated as a discrete event where the winner is determined stochastically based on historical win rates.
* **Risk Analysis:** Calculates the exact probability (0-100%) of critical events like **relegation** or **European qualification**.
* **Visual Analytics:** Interactive dashboards showing:
    * **Rank Distribution:** How often a team finishes in each position.
    * **Safety Thresholds:** The gap between a team's projected points and the "safety line."
    * **Scenario Analysis:** "Best Case" vs "Worst Case" scenarios.
* **Interactive Controls:** Users can select any team and adjust the simulation depth (up to 5,000 runs) via the sidebar.

## 🛠️ Technologies Used
* **Python 3.9+**
* **[SimPy](https://simpy.readthedocs.io/):** For process-based discrete-event simulation (DES).
* **[Streamlit](https://streamlit.io/):** For the interactive web interface.
* **[Matplotlib](https://matplotlib.org/):** For statistical data visualization.
* **Pandas:** For data manipulation and tabular reporting.

## ⚙️ Installation & Usage

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/](https://github.com/)[your-username]/laliga-monte-carlo.git
    cd laliga-monte-carlo
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**
    ```bash
    streamlit run app.py
    ```

4.  **View the App**
    The app will open automatically in your browser at `http://localhost:8501`.

## 🧠 Methodology: How it Works

1.  **Data Initialization:** The app loads current standings (Points, Wins, Draws, Losses) as the starting state.
2.  **Probability Calculation:** For each team, we calculate win/draw/loss probabilities ($P_{win}, P_{draw}, P_{loss}$) based on their current form.
3.  **Discrete-Event Simulation (SimPy):**
    * The simulation treats the remaining season as a time-based process.
    * It steps through time (`yield env.timeout(1)`), simulating one matchday at a time until Matchday 38.
    * Outcomes are determined stochastically using `random.choices()` weighted by the team's form.
4.  **Monte Carlo Aggregation:** We run this process $N$ times (default: 1,000). By aggregating the results of these thousands of simulations, we build a statistical distribution of final rankings, allowing us to quantify risk with high precision.
