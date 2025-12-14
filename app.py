import streamlit as st
import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION & DATA ---
st.set_page_config(page_title="LaLiga Monte Carlo Predictor", layout="wide")

def get_initial_standings():
    # Helper to get a fresh copy of data
    return [
        {"name": "Barcelona", "pj": 17, "pts": 43, "w": 14, "d": 1, "l": 2},
        {"name": "Real Madrid", "pj": 16, "pts": 36, "w": 11, "d": 3, "l": 2},
        {"name": "Villarreal", "pj": 15, "pts": 35, "w": 11, "d": 2, "l": 2},
        {"name": "Atlético Madrid", "pj": 17, "pts": 34, "w": 10, "d": 4, "l": 3},
        {"name": "RCD Espanyol", "pj": 16, "pts": 30, "w": 9, "d": 3, "l": 4},
        {"name": "Real Betis", "pj": 15, "pts": 24, "w": 6, "d": 6, "l": 3},
        {"name": "Athletic", "pj": 17, "pts": 23, "w": 7, "d": 2, "l": 8},
        {"name": "Celta de Vigo", "pj": 16, "pts": 22, "w": 5, "d": 7, "l": 4},
        {"name": "Sevilla", "pj": 16, "pts": 20, "w": 6, "d": 2, "l": 8},
        {"name": "Getafe", "pj": 16, "pts": 20, "w": 6, "d": 2, "l": 8},
        {"name": "Elche C. F.", "pj": 16, "pts": 19, "w": 4, "d": 7, "l": 5},
        {"name": "Alavés", "pj": 15, "pts": 18, "w": 5, "d": 3, "l": 7},
        {"name": "Rayo Vallecano", "pj": 15, "pts": 17, "w": 4, "d": 5, "l": 6},
        {"name": "R.C.D. Mallorca", "pj": 16, "pts": 17, "w": 4, "d": 5, "l": 7},
        {"name": "Real Sociedad", "pj": 16, "pts": 16, "w": 4, "d": 4, "l": 8},
        {"name": "Osasuna", "pj": 16, "pts": 15, "w": 4, "d": 3, "l": 9},
        {"name": "Valencia C. F.", "pj": 16, "pts": 15, "w": 3, "d": 6, "l": 7},
        {"name": "Girona", "pj": 16, "pts": 15, "w": 3, "d": 6, "l": 7},
        {"name": "Real Oviedo", "pj": 16, "pts": 10, "w": 2, "d": 4, "l": 10},
        {"name": "Levante", "pj": 15, "pts": 9, "w": 2, "d": 3, "l": 10},
    ]

# --- 2. LOGIC FUNCTIONS ---
def get_probabilities(team):
    total = team['w'] + team['d'] + team['l']
    if total == 0: return 0.33, 0.33, 0.34
    return team['w']/total, team['d']/total, team['l']/total

def season_process(env, team_data):
    """Simulates one team's season"""
    p_win, p_draw, p_loss = get_probabilities(team_data)
    
    while team_data['pj'] < 38:
        yield env.timeout(1)
        result = random.choices(['W', 'D', 'L'], weights=[p_win, p_draw, p_loss])[0]
        if result == 'W': team_data['pts'] += 3
        elif result == 'D': team_data['pts'] += 1
        team_data['pj'] += 1

def run_monte_carlo(target_team_name, num_simulations):
    """Runs the full simulation loop"""
    
    results = {
        'ranks': [],
        'points': [],
        'relegated': 0,
        'survived': 0,
        'europe': 0
    }
    
    # Progress bar for UX
    progress_bar = st.progress(0)
    
    for i in range(num_simulations):
        env = simpy.Environment()
        season_standings = get_initial_standings() # Reset data
        
        # Run processes
        for team in season_standings:
            env.process(season_process(env, team))
        env.run()
        
        # Sort Table
        season_standings.sort(key=lambda x: (x['pts'], x['w']), reverse=True)
        
        # Extract stats for target team
        for rank, team in enumerate(season_standings, 1):
            if team['name'] == target_team_name:
                results['ranks'].append(rank)
                results['points'].append(team['pts'])
                
                if rank <= 6: results['europe'] += 1
                if rank >= 18: results['relegated'] += 1
                else: results['survived'] += 1
                break
        
        # Update progress every 10%
        if i % (num_simulations // 10) == 0:
            progress_bar.progress((i + 1) / num_simulations)
            
    progress_bar.progress(1.0)
    return results

# --- 3. STREAMLIT UI ---
st.title("⚽ LaLiga Monte Carlo Simulator")
st.markdown("Predict the destiny of your team using **Stochastic Simulation**.")

# Sidebar Controls
with st.sidebar:
    st.header("Settings")
    teams_list = [t['name'] for t in get_initial_standings()]
    selected_team = st.selectbox("Choose a Team:", teams_list, index=teams_list.index("Levante"))
    
    n_sims = st.slider("Number of Simulations:", min_value=100, max_value=5000, value=1000, step=100)
    
    start_btn = st.button("Run Simulation", type="primary")

# Main Area Logic
if start_btn:
    with st.spinner(f"Simulating {n_sims} seasons for {selected_team}..."):
        data = run_monte_carlo(selected_team, n_sims)
        
    # --- Metrics Section ---
    prob_safe = (data['survived'] / n_sims) * 100
    prob_rel = (data['relegated'] / n_sims) * 100
    prob_eur = (data['europe'] / n_sims) * 100
    avg_rank = sum(data['ranks']) / len(data['ranks'])
    best_rank = min(data['ranks'])
    worst_rank = max(data['ranks'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Survival Probability", f"{prob_safe:.1f}%", delta_color="normal")
    col2.metric("Relegation Probability", f"{prob_rel:.1f}%", delta_color="inverse")
    col3.metric("Europe Probability", f"{prob_eur:.1f}%")
    col4.metric("Projected Rank", f"{avg_rank:.1f}")

    # --- Charts Section ---
    st.divider()
    
    # 1. Rank Distribution Plot
    fig, ax = plt.subplots(figsize=(10, 4))
    counts, bins, patches = ax.hist(data['ranks'], bins=range(1, 22), align='left', rwidth=0.8, edgecolor='black')
    
    # Color coding the bars
    for i, patch in enumerate(patches):
        rank = bins[i]
        if rank <= 6: patch.set_facecolor('#4CAF50') # Green (Europe)
        elif rank >= 18: patch.set_facecolor('#F44336') # Red (Relegation)
        else: patch.set_facecolor('#FFC107') # Yellow (Mid-table)
            
    ax.set_title(f"Final Rank Distribution for {selected_team} ({n_sims} simulations)")
    ax.set_xlabel("League Position")
    ax.set_ylabel("Frequency")
    ax.set_xticks(range(1, 21))
    st.pyplot(fig)
    
    # --- Detailed Stats Table ---
    st.subheader("Detailed Outcomes")
    st.write(f"In **{n_sims}** simulations, **{selected_team}** outcomes were:")
    
    df_stats = pd.DataFrame({
        "Outcome": ["Relegated (18-20)", "Safe (7-17)", "Europe (1-6)"],
        "Count": [data['relegated'], data['survived'] - data['europe'], data['europe']],
        "Percentage": [f"{prob_rel:.2f}%", f"{prob_safe - prob_eur:.2f}%", f"{prob_eur:.2f}%"]
    })
    st.table(df_stats)
    
    st.info(f"🏆 **Best Case Scenario:** Finished **{best_rank}th** position.\n\n"
            f"💀 **Worst Case Scenario:** Finished **{worst_rank}th** position.")

else:
    st.info("👈 Select a team in the sidebar and click **Run Simulation** to start.")
