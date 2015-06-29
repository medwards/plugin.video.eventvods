import operator
import requests
import urlparse

API_HOST = 'http://na.lolesports.com/api/'
def build_tournaments(plugin, game, api_source):
    # assumes Riot API for now, extract later
    leagues = requests.get(urlparse.urljoin(API_HOST, 'league'), params={'parameters[method]': 'all'}, headers={'User-agent': 'Kodi plugin.video.eventvods'}).json()
    leagues = sorted(leagues['leagues'], key=operator.itemgetter('menuWeight'))
    events = [{'label': l['label'],
               'icon': l['leagueImage'],
               'thumbnail': l['leagueImage'],
               'path': plugin.url_for('show_api_matches', game='League of Legends', tournament=l['defaultTournamentId'])}
              for l in leagues if l['noVods'] == 0 and l['defaultTournamentId'] != 0]
    return events

def build_matches(plugin, tournament):
    match_data = {}
    contestants = get_contestants(tournament)
    for contestant in contestants:
        # TODO: THIS API CALL DOESN'T WORK FOR SOME REASON
        # Seems like it caches valid responses but doesn't distinguish the paramaters used, so you always
        # get your first successful cache hit
        contestant_matches = requests.get(urlparse.urljoin(API_HOST, 'match'), params={'parameters[tournament]': tournament, 'parameters[team]': contestant, 'parameters[method]': 'all'}, headers={'User-agent': 'Kodi plugin.video.eventvods'}).json()
        match_data.update(contestant_matches)  # horribly ugly, only guaranteed way to get all matches

    games = []
    game_url = urlparse.urljoin(API_HOST, 'game')
    for match in match_data.values():  # TODO: need to sort by time
        if not match.get('games'):
            continue
        for game in match['games'].values(): # TODO: also need to sort
            if game['hasVod'] == 0:
                continue
            game = requests.get(urlparse.urljoin(API_HOST, 'game/%s' % game['id']), headers={'User-agent': 'Kodi plugin.video.eventvods'}).json()
            if game['vods']['vod']['type'] != 'youtube':
                continue  # skip until we can handle other types
            games.append(make_game_item(plugin, match, game))
    return games

def make_game_item(plugin, match, game):
    vod = game['vods']['vod']['URL']
    item = {'label': "%s vs %s" % (match['contestants']['blue']['name'], match['contestants']['red']['name']),
            'path': plugin.url_for('youtube_play_match', video_id=extract_youtube_id(vod)),
            'is_playable': True
           }
    return item


def get_contestants(tournament):
    tournament = requests.get(urlparse.urljoin(API_HOST, 'tournament/%s' % tournament), headers={'User-agent': 'Kodi plugin.video.eventvods'}).json()
    return [c['id'] for c in tournament['contestants'].values()]

def extract_youtube_id(url):  # TODO: Duplicated from r/l/reddit.py
    result = urlparse.urlparse(url)
    if result.path == '/watch':  # standard youtube.com url
        params = urlparse.parse_qs(result.query)
        return params['v'][0]
    elif result.netloc == 'youtu.be':  # used an URL shortener, thankfully ID matches
        return result.path.strip('/')
