import requests
from django.conf import settings
from django.shortcuts import render, redirect
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)

def home(request):
    """Render the homepage"""
    return render(request, 'home.html')

def live_matches(request):
    """Function to fetch live cricket matches"""
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Live matches API response status: {response.status_code}")
        data = response.json()
    except Exception as e:
        logger.exception("Error fetching live matches")
        data = {"error": "Unable to fetch live matches"}

    return render(request, "matches/live_matches.html", {'live_data': data})

def recent_matches(request):
    """Function to fetch recent cricket matches"""
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Recent matches API response status: {response.status_code}")
        data = response.json()
    except Exception as e:
        logger.exception("Error fetching recent matches")
        data = {"error": "Unable to fetch recent matches"}

    return render(request, "matches/recent_matches.html", {'recent_data': data})

def upcoming_matches(request):
    """Function to fetch upcoming cricket matches"""
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Upcoming matches API response status: {response.status_code}")
        data = response.json()

        # Convert startDate strings to datetime objects
        if 'typeMatches' in data:
            for type_match in data['typeMatches']:
                for series in type_match.get('seriesMatches', []):
                    if 'seriesAdWrapper' in series:
                        for match in series['seriesAdWrapper'].get('matches', []):
                            if 'matchInfo' in match and 'startDate' in match['matchInfo']:
                                # Convert timestamp to datetime
                                timestamp = int(match['matchInfo']['startDate'])
                                match['matchInfo']['startDate'] = datetime.fromtimestamp(timestamp/1000)

    except Exception as e:
        logger.exception("Error fetching upcoming matches")
        data = {"error": "Unable to fetch upcoming matches"}

    return render(request, "matches/upcoming_matches.html", {'upcoming_data': data})

def commentary(request, match_id):
    """Function to fetch ball by ball commentary for a match"""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/comm"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Commentary API response status: {response.status_code}")
        data = response.json()
        context = {
            'data': data,
            'match_id': match_id,
            'active_tab': 'commentary'
        }
        return render(request, 'matches/commentary.html', context)

    except Exception as e:
        logger.exception("Error fetching commentary")
        messages.error(request, 'Unable to fetch match commentary')
        return redirect('live_matches')

def scorecard(request, match_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/hscard"

    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
    }

    response = requests.get(url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        logger.info(f"Scorecard API response status: {response.status_code}")
        scorecard_content = response.json()
    else:
        logger.error(f"Scorecard API error: {response.status_code}")
        scorecard_content = {"error": "Unable to fetch scorecard"}

    # Render the scorecard.html template with the fetched data
    return render(request, "matches/scorecard.html", {"scorecard": scorecard_content, "match_id": match_id})

def match_info(request, match_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}"

    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
    }

    response = requests.get(url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        logger.info(f"Match info API response status: {response.status_code}")
        match_data = response.json()
    else:
        logger.error(f"Match info API error: {response.status_code}")
        match_data = {"error": "Unable to fetch match info"}

    # Render the match_details.html template with the fetched data
    return render(request, "matches/match_details.html", {"match_data": match_data, "match_id": match_id})

def match_details(request, match_id):
    try:
        # API headers
        headers = {
            'X-RapidAPI-Key': settings.RAPIDAPI_KEY,
            'X-RapidAPI-Host': settings.RAPIDAPI_HOST
        }

        # Fetch match data from your API
        match_url = f"{settings.API_BASE_URL}/matches/{match_id}/info"
        response = requests.get(match_url, headers=headers)
        match_data = response.json()

        context = {
            'match_data': match_data,
            'match_id': match_id
        }
        return render(request, 'matches/match_details.html', context)
    except Exception as e:
        context = {
            'error': f"Error fetching match details: {str(e)}",
            'match_id': match_id
        }
        return render(request, 'matches/match_details.html', context)

def schedule(request):
    schedule_url = "https://cricbuzz-cricket.p.rapidapi.com/schedule/v1/international"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
    }

    try:
        schedule_response = requests.get(schedule_url, headers=headers)
        logger.info(f"Schedule API response status: {schedule_response.status_code}")
        schedule_data = schedule_response.json() if schedule_response.status_code == 200 else {"error": "Unable to fetch schedule"}

        # Convert timestamps to datetime objects
        if 'matchScheduleMap' in schedule_data:
            for schedule in schedule_data['matchScheduleMap']:
                if 'scheduleAdWrapper' in schedule:
                    for match in schedule['scheduleAdWrapper'].get('matchScheduleList', []):
                        if 'matchInfo' in match and match['matchInfo']:
                            start_date = match['matchInfo'][0].get('startDate')
                            if start_date:
                                # Convert timestamp to datetime
                                match['matchInfo'][0]['startDate'] = datetime.fromtimestamp(int(start_date)/1000)

    except Exception as e:
        logger.exception("Error fetching schedule")
        schedule_data = {"error": "Unable to fetch schedule"}

    return render(request, "schedule/schedule.html", {"schedule_data": schedule_data})

def news(request):
    """Fetch cricket news from CricBuzz API."""
    url = "https://cricbuzz-cricket.p.rapidapi.com/news/v1/index"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
    }
    response = requests.get(url, headers=headers)
    logger.info(f"News API response status: {response.status_code}")
    news_data = response.json() if response.status_code == 200 else {"error": "Unable to fetch cricket news"}
    return render(request, "news/news.html", {"news_items": news_data})

def news_detail(request, story_id):
    """Fetch detailed news article from CricBuzz API."""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/news/v1/detail/{story_id}"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
    }
    response = requests.get(url, headers=headers)
    logger.info(f"News detail API response status: {response.status_code}")
    news_detail = response.json() if response.status_code == 200 else {"error": "Unable to fetch news details"}
    return render(request, "news/news_detail.html", {"news": news_detail})

def players(request):
    """Fetch trending players."""
    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/trending"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
    }
    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Trending players API response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            return render(request, "players/player.html", data)
        else:
            return render(request, "players/player.html", {
                "error": "Unable to fetch trending players",
                "player": [],
                "category": "Trending Players"
            })
    except Exception as e:
        logger.exception("Error fetching trending players")
        return render(request, "players/player.html", {
            "error": "Unable to fetch trending players",
            "player": [],
            "category": "Trending Players"
        })

def player_info(request, player_id):
    """Fetch and display player information along with batting, bowling statistics, and photos from the CricBuzz API."""
    base_url = "https://cricbuzz-cricket.p.rapidapi.com"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        info_url = f"{base_url}/stats/v1/player/{player_id}"
        info_response = requests.get(info_url, headers=headers)
        logger.info(f"Player info API response status: {info_response.status_code}")
        player_data = info_response.json()

        if isinstance(player_data.get('teams'), list):
            player_data['teams'] = ', '.join(player_data['teams'])

        if 'image' in player_data:
            player_data['image'] = player_data['image'].replace('http://', 'https://')

        batting_url = f"{base_url}/stats/v1/player/{player_id}/batting"
        batting_response = requests.get(batting_url, headers=headers)
        logger.info(f"Batting stats API response status: {batting_response.status_code}")
        if batting_response.status_code == 200:
            player_data['batting_stats'] = batting_response.json()

        bowling_url = f"{base_url}/stats/v1/player/{player_id}/bowling"
        bowling_response = requests.get(bowling_url, headers=headers)
        logger.info(f"Bowling stats API response status: {bowling_response.status_code}")
        if bowling_response.status_code == 200:
            player_data['bowling_stats'] = bowling_response.json()

        galleries_url = f"{base_url}/photos/v1/index"
        galleries_response = requests.get(galleries_url, headers=headers)
        logger.info(f"Galleries API response status: {galleries_response.status_code}")
        if galleries_response.status_code == 200:
            galleries_data = galleries_response.json()
            player_photos = []

            player_name = player_data.get('name', '').lower()
            for gallery in galleries_data.get('galleries', []):
                if (player_name in gallery.get('title', '').lower() or
                    player_name in gallery.get('caption', '').lower()):
                    detail_url = f"{base_url}/photos/v1/detail/{gallery['id']}"
                    detail_response = requests.get(detail_url, headers=headers)
                    logger.info(f"Gallery detail API response status: {detail_response.status_code}")
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        gallery['images'] = []
                        for image in detail_data.get('images', []):
                            if 'id' in image:
                                image_id = image['id']
                                if not image_id.startswith('c'):
                                    image_id = f"c{image_id}"
                                image['urls'] = {
                                    'large': f"https://cricbuzz-cricket.p.rapidapi.com/img/v1/i1/{image_id}/i.jpg?p=de&d=high",
                                    'thumb': f"https://cricbuzz-cricket.p.rapidapi.com/img/v1/i1/{image_id}/i.jpg?p=thumb&d=high",
                                    'gallery_thumb': f"https://cricbuzz-cricket.p.rapidapi.com/img/v1/i1/{image_id}/i.jpg?p=gthumb&d=high"
                                }
                                gallery['images'].append(image)
                        if gallery['images']:
                            player_photos.append(gallery)

            player_data['photo_galleries'] = player_photos[:5]

        return render(request, "players/player_info.html", {
            "player": player_data,
            "error": None
        })

    except Exception as e:
        logger.exception("Error fetching player information")
        return render(request, "players/player_info.html", {
            "error": "Unable to fetch player information"
        })

def search_player(request):
    player_name = request.GET.get('plrN', '')

    if not player_name:
        return render(request, "players/player_search.html", {
            "error": "Please enter a player name to search",
            "player": []
        })

    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"

    querystring = {"plrN": player_name}

    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        logger.info(f"Player search API response status: {response.status_code}")
        if response.status_code == 200:
            search_results = response.json()
            if 'player' in search_results:
                for player in search_results['player']:
                    if not player.get('id'):
                        player['id'] = ''
            return render(request, "players/player_search.html", search_results)
        else:
            return render(request, "players/player_search.html", {
                "error": "Unable to fetch player data",
                "player": []
            })
    except Exception as e:
        logger.exception("Error searching for players")
        return render(request, "players/player_search.html", {
            "error": "An error occurred while searching for players",
            "player": []
        })

def default_ranking(request):
    """Redirect to test batsmen rankings by default"""
    return redirect('player_ranking', format='test', category='batsmen')

def player_ranking(request, format='test', category='batsmen'):
    """
    Fetch player rankings based on format and category.
    Args:
        format (str): One of 'test', 'odi', 't20'
        category (str): One of 'batsmen', 'bowlers', 'allrounders', 'teams'
    """
    try:
        base_url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/rankings"

        valid_categories = ['batsmen', 'bowlers', 'allrounders', 'teams']
        if category not in valid_categories:
            messages.error(request, f"Invalid category: {category}")
            return redirect('default_ranking')

        url = f"{base_url}/{category}"

        valid_formats = ['test', 'odi', 't20']
        if format not in valid_formats:
            messages.error(request, f"Invalid format: {format}")
            return redirect('default_ranking')

        params = {
            "formatType": format
        }

        is_women = request.GET.get('isWomen')
        if is_women:
            params['isWomen'] = '1'
            if format == 'odi':
                messages.warning(request, "ODI format not available for women's cricket")
                return redirect('player_ranking', format='test', category=category)

        headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": settings.RAPIDAPI_HOST
        }

        response = requests.get(url, headers=headers, params=params)
        logger.info(f"Rankings API response status: {response.status_code}")
        response.raise_for_status()
        rankings_data = response.json()

        context = {
            'rankings': rankings_data,
            'format': format,
            'category': category,
            'is_women': bool(is_women),
            'format_options': ['test', 't20'] if is_women else ['test', 'odi', 't20'],
            'category_options': valid_categories
        }

        return render(request, 'rankings/player_ranking.html', context)

    except requests.RequestException as e:
        error_message = str(e)
        logger.error(f"Error fetching rankings: {error_message}")
        messages.error(request, f"Failed to fetch rankings data: {error_message}")
        return redirect('home')
    except Exception as e:
        logger.exception("Error fetching rankings")
        messages.error(request, "An unexpected error occurred")
        return redirect('home')

def teams(request, team_type='international'):
    """
    Fetch teams based on type (international, league, domestic, women).
    Args:
        team_type (str): Type of teams to fetch (international, league, domestic, women)
    """
    valid_types = ['international', 'league', 'domestic', 'women']
    if team_type not in valid_types:
        messages.error(request, f"Invalid team type. Must be one of: {', '.join(valid_types)}")
        return redirect('teams', team_type='international')

    url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_type}"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Teams API response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
        else:
            messages.error(request, f"Error fetching {team_type} teams. Status code: {response.status_code}")
            data = {"error": f"Unable to fetch {team_type} teams"}

    except Exception as e:
        logger.exception("Error fetching teams")
        messages.error(request, f"Error fetching {team_type} teams")
        data = {"error": f"Unable to fetch {team_type} teams"}

    context = {
        'teams_data': data,
        'team_type': team_type,
        'valid_types': valid_types
    }
    return render(request, "teams/teams.html", context)

def team_details(request, team_id):
    """Fetch comprehensive team details including schedule, players, stats, and results"""
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    schedule_url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/schedule"
    try:
        schedule_response = requests.get(schedule_url, headers=headers)
        logger.info(f"Team schedule API response status: {schedule_response.status_code}")
        schedule_data = schedule_response.json() if schedule_response.status_code == 200 else None
    except Exception as e:
        logger.exception("Error fetching team schedule")
        schedule_data = None

    players_url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/players"
    try:
        players_response = requests.get(players_url, headers=headers)
        logger.info(f"Team players API response status: {players_response.status_code}")
        players_data = players_response.json() if players_response.status_code == 200 else None
    except Exception as e:
        logger.exception("Error fetching team players")
        players_data = None

    stats_url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/team/{team_id}"
    try:
        stats_response = requests.get(stats_url, headers=headers)
        logger.info(f"Team stats API response status: {stats_response.status_code}")
        stats_data = stats_response.json() if stats_response.status_code == 200 else None
    except Exception as e:
        logger.exception("Error fetching team stats")
        stats_data = None

    results_url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/results"
    try:
        results_response = requests.get(results_url, headers=headers)
        logger.info(f"Team results API response status: {results_response.status_code}")
        results_data = results_response.json() if results_response.status_code == 200 else None
    except Exception as e:
        logger.exception("Error fetching team results")
        results_data = None

    context = {
        'team_id': team_id,
        'schedule_data': schedule_data,
        'players_data': players_data,
        'stats_data': stats_data,
        'results_data': results_data,
        'active_tab': request.GET.get('tab', 'schedule')
    }

    return render(request, "teams/team_details.html", context)

def render_series_list(request, series_type='international'):
    """Render the series list template"""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{series_type}"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Series list API response status: {response.status_code}")
        data = response.json()

        if 'seriesMapProto' in data:
            for series_type in data['seriesMapProto']:
                for series in series_type.get('series', []):
                    if 'startDt' in series:
                        series['startDt'] = datetime.fromtimestamp(int(series['startDt'])/1000)
                    if 'endDt' in series:
                        series['endDt'] = datetime.fromtimestamp(int(series['endDt'])/1000)

    except Exception as e:
        logger.exception("Error fetching series list")
        data = {"error": "Unable to fetch series list"}

    return render(request, 'series/series_list.html', {'series_data': data, 'series_type': series_type})

def render_series_detail(request, series_id):
    """Render the series matches template"""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{series_id}"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Series detail API response status: {response.status_code}")
        if response.status_code != 200:
            data = {"error": f"API returned status code {response.status_code}"}
            logger.error(f"API error for series detail: {response.status_code}")
        else:
            data = response.json()
            logger.info("Successfully fetched series detail data")
            data['seriesId'] = series_id

            if 'matchDetails' in data:
                for detail in data['matchDetails']:
                    if 'matchDetailsMap' in detail:
                        matches = detail['matchDetailsMap'].get('match', [])
                        for match in matches:
                            if 'matchInfo' in match:
                                info = match['matchInfo']
                                if 'startDate' in info:
                                    info['startDate'] = datetime.fromtimestamp(int(info['startDate'])/1000)
                                if 'endDate' in info:
                                    info['endDate'] = datetime.fromtimestamp(int(info['endDate'])/1000)
                                if 'seriesStartDt' in info:
                                    info['seriesStartDt'] = datetime.fromtimestamp(int(info['seriesStartDt'])/1000)
                                if 'seriesEndDt' in info:
                                    info['seriesEndDt'] = datetime.fromtimestamp(int(info['seriesEndDt'])/1000)
    except Exception as e:
        logger.exception("Error fetching series detail")
        data = {"error": "Unable to fetch series matches"}

    return render(request, 'series/series_matches.html', {'matches_data': data})

def render_series_squads(request, series_id):
    """Render the series squads template"""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{series_id}/squads"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Squads API response status: {response.status_code}")

        if response.status_code == 429:
            data = {"error": "We've hit our API rate limit. Please try again in a few minutes."}
            logger.warning("API rate limit exceeded for squads")
        elif response.status_code != 200:
            data = {"error": f"API returned status code {response.status_code}"}
            logger.error(f"API error for squads: {response.status_code}")
        else:
            data = response.json()
            logger.info("Successfully fetched squads data")

            if 'squads' in data:
                data['squads'] = [squad for squad in data['squads'] if not squad.get('isHeader', False)]
            else:
                data = {"error": "No squad information available for this series"}
                logger.warning("No squads data in API response")

            data['seriesId'] = series_id

    except Exception as e:
        logger.exception("Error fetching series squads")
        data = {"error": "Unable to fetch series squads"}

    return render(request, 'series/series_squads.html', {'squads_data': data})

def render_squad_players(request, series_id, squad_id):
    """Render the squad players template"""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{series_id}/squads/{squad_id}"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Squad players API response status: {response.status_code}")

        if response.status_code == 429:
            data = {"error": "We've hit our API rate limit. Please try again in a few minutes."}
            logger.warning("API rate limit exceeded for squad players")
        elif response.status_code != 200:
            data = {"error": f"API returned status code {response.status_code}"}
            logger.error(f"API error for squad players: {response.status_code}")
        else:
            data = response.json()
            logger.info("Successfully fetched squad players data")

            if 'player' in data:
                players_by_role = {}
                current_role = None

                for item in data['player']:
                    if item.get('isHeader'):
                        current_role = item['name']
                    else:
                        if current_role not in players_by_role:
                            players_by_role[current_role] = []
                        players_by_role[current_role].append(item)

                data['players_by_role'] = players_by_role
            else:
                data = {"error": "No player information available for this squad"}
                logger.warning("No players data in API response")

            data['seriesId'] = series_id
            data['squadId'] = squad_id

    except Exception as e:
        logger.exception("Error fetching squad players")
        data = {"error": "Unable to fetch squad players"}

    return render(request, 'series/squad_players.html', {'squad_data': data})

def get_cricbuzz_headers():
    """Get headers for CricBuzz API"""
    return {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST
    }

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile(request):
    return render(request, 'registration/profile.html', {'user': request.user})
