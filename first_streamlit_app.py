import numpy as np
import pandas as pd
import streamlit as st
from collections import Counter

# Local
#df = pd.read_csv("/Users/acer1/Downloads/team_avgs2026.csv", header = None)
df = pd.read_csv("team_avgs2026.csv", header = None)
df = df.loc[1:]
df = df.rename(columns = {0: "team", 1: "PPG", 2: "PAPG"})
winner = ""

import base64

def display_logo(team, is_winner):
    st.empty()
    border_style = "5px solid green" if is_winner else "none"
    
    with open(f"logos/{team}.png", "rb") as f:
        img_bytes = f.read()
        encoded = base64.b64encode(img_bytes).decode()
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{encoded}"
                 style="border: {border_style}; border-radius: 10px; padding: 1px; width:300px;">
        </div>
        """,
        unsafe_allow_html=True
    )


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
    options = df["team"].sort_values(ascending = True).unique(),
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
    options = df["team"].sort_values(ascending = True).unique(),
    index = None, # Optional: starts with no option selected
    placeholder = "Select a second team..."
)

if second_team_choice:
    second_team_df = df[df["team"] == second_team_choice]
    team2 = second_team_choice

    col1, col2, col3 = st.columns(3)
    with col1:
        team1_placeholder = st.empty()
        #display_logo(team1, team1 == winner)
    with col2:
        #st.write("vs")
        st.markdown("<h3 style='text-align: center;'>vs</h3>", unsafe_allow_html = True, text_alignment = "center")
    with col3:
        team2_placeholder = st.empty()
        #display_logo(team1, team2 == winner)

    team1_placeholder.image(f"logos/{team1}.png")
    team2_placeholder.image(f"logos/{team2}.png")

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
    winner = max(probs, key = probs.get)
    #with col1:
    #    team1_placeholder.markdown(
    #        display_logo(team1, team1 == winner),
    #        unsafe_allow_html=True
    #    )
    #with col3:
    #    team2_placeholder.markdown(
    #        display_logo(team2, team2 == winner),
    #        unsafe_allow_html=True
    #    )
    with team1_placeholder:
        display_logo(team1, team1 == winner)
    with team2_placeholder:
        display_logo(team2, team2 == winner)
    
    st.write("Win Probabilities")
    st.dataframe(probs)