from xbmcswift2 import Plugin
from resources.lib.reddit import build_events_from_subreddit, build_matches_from_subreddit_submission
from resources.lib import api

plugin = Plugin()

# master listing of games /w subreddits
# need to exempt League because Riot has a proper API for them
games = {
         'League of Legends': {'subreddit': 'LoLeventVoDs'},
         #'League of Legends': {'api': 'lolesports'},  # lolesports API does bad caching on /match so its not useable right now
         'Counter-Strike: Global Offensive': {'subreddit': 'cseventvods'}
        }

@plugin.route('/')
def show_games():
    game_items = [{'label': name, 'path': plugin.url_for('show_posts', game=name)}
                  for name in games]
    return game_items

@plugin.route('/show_posts/<game>')
def show_posts(game):
    if 'api' in games[game]:
        events = api.build_events_from_api(plugin, game, games[game]['api'])
    elif 'subreddit' in games[game]:
        events = build_events_from_subreddit(plugin, game, games[game]['subreddit'])
    else:
        events = []

    return events

@plugin.route('/show_riot_api_tournament/<tournament>')
def show_riot_api_tournament(tournament):
    return api.build_games(plugin, tournament)

@plugin.route('/show_matches/<game>/<submission>')
def show_matches(game, submission):
    matches = build_matches_from_subreddit_submission(plugin, game, submission)
    return matches

@plugin.route('/play/youtube/<video_id>')
def youtube_play_match(video_id):
    # maybe accept the url and then figure out the player then?
    url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % video_id
    plugin.set_resolved_url(url)

@plugin.route('/play/twitch/<video_id>')
def twitch_play_match(video_id):
    # maybe accept the url and then figure out the player then?
    url = 'plugin://plugin.video.twitch/playVideo/%s' % video_id
    plugin.set_resolved_url(url)

if __name__ == '__main__':
    plugin.run()
