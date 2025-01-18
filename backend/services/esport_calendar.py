import requests
from datetime import datetime, timedelta
import os
import shutil

from ics import Calendar, Event
from box import Box

from config.logs import LoggerManager
from config.settings import get_settings

class EsportCalendarService:
    def __init__(self):
        # Initialize the service with configuration
        self.logging = LoggerManager()
        settings = get_settings()
        self.base_url = settings.BACK_PANDA_BASE_URL
        self.api_key = settings.BACK_PANDA_API_KEY
        self.team_ids = [
            settings.BACK_PANDA_ID_JL_LOL,
            settings.BACK_PANDA_ID_JL_VALO,
        ]
        self.static_dir = "static"  # Directory to save the .ics file
        self.ics_file_path = os.path.join(self.static_dir, "calendar.ics")  # Path to the final .ics file
        self.temp_ics_file_path = os.path.join(self.static_dir, "calendar_temp.ics")  # Temp file path for atomic update

        # Ensure the static directory exists
        os.makedirs(self.static_dir, exist_ok=True)

    def _fetch_upcoming_matches(self, team_id):
        """ Fetch upcoming match data from the PandaScore API """
        url = f"{self.base_url}/teams/{team_id}/matches?filter[status]=not_started&sort=begin_at"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        self.logging.info(f"Fetching upcoming matches from API... URL: {url}")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception if the request fails
            data = response.json()
        except requests.RequestException as e:
            self.logging.error(f"Error fetching matches: {e}")
            return []

        matches = []
        for matchjson in data:
            match = Box(matchjson)
            
            stream = next(
                (s for s in match.streams_list if s.main and s.language == 'fr'),
                next(
                    (s for s in match.streams_list if s.main),
                    None
                )
            )
            match.stream_url = stream.raw_url if stream else ""
                    
            matches.append({
                "id": f"{match.league_id}{match.tournament_id}{match.serie_id}{match.id}",
                "tournament_name": match.tournament.name,
                "tournament_slug": match.tournament.slug,
                "tournament_tier": match.tournament.tier,
                "videogame_name": match.videogame.name,
                "videogame_slug": match.videogame.slug,
                "begin_at": match.begin_at,
                "number_of_games": match.number_of_games,
                "opponents_1_acronym": match.opponents[0].opponent.acronym,
                "opponents_1_name": match.opponents[0].opponent.name,
                "opponents_1_location": match.opponents[0].opponent.location,
                "opponents_2_acronym": match.opponents[1].opponent.acronym,
                "opponents_2_name": match.opponents[1].opponent.name,
                "opponents_2_location": match.opponents[1].opponent.location,
                "slug": match.slug,
                "league_name": match.league.name,
                "stream_url": match.stream_url,
            })
            self.logging.info(f"Fetched match: {match.slug} at {datetime.fromisoformat(match.begin_at)} from tournament {match.tournament.slug}")

        return matches

    def _load_existing_calendar(self):
        """ Load the existing .ics calendar file if it exists, otherwise return a new calendar """
        if os.path.exists(self.ics_file_path):
            with open(self.ics_file_path, "r") as f:
                self.logging.info(f"Loaded existing calendar file: {self.ics_file_path}")
                return Calendar(f.read())
        self.logging.info("No existing calendar file found. Creating a new calendar.")
        return Calendar()

    def _generate_calendar_events(self, matches):
        """ Generate calendar events from the match data and update the .ics calendar """
        calendar = self._load_existing_calendar()

        for match in matches:
            match = Box(match)
            event = Event()
            event.uid = f"{match['id']}@esport_calendar"
            event.name = f"[{match.league_name}] {match.opponents_1_name} - {match.opponents_2_name} ({match.tournament_name} BO{match.number_of_games})"

            # Create a detailed description with more info
            event.description = (
                f"Video Game: [{match.videogame_name}] {match.videogame_slug}\n"
                f"League: {match.league_name}\n"
                f"Tournament: [Tier {match.tournament_tier}] {match.tournament_slug} ({match.tournament_name})\n"
                f"Match: {match.slug}\n"
                f"Team 1: [{match.opponents_1_location}] {match.opponents_1_name} ({match.opponents_1_acronym})\n"
                f"Team 2: [{match.opponents_2_location}] {match.opponents_2_name} ({match.opponents_2_acronym})\n"
            )

            event.begin = match['begin_at']  # ISO 8601 with timezone handling
            if match.number_of_games == 5:
                event.duration = timedelta(hours=3)
            elif match.number_of_games == 3:
                event.duration = timedelta(hours=2)
            else:
                event.duration = timedelta(hours=1)
                
            event.location = match.stream_url

            # Check if the event already exists, and update if it does
            existing_event = next((e for e in calendar.events if e.uid == event.uid), None)

            if existing_event:
                # Update the existing event if it already exists
                self.logging.info(f"Updating event: {event.name}")
                calendar.events.remove(existing_event)
                calendar.events.add(event)
            else:
                # Add a new event if it doesn't exist
                self.logging.info(f"Adding event: {event.name}")
                calendar.events.add(event)

        # Save the generated calendar to a temporary file first
        with open(self.temp_ics_file_path, "w") as f:
            f.write(calendar.serialize())
        self.logging.info(f"Temporary calendar file {self.temp_ics_file_path} generated.")

    def _replace_calendar_atomically(self):
        """ Replace the existing .ics file atomically with the updated one """
        try:
            # Atomically replace the old calendar with the new one
            shutil.move(self.temp_ics_file_path, self.ics_file_path)
            self.logging.info(f"Successfully updated the calendar file: {self.ics_file_path}.")
        except Exception as e:
            self.logging.error(f"Error updating the ICS file: {e}")
            # If something goes wrong, make sure to clean up the temporary file
            if os.path.exists(self.temp_ics_file_path):
                os.remove(self.temp_ics_file_path)

    def update_calendar(self):
        """ Main method to update the calendar """
        self.logging.info("Starting calendar update process...")
        matches = []
        for team_id in self.team_ids:
            self.logging.info(f"Fetching upcoming matches for team ID: {team_id}")
            matches.extend(self._fetch_upcoming_matches(team_id))
        self.logging.info(f"Total matches fetched: {len(matches)}")
        if matches:
            self._generate_calendar_events(matches)  # Generate events based on fetched data
            self._replace_calendar_atomically()  # Replace the old calendar with the new one
        self.logging.info("Calendar update process completed.")
