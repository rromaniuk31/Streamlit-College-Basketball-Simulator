import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
from collections import Counter

df = pd.read_csv("team_avgs2026.csv", header = None)
df = df.loc[1:]
df = df.rename(columns = {0: "team", 1: "PPG", 2: "PAPG", 3: "PPG_STD", 4: "PAPG_STD"})
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
    t1_all_points = []
    t2_all_points = []
    for i in range(n_sim):
        t1_PPG = stats_df[stats_df["team"] == team1]["PPG"]
        t1_PAPG = stats_df[stats_df["team"] == team1]["PAPG"]
        t1_PPG_std = stats_df[stats_df["team"] == team1]["PPG_STD"]
        t1_PAPG_std = stats_df[stats_df["team"] == team1]["PAPG_STD"]

        t2_PPG = stats_df[stats_df["team"] == team2]["PPG"]
        t2_PAPG = stats_df[stats_df["team"] == team2]["PAPG"]
        t2_PPG_std = stats_df[stats_df["team"] == team2]["PPG_STD"]
        t2_PAPG_std = stats_df[stats_df["team"] == team2]["PAPG_STD"]
    
        t1_points = (np.random.normal(t1_PPG, t1_PPG_std) + np.random.normal(t2_PAPG, t2_PAPG_std)) / 2
        t2_points = (np.random.normal(t2_PPG, t2_PPG_std) + np.random.normal(t1_PAPG, t1_PAPG_std)) / 2

        t1_all_points.append(t1_points)
        t2_all_points.append(t2_points)

        if t1_points > t2_points:
            winner = team1
        else:
            winner = team2

        winners.append(winner)
    
    return t1_points, t2_points, winners, t1_all_points, t2_all_points


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
    with col2:
        st.markdown("<h3 style='text-align: center;'>vs</h3>", unsafe_allow_html = True, text_alignment = "center")
    with col3:
        team2_placeholder = st.empty()

    team1_placeholder.image(f"logos/{team1}.png")
    team2_placeholder.image(f"logos/{team2}.png")

else:
    st.write("Please select a team to simulate.")

n_sim = st.slider("Number of simulations", 100, 10000, 1000)

if st.button("Run Simulation"):
    _, _, results, t1_all_points, t2_all_points = sim_game(team1, team2, df, n_sim)
    
    # convert to percentages
    winner_array = np.array(results)
    winner_array = winner_array == team1
    print(winner_array)

    probs = {team1: round(sum(winner_array) / len(winner_array), 2), team2: round(1 - (sum(winner_array) / len(winner_array)), 2)}
    winner = max(probs, key = probs.get)
 
    with team1_placeholder:
        display_logo(team1, team1 == winner)
    with team2_placeholder:
        display_logo(team2, team2 == winner)
    
    st.write("Win Probabilities")
    st.dataframe(probs)

    #t1_all_points_df = pd.DataFrame(t1_all_points, columns = ["Points"])
    #t1_all_points_df["Points_Bins"] = t1_all_points_df["Points"].transform(lambda x: pd.cut(x, bins=15, labels=False))
    #mean_df = t1_all_points_df.groupby(["Points_Bins"])["Points"].mean().reset_index()
    #t1_all_points_df = t1_all_points_df.merge(mean_df, on = "Points_Bins")
    #t1_all_points_df["Points_y"] = round(t1_all_points_df["Points_y"], 2)
    #bin_counts = (
    #t1_all_points_df.groupby("Points_y")
    #                .size()
    #                .reset_index(name="count")
    #                .sort_values("Points_y")
    #)

    #chart = alt.Chart(bin_counts).mark_bar().encode(
    #    x=alt.X("Points_y:O", title="Points Bin"),
    #    y=alt.Y("count:Q", title="Count")
    #)


    # Display the chart in the Streamlit app
    #st.altair_chart(chart, use_container_width=True)

    t1_df = pd.DataFrame(t1_all_points, columns = ["points"])
    t1_df["Team"] = "Team 1"
    t2_df = pd.DataFrame(t2_all_points, columns = ["points"])
    t2_df["Team"] = "Team 2"
    both_points = pd.concat([t1_df, t2_df])
    bins_col = both_points["points"].transform(lambda x: pd.cut(x, bins = 15, labels = False))
    both_points["Bins"] = bins_col
    bin_means = both_points.groupby(["Bins"])["points"].mean().reset_index()
    both_points = both_points.merge(bin_means, on = "Bins")

    #fig, ax = plt.subplots()

    #ax.hist([both_points[both_points["Team"] == "Team 1"]["points_x"], both_points[both_points["Team"] == "Team 2"]["points_x"]], bins=15, stacked=True, color=['cyan', 'Purple'], edgecolor='black')[2]

    combined = np.concatenate([both_points[both_points["Team"] == "Team 1"]["points_x"], both_points[both_points["Team"] == "Team 2"]["points_x"]])
    print("team1", both_points[both_points["Team"] == team1]["points_x"])
    print("team2", both_points[both_points["Team"] == team2]["points_x"])
    bins = np.linspace(combined.min(), combined.max(), 26)  # 25 bins

    fig, ax = plt.subplots()

    plt.hist(both_points[both_points["Team"] == "Team 1"]["points_x"], bins=bins, alpha=0.5, label=team1)
    plt.hist(both_points[both_points["Team"] == "Team 2"]["points_x"], bins=bins, alpha=0.5, label=team2)

    plt.xlabel("Points")
    plt.ylabel("Frequency")
    plt.legend()
    
    st.pyplot(fig)