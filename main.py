import tkinter as tk
from tkinter import simpledialog
import instaloader
import pandas as pd
from datetime import datetime
import os
import time
import random


def get_followers_followings(username, password, target_username):
    L = instaloader.Instaloader()

    session_file = os.path.join(".sessions", f"{username}_session")
    if os.path.exists(session_file):
        L.load_session_from_file(username, session_file)
    else:

        def input_2fa_code():
            return simpledialog.askstring("2FA", "Enter 2FA code:")

        try:
            L.login(username, password)
        except instaloader.TwoFactorAuthRequiredException:
            L.two_factor_login(input_2fa_code())

        L.save_session_to_file(session_file)

    profile = instaloader.Profile.from_username(L.context, target_username)

    time.sleep(random.uniform(1, 3))

    followers = [follower.username for follower in profile.get_followers()]
    followings = [following.username for following in profile.get_followees()]

    return followers, followings


def save_to_csv(data, filename):
    df = pd.DataFrame(data, columns=["username"])
    df.to_csv(filename, index=False)


def load_from_csv(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)["username"].tolist()
    else:
        return []


def compare_data(old_data, new_data):
    added = list(set(new_data) - set(old_data))
    removed = list(set(old_data) - set(new_data))
    return added, removed


def save_changes_with_timestamp(changes, target_username, user_type, change_type):
    if changes:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        directory = os.path.join("targets", target_username)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, f"{change_type}_{user_type}.csv")
        df = pd.DataFrame(changes, columns=["username"])
        df["checked_at"] = timestamp
        if os.path.exists(filename):
            df.to_csv(filename, mode="a", header=False, index=False)
        else:
            df.to_csv(filename, index=False)


def insert_usernames(text_widget, label, usernames):
    text_widget.insert(tk.END, label + "\n")
    for username in usernames:
        text_widget.insert(tk.END, username + "\n")
    text_widget.insert(tk.END, "\n")


def execute_and_display():
    username = entry_username.get()
    password = entry_password.get()
    target_username = entry_target_username.get()

    directory = os.path.join("targets", target_username)
    os.makedirs(directory, exist_ok=True)
    followers_file = os.path.join(directory, "followers.csv")
    followings_file = os.path.join(directory, "followings.csv")

    old_followers = load_from_csv(followers_file)
    old_followings = load_from_csv(followings_file)

    followers, followings = get_followers_followings(
        username, password, target_username
    )

    new_followers, removed_followers = compare_data(old_followers, followers)
    new_followings, removed_followings = compare_data(old_followings, followings)

    result_text.delete("1.0", tk.END)
    if new_followers:
        insert_usernames(result_text, "New Followers:", new_followers)
    else:
        result_text.insert(tk.END, "No new followers.\n\n")

    if removed_followers:
        insert_usernames(result_text, "Removed Followers:", removed_followers)
    else:
        result_text.insert(tk.END, "No removed followers.\n\n")

    if new_followings:
        insert_usernames(result_text, "New Followings:", new_followings)
    else:
        result_text.insert(tk.END, "No new followings.\n\n")

    if removed_followings:
        insert_usernames(result_text, "Removed Followings:", removed_followings)
    else:
        result_text.insert(tk.END, "No removed followings.\n")

    save_to_csv(followers, followers_file)
    save_to_csv(followings, followings_file)

    save_changes_with_timestamp(new_followers, target_username, "followers", "added")
    save_changes_with_timestamp(
        removed_followers, target_username, "followers", "removed"
    )
    save_changes_with_timestamp(new_followings, target_username, "followings", "added")
    save_changes_with_timestamp(
        removed_followings, target_username, "followings", "removed"
    )


root = tk.Tk()
root.title("Instagram Follower and Following Checker")


tk.Label(root, text="Instagram Username").grid(row=0, column=0)
entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1)

tk.Label(root, text="Instagram Password").grid(row=1, column=0)
entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1)

tk.Label(root, text="Target Username").grid(row=2, column=0)
entry_target_username = tk.Entry(root)
entry_target_username.grid(row=2, column=1)

button_check = tk.Button(root, text="Check", command=execute_and_display)
button_check.grid(row=3, column=0, columnspan=2)


result_text = tk.Text(root, height=20, width=50)
result_text.grid(row=4, column=0, columnspan=2)


root.mainloop()