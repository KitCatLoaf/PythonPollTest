import os
import requests
import json
import time



VOTE_RECORD_FILE = "vote_record.json"
def load_vote_record():
    if not os.path.exists(VOTE_RECORD_FILE):
        return {}
    with open(VOTE_RECORD_FILE, "r") as f: # r opens in read mode, f converts to python dict
        return json.load(f)
    
def save_vote_record(record):
    with open(VOTE_RECORD_FILE, "w") as f: # w opens in write mode
        json.dump(record, f) # converts the record to json and writes to file

def has_voted(poll_id):
    record = load_vote_record()
    return record.get(f"poll_{poll_id}", False)

def set_voted(poll_id):
    record = load_vote_record()
    record[f"poll_{poll_id}"] = True
    save_vote_record(record)

def clear_vote_record(poll_id):
    record = load_vote_record()
    record.pop(f"poll_{poll_id}", None)
    record.pop(f"poll_{poll_id}_title", None)
    save_vote_record(record)

        
def saveTitle(poll_id, title):
    record = load_vote_record()
    if not title or title.strip() == "":
        print("ERROR: Couldn't save title to record")
        exit()
    record[f"poll_{poll_id}_title"] = title
    save_vote_record(record)

def titleMatch(poll_id):
    record = load_vote_record()
    poll = getPoll(poll_id)
    if not poll:
        return False
    return record.get(f"poll_{poll_id}_title") == poll["title"]




supabaseUrl = "https://bulqrxnaqwyivivyvsfo.supabase.co" # os.getenv("SUPABASE_URL") Deprecated code - hardcoded to run on clients.
supabaseApiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ1bHFyeG5hcXd5aXZpdnl2c2ZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNTM5NzgsImV4cCI6MjA3NjcyOTk3OH0.d1HmzZTSst_Wzb9enm66p1b7bjhdvPxx2dtQEaBmLPA" # os.getenv("SUPABASE_KEY")

headers = {
    "apikey": supabaseApiKey,
    "Authorization": f"Bearer {supabaseApiKey}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def getAndSaveTitle(poll_id):
    poll = getPoll(poll_id)
    if poll and poll.get('title'):
        saveTitle(poll_id, poll['title'])
    else:
        print("Couldn't fetch title from poll. Exiting...")
        exit()


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

def displayPoll(poll):
    print(f"Poll: {poll['title']}\nDesc: {poll['description']}")
    displayVotes(poll)

def vote(choice, poll_id):
    if choice not in ["yes", "no", "y", "n"]:
        print("Invalid Choice")
        return
    
    column = "yes_votes" if choice in ("y", "yes") else "no_votes"
    poll = getPoll(poll_id)
    if not poll:
        print("ERROR: No poll found.")
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

    if not has_voted(poll_id):
        getAndSaveTitle(poll_id)

    if not titleMatch(poll_id):
        clear_vote_record(poll_id)

    if has_voted(poll_id):
        print("You have already voted in this poll. See updated results?\n")
        answer = input("(Y/N): ").strip().lower()
        if answer not in ('y', "yes"):
            if answer == "emergencycleardata":
                if os.path.exists(VOTE_RECORD_FILE):
                 os.remove(VOTE_RECORD_FILE)
                 print("Vote record cleared.")
            print("Exiting...")
        elif answer in ('y', "yes"):
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
    getAndSaveTitle(poll_id)
    vote(user_choice, poll_id)
    if not user_choice in ["yes", "no", "y", "n"]:
        print("Exiting...")
        exit()
    set_voted(poll_id)

    poll= getPoll(poll_id)
    print("\nUpdated Votes:\n")
    displayVotes(poll)

    print("Exiting...")