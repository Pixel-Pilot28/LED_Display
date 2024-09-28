import os
import json
import time
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from threading import Thread
from bs4 import BeautifulSoup

class SoccerApp:
    def __init__(self, display_controller):
        self.display_controller = display_controller
        self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 7)
        self.update_interval = 10  # seconds
        self.schedule_cache_file = "/home/pi/Projects/Display/py_cache/sportscache.json"
        self.icon_path = "/home/pi/Projects/Display/sport_logos"
        self.favorite_teams = [
            {'name': 'Arsenal', 'league': 'eng.1'},
            {'name': 'St. Pauli', 'league': 'ger.2'},
            {'name': 'USA Mens', 'league': 'fifa.world'},
            {'name': 'USA Womens', 'league': 'fifa.world'}
        ]
        self.running = False
        self.team_info = self.get_team_info()
    
    def fetch_team_abbreviations(self):
        url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/teams"
        try:
            response = requests.get(url)
            response.raise_for_status()
            teams_data = response.json()
            return {team['id']: team['abbreviation'] for team in teams_data['teams']}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching team abbreviations: {e}")
            return {}
            
    def get_team_info(self):
        team_info = {}
        for team in self.favorite_teams:
            league = team['league']
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/teams"
            response = requests.get(url)
            data = response.json()
            for t in data['sports'][0]['leagues'][0]['teams']:
                if t['team']['displayName'] == team['name']:
                    team_info[team['name']] = {
                        'id': t['team']['id'],
                        'slug': t['team']['slug'],
                        'abbreviation': t['team']['abbreviation'],
                        'league': league
                    }
                    break
        return team_info

    def fetch_schedule(self, team):
        team_data = self.team_info.get(team['name'])
        if not team_data:
            print(f"Error: Team data not found for {team['name']}")
            return []

        url = f"https://www.espn.com/soccer/team/fixtures/_/id/{team_data['id']}/{team_data['slug']}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            fixtures = []
            for row in soup.select('.Table__TR'):
                cells = row.select('.Table__TD')
                if len(cells) >= 6:
                    date = cells[0].get_text()
                    home = cells[1].get_text()
                    away = cells[3].get_text()
                    time = cells[4].get_text()
                    competition = cells[5].get_text()
                    if time == "TBD":
                        time = "12:00 PM"
                    fixtures.append({
                        'date': date,
                        'time': time,
                        'home': home,
                        'competition': competition,
                        'away': away
                    })
            return fixtures
        except requests.exceptions.RequestException as e:
            print(f"Error fetching schedule for {team['name']}: {e}")
            return []

    def update_schedule_cache(self):
        current_time = datetime.now()
        if os.path.exists(self.schedule_cache_file):
            with open(self.schedule_cache_file, 'r') as f:
                cache = json.load(f)
                last_updated = datetime.strptime(cache.get('last_updated', '1970-01-01T00:00:00'), '%Y-%m-%dT%H:%M:%S')
                if (current_time - last_updated).total_seconds() < 86400:  # less than 24 hours
                    return cache

        schedule = {'last_updated': current_time.strftime('%Y-%m-%dT%H:%M:%S')}
        for team in self.favorite_teams:
            schedule[team['name']] = self.fetch_schedule(team)

        with open(self.schedule_cache_file, 'w') as f:
            json.dump(schedule, f)
        return schedule

    def fetch_live_scores(self, league):
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching live scores: {e}")
            return {}

    def draw_text(self, draw, text, font, position, color=(255, 255, 255)):
        draw.text(position, text, font=font, fill=color)

    def load_team_icon(self, team_abbr):
        icon_path = f"{self.icon_path}/{team_abbr}.bmp"
        print(f"Loading icon from: {icon_path}")  # Debug statement
        try:
            icon = Image.open(icon_path).convert("RGBA")
            icon = icon.resize((8, 8), Image.LANCZOS)  # Resize to 8x8 pixels
            return icon
        except IOError:
            print(f"Error loading icon for {team_abbr} at {icon_path}")
            return None

    def render_game_info(self, draw, game, y_offset):
        home_abbr = self.team_info.get(game['home'], {}).get('abbreviation', game['home'][:3]).upper()
        away_abbr = self.team_info.get(game['away'], {}).get('abbreviation', game['away'][:3]).upper()
        score = game.get('score', 'TBD')
        status = game['status']

        # Load and display team icons
        home_icon = self.load_team_icon(home_abbr)
        away_icon = self.load_team_icon(away_abbr)
        if home_icon:
            draw.bitmap((2, y_offset), home_icon)
        if away_icon:
            draw.bitmap((48, y_offset), away_icon)

        # Position elements based on the screen size
        self.draw_text(draw, home_abbr, self.font_small, (2, y_offset + 10))
        self.draw_text(draw, away_abbr, self.font_small, (48, y_offset + 10))
        self.draw_text(draw, score, self.font_large, (28, y_offset + 8))
        self.draw_text(draw, status, self.font_small, (15, y_offset))

    def get_time_str(self, time_str):
        try:
            time_obj = datetime.strptime(time_str, '%I:%M %p')
            return time_obj.strftime('%I:%M %p')[-1]
        except ValueError:
            return time_str

    def get_status(self, game_date, game_time):
        current_time = datetime.now()
        game_datetime_str = f"{game_date} {game_time}"
        try:
            game_datetime = datetime.strptime(game_datetime_str, '%a, %b %d %I:%M %p')
            if game_datetime > current_time:
                return game_datetime.strftime('%m/%d %I:%M %p')[:-2] + self.get_time_str(game_time)
            elif game_datetime < current_time and "TBD" not in game_datetime_str:
                return "In Progress"
            else:
                return "Final"
        except ValueError:
            return "TBD"

    def run(self):
        self.running = True
        while self.running:
            try:
                schedule = self.update_schedule_cache()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

                for team in self.favorite_teams:
                    games = schedule.get(team['name'], [])[:3]
                    for game in games:
                        image = Image.new("RGB", (64, 32))
                        draw = ImageDraw.Draw(image)
                        draw.fontmode = "1"  # Single pixel wide lines for text

                        status = self.get_status(game['date'], game['time'])
                        game_info = {
                            'home': game['home'],
                            'away': game['away'],
                            'score': game.get('result', 'TBD'),
                            'status': status
                        }

                        self.render_game_info(draw, game_info, 0)
                        self.display_controller.set_image(image)
                        time.sleep(3)

                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in SoccerApp: {e}")
                time.sleep(60)

    def stop(self):
        self.running = False

# Example usage
if __name__ == "__main__":
    # Assuming `display_controller` is already defined and initialized
    soccer_app = SoccerApp(display_controller)
    app_thread = Thread(target=soccer_app.run)
    app_thread.start()

    # To stop the app, call `soccer_app.stop()`
    # soccer_app.stop()
    # app_thread.join()
