import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import base64
import matplotlib.pyplot as plt
from collections import Counter

# Get data and rename columns
df = pd.read_csv("team_avgs2026.csv", header = None)
df = df.loc[1:]
df = df.rename(columns = {0: "team", 1: "PPG", 2: "PAPG", 3: "PPG_STD", 4: "PAPG_STD", 5: "KP_PPG", 6: "KP_PAPG"})
winner = ""

# Display logo function
def display_logo(team, is_winner):
    st.empty()
    # If there is no winner yet, then no border
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
        unsafe_allow_html = True
    )

# Sim game based on opponent adjusted PPG and PAPG
def sim_game(team1, team2, stats_df, n_sim):
    # Intialize lists
    winners = []
    t1_all_points = []
    t2_all_points = []
    # Loop through games
    for i in range(n_sim):
        # Get means and standard deviations
        t1_PPG = stats_df[stats_df["team"] == team1]["KP_PPG"]
        t1_PAPG = stats_df[stats_df["team"] == team1]["KP_PAPG"]
        t1_PPG_std = stats_df[stats_df["team"] == team1]["PPG_STD"]
        t1_PAPG_std = stats_df[stats_df["team"] == team1]["PAPG_STD"]

        t2_PPG = stats_df[stats_df["team"] == team2]["KP_PPG"]
        t2_PAPG = stats_df[stats_df["team"] == team2]["KP_PAPG"]
        t2_PPG_std = stats_df[stats_df["team"] == team2]["PPG_STD"]
        t2_PAPG_std = stats_df[stats_df["team"] == team2]["PAPG_STD"]
    
        # Simulate each teams points
        t1_points = (np.random.normal(t1_PPG, t1_PPG_std) + np.random.normal(t2_PAPG, t2_PAPG_std)) / 2
        t2_points = (np.random.normal(t2_PPG, t2_PPG_std) + np.random.normal(t1_PAPG, t1_PAPG_std)) / 2

        t1_all_points.append(t1_points)
        t2_all_points.append(t2_points)

        # Check who won
        if t1_points > t2_points:
            winner = team1
        else:
            winner = team2

        winners.append(winner)
    
    return t1_points, t2_points, winners, t1_all_points, t2_all_points


st.title("March Madness Simulator")

# Select first team
first_team_choice = st.selectbox(
    "Select First Team",
    options = df["team"].sort_values(ascending = True).unique(),
    index = None,
    placeholder = "Select a team..."
)

if first_team_choice:
    first_team_df = df[df["team"] == first_team_choice]
    team1 = first_team_choice
else:
    st.write("Please select a team to simulate.")

# Select second team
second_team_choice = st.selectbox(
    "Select Second Team",
    options = df["team"].sort_values(ascending = True).unique(),
    index = None, 
    placeholder = "Select a second team..."
)

if second_team_choice:
    second_team_df = df[df["team"] == second_team_choice]
    team2 = second_team_choice

    # With both teams selected display logos
    col1, col2, col3 = st.columns(3)
    with col1:
        team1_placeholder = st.empty()
    with col2:
        st.markdown("<h3 style='text-align: center;'>vs</h3>", unsafe_allow_html = True, text_alignment = "center")
    with col3:
        team2_placeholder = st.empty()

    team1_placeholder.image(f"logos/{team1}.png")
    team2_placeholder.image(f"logos/{team2}.png")

else:
    st.write("Please select a team to simulate.")

# Simulation number slider
n_sim = st.slider("Number of simulations", 100, 10000, 1000)

# Run simulation button
if st.button("Run Simulation"):
    _, _, results, t1_all_points, t2_all_points = sim_game(team1, team2, df, n_sim)

    winner_array = np.array(results)
    winner_array = winner_array == team1

    # convert wins to percentages
    probs = {team1: round(sum(winner_array) / len(winner_array), 2), team2: round(1 - (sum(winner_array) / len(winner_array)), 2)}
    winner = max(probs, key = probs.get)
 
    with team1_placeholder:
        display_logo(team1, team1 == winner)
    with team2_placeholder:
        display_logo(team2, team2 == winner)
    
    # Display the win probabilities
    st.write("Win Probabilities")
    st.dataframe(probs)

    # Create bins for plotting
    t1_df = pd.DataFrame(t1_all_points, columns = ["points"])
    t1_df["Team"] = "Team 1"
    t2_df = pd.DataFrame(t2_all_points, columns = ["points"])
    t2_df["Team"] = "Team 2"
    both_points = pd.concat([t1_df, t2_df])
    bins_col = both_points["points"].transform(lambda x: pd.cut(x, bins = 15, labels = False))
    both_points["Bins"] = bins_col
    bin_means = both_points.groupby(["Bins"])["points"].mean().reset_index()
    both_points = both_points.merge(bin_means, on = "Bins")

    combined = np.concatenate([both_points[both_points["Team"] == "Team 1"]["points_x"], both_points[both_points["Team"] == "Team 2"]["points_x"]])
    bins = np.linspace(combined.min(), combined.max(), 26)  # 25 bins

    fig, ax = plt.subplots()

    plt.hist(both_points[both_points["Team"] == "Team 1"]["points_x"], bins = bins, alpha = 0.5, label = team1)
    plt.hist(both_points[both_points["Team"] == "Team 2"]["points_x"], bins = bins, alpha = 0.5, label = team2)

    plt.xlabel("Points")
    plt.ylabel("Frequency")
    plt.legend()
    
    st.pyplot(fig)

    # Complute mean PPG
    t1_mean_ppg = sum(t1_all_points) / len(t1_all_points)
    t2_mean_ppg = sum(t2_all_points) / len(t2_all_points)
    teams_sum = t1_mean_ppg + t2_mean_ppg
    ppg_df = pd.DataFrame({team1: t1_mean_ppg, team2: t2_mean_ppg, "Total": teams_sum})
    ppg_df.index = ["PPG"]
    st.dataframe(ppg_df, hide_index = False)