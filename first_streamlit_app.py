import numpy as np
import pandas as pd
from collections import Counter


def sim_game(team1, team2, stats_df, n_sim):
    winners = []
    for i in range(n_sim):
        t1_PPG = stats_df[stats_df["team"] == team1]["PPG"]
        t1_PAPG = stats_df[stats_df["team"] == team1]["PAPG"]

        t2_PPG = stats_df[stats_df["team"] == team2]["PPG"]
        t2_PAPG = stats_df[stats_df["team"] == team2]["PAPG"]
    
        t1_points = (np.random.normal(t1_PPG, 12) + np.random.normal(t2_PAPG, 12)) / 2
        t2_points = (np.random.normal(t2_PPG, 12) + np.random.normal(t1_PAPG, 12)) / 2

        if t1_points > t2_points:
            winner = team1
        else:
            winner = team2

        winners.append(winner)
    
    return t1_points, t2_points, winners

test_df = pd.DataFrame({"team": ["Gonzaga", "Mississippi Valley St"], "PPG": [85.1, 64.2], "PAPG": [66, 83]})

import streamlit as st

st.title("March Madness Monte Carlo Simulator")

n_sim = st.slider("Number of simulations", 100, 1000, 10)

if st.button("Run Simulation"):
    team1 = "Gonzaga"
    team2 = "Mississippi Valley St"
    _, _, results = sim_game(team1, team2, test_df, n_sim)
    
    # convert to percentages
    winner_array = np.array(results)
    winner_array = winner_array == team1
    print(winner_array)

    probs = {team1: round(sum(winner_array) / len(winner_array), 2), team2: round(1 - (sum(winner_array) / len(winner_array)), 2)}
    #total = sum(results.values())
    #probs = {k: v / total for k, v in results.items()}
    
    st.write("Championship Probabilities")
    st.dataframe(probs)