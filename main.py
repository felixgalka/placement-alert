import os
import sys
import requests
import pandas as pd
import csv
import smtplib
from dotenv import load_dotenv
import datetime

load_dotenv()
API = "https://api.the-trackr.com/programmes?region=UK&industry=Technology&season=2026&type=industrial-placements"
URL = "https://app.the-trackr.com/uk-technology/industrial-placements"

res = requests.get(API, timeout=10).json()

# Get all current placements in a file
def get2026Placements(all_placements):
    for i in range(all_placements.shape[0]):
        date = all_placements.loc[i].openingDate
        if not date:
            all_placements.drop(i, axis=0, inplace=True)
    return all_placements

def getNewPlacements():
    df = pd.DataFrame(res)
    df = get2026Placements(df)
    df.sort_values(by=['openingDate'], ascending=True, inplace=True)
    df.to_csv("fresh_placements.csv", index=False)
    lines = []
    with open("fresh_placements.csv", "r") as f:
        new_count = sum(1 for l in f)
    with open("original_placements.csv", "r") as f:
        old_count = sum(1 for line in f)
    if new_count > old_count:
        lines = []
        with open("fresh_placements.csv", "r") as f:
            lines = list(csv.reader(f))
        df.to_csv("original_placements.csv", index=False) #save fresh placements to the original file
    return lines[old_count:new_count]

newPlacements = getNewPlacements()
if newPlacements:
    receiver = os.getenv('EMAIL')
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(receiver, os.getenv("GMAIL_PASS"))
    subject = f"Placement Updates {datetime.datetime.now()}"
    body = ""
    for pm in newPlacements:
        emailData = pm[1:4] #name, company, url
        body = body + f"New opportunity!: \n {emailData[1]} is hiring for {emailData[0]}. \nApply at: {emailData[2]} \n \n"
    text = f"Subject: {subject}\n\n{body}"
    server.sendmail(receiver, receiver, text)
    print("Email sent successfully")
    server.quit()
else:
    print("No new opportunity found")
