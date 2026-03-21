import numpy as np
import pandas as pd
import streamlit as st
from collections import Counter

# Local
#df = pd.read_csv("/Users/acer1/Downloads/team_avgs2026.csv", header = None)
df = pd.read_csv("team_avgs2026.csv", header = None)
df = df.loc[1:]
df = df.rename(columns = {0: "team", 1: "PPG", 2: "PAPG"})


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


st.title("March Madness Monte Carlo Simulator")

first_team_choice = st.selectbox(
    "Select First Team",
    options = df["team"].unique(),
    index = None, # Optional: starts with no option selected
    placeholder = "Select a team..."
)

if first_team_choice:
    first_team_df = df[df["team"] == first_team_choice]
    team1 = first_team_choice
else:
    st.write("Please select a team to simulate.")


second_team_choice = st.selectbox(
    "Select Second Team",
    options = df["team"].unique(),
    index = None, # Optional: starts with no option selected
    placeholder = "Select a second team..."
)

if second_team_choice:
    second_team_df = df[df["team"] == second_team_choice]
    team2 = second_team_choice
else:
    st.write("Please select a team to simulate.")

n_sim = st.slider("Number of simulations", 100, 1000, 10)

if st.button("Run Simulation"):
    _, _, results = sim_game(team1, team2, df, n_sim)
    
    # convert to percentages
    winner_array = np.array(results)
    winner_array = winner_array == team1
    print(winner_array)

    probs = {team1: round(sum(winner_array) / len(winner_array), 2), team2: round(1 - (sum(winner_array) / len(winner_array)), 2)}
    #total = sum(results.values())
    #probs = {k: v / total for k, v in results.items()}
    
    st.write("Win Probabilities")
    st.dataframe(probs)