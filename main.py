import os
import requests
import json
import time



VOTE_RECORD_FILE = "vote_record.json"
def load_vote_record():
    if not os.path.exists(VOTE_RECORD_FILE):
        return {}
    with open(VOTE_RECORD_FILE, "r") as f:
        return json.load(f)
def save_vote_record(record):
    with open(VOTE_RECORD_FILE, "w") as f:
        json.dump(record, f)
def has_voted(poll_id):
    record = load_vote_record()
    return record.get(f"poll_{poll_id}", False)
def set_voted(poll_id):
    record = load_vote_record()
    record[f"poll_{poll_id}"] = True
    save_vote_record(record)



supabaseUrl = "https://bulqrxnaqwyivivyvsfo.supabase.co" # os.getenv("SUPABASE_URL") Deprecated code - hardcoded to run on clients.
supabaseApiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ1bHFyeG5hcXd5aXZpdnl2c2ZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNTM5NzgsImV4cCI6MjA3NjcyOTk3OH0.d1HmzZTSst_Wzb9enm66p1b7bjhdvPxx2dtQEaBmLPA" # os.getenv("SUPABASE_KEY")

headers = {
    "apikey": supabaseApiKey,
    "Authorization": f"Bearer {supabaseApiKey}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def getPoll(poll_id=1):
    url = f"{supabaseUrl}/rest/v1/votes?id=eq.{poll_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data[0] if data else None
    print("ERROR: Failed to fetch poll: ", response.text)
    return None

def getAllPolls():
    url = f"{supabaseUrl}/rest/v1/votes"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    print("ERROR: Failed to fetch polls: ", response.text)
    return []

def getVotes():
    url = f"{supabaseUrl}/rest/v1/votes?id=eq.1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data[0] if data else None
    print("ERROR: Failed to fetch votes: ", response.text)
    return None

def displayPoll(poll):
    print(f"Poll: {poll['title']}\nDesc: {poll['description']}")
    displayVotes(poll)

def vote(choice, poll_id=1):
    if choice not in ["yes", "no"]:
        print("Invalid Choice")
        return
    
    column = "yes_votes" if choice == "yes" else "no_votes"
    poll = getPoll(poll_id)
    if not poll:
        print("Not poll found.")
        return

    new_count = poll[column] + 1
    url = f"{supabaseUrl}/rest/v1/votes?id=eq.{poll_id}"
    data = {column: new_count}

    response = requests.patch(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print(f"Voted {choice} successfully!\n")
    else:
        print(f"ERROR: Failed to update field {choice} of votes: ", response.text)

def displayVotes(poll):
    y = poll['yes_votes']
    n = poll['no_votes']
    total = y + n
    if total == 0:
        y_percent = n_percent = 0
    else:
        y_percent = round((y / total) * 100)
        n_percent = round((n / total) * 100)
    print(f"Y:{y} - N:{n}")
    print(f"{y_percent}% - {n_percent}%")

if __name__ == "__main__":
    cooldown = 5
    print("Created by @KitCatLoaf with a huge lack of sleep.. And supabase.")
    print("This app is a prototype and may break. Meant only for simple tests and close friends.")
    print("Please do not attempt to edit your save data to vote multiple times.")
    print(f"Have fun!! Running in {cooldown} second(s)..\n")
    time.sleep(cooldown)
    polls = getAllPolls()

    if not polls:
        print("No polls available. Exiting...")
        exit()

    print("Available Polls:")
    for p in polls:
        print(f"ID: {p['id']} - Title: {p['title']}")
    
    poll_id = input("Enter Poll ID to vote in:\nInput: ").strip()

    if not poll_id.isdigit():
        print("Invalid Poll ID. Exiting...")
        exit()
    poll_id = int(poll_id)

    if has_voted(poll_id):
        print("You have already voted in this poll. See updated results?\n")
        answer = input("(Y/N): ").strip().lower()
        if answer != 'y':
            exit()
        else:
            poll = getPoll(poll_id)
            if poll:
                displayPoll(poll)
            else:
                print("No poll found. Exiting...")
            exit()
    poll = getPoll(poll_id)
    if not poll:
        print("No poll found. Exiting...")
        exit()
    
    displayPoll(poll)

    user_choice = input("Enter your vote (yes/no):\nInput: ").strip().lower()
    vote(user_choice, poll_id)
    set_voted(poll_id)

    poll= getPoll(poll_id)
    print("\nUpdated Voted:\n")
    displayVotes(poll)

    print("Exiting...")