import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def scrape_transfermark(url_page):
    response = requests.get(url_page, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        list_clubs = soup.find_all(class_="hauptlink no-border-links")
        list_links = list(map(lambda i: i.find('a').get('href'), list_clubs))

        df = pd.DataFrame(columns=["Name", "Date of birth", "Nationality", "Team", "League"])

        for link in list_links[:10]:
            # Get the DataFrame with updated data for the current league
            df = get_players("https://www.transfermarkt.com" + link, df)
        
        print("Data appended successfully.")
        return df

    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None

def get_players(url_page, df):
    response = requests.get(url_page, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        team = str(soup.find(class_="data-header__headline-wrapper data-header__headline-wrapper--oswald").text).strip()
        league = str(soup.find(class_="data-header__club").find("a").text).strip()

        players = []

        list_players = soup.find(class_="items").find("tbody").find_all('tr')

        for player_row in list_players:
            player_name = player_row.find(class_="inline-table")

            if player_name:
                player_name = player_name.find(class_="data-link").find("a").text

            zentriert = player_row.find_all(class_='zentriert')

            if len(zentriert) != 0:
                date_birth = zentriert[1].text
                nationality = zentriert[2].find(class_="flaggenrahmen").get("title")
                date_birth = str(re.sub(r"\([^)]*\)", "", date_birth)).rstrip()

                players.append({
                    "Name": player_name,
                    "Date of birth": datetime.strptime(date_birth, "%b %d, %Y").date(),
                    "Nationality": nationality,
                    "Team": team,
                    "League": league
                })

        df = df.append(players, ignore_index=True)
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")

    return df

# Create an empty DataFrame to hold the combined data
all_leagues_df = pd.DataFrame(columns=["Name", "Date of birth", "Nationality", "Team", "League"]) 

# Scrape data for each league and store it in separate DataFrames
spain_league = scrape_transfermark("https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1")
premier_league = scrape_transfermark("https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1")
france_league = scrape_transfermark("https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1")
german_league = scrape_transfermark("https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1")
italian_league = scrape_transfermark("https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1")

# Concatenate all the DataFrames into a new DataFrame
all_leagues_df = pd.concat([all_leagues_df, spain_league, premier_league, france_league, german_league, italian_league], ignore_index=True)

# Print or use the new DataFrame as needed
all_leagues_df.to_csv('football_players_data.csv', index=False)

