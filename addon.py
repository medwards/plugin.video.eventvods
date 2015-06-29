from xbmcswift2 import Plugin
from resources.lib import reddit
from resources.lib import api

plugin = Plugin()

# master listing of games /w subreddits
# need to exempt League because Riot has a proper API for them
games = {
        'League of Legends': {'subreddit': 'LoLeventVoDs',
                              'api': 'lolesports',
                              'twitch_streams': {'EN': ['riotgames', 'riotgames2']}  # Snipe from API?
                             },
         'Counter-Strike: Global Offensive': {'subreddit': 'cseventvods'},
         #'HearthStone': {'subreddit': 'hearthstonevods'},
         #'StarCraft': {'subreddit': 'SpoilerFreeSC'}
        }

@plugin.route('/')
def show_games():
    game_items = [{'label': name, 'path': plugin.url_for('show_reddit_tournaments', game=name)}
                  for name in games]
    return game_items

@plugin.route('/tournament/<game>/reddit')
def show_reddit_tournaments(game):
    streams = [{'label': 'STREAM %s' % stream,
                'path': plugin.url_for('twitch_play_stream', stream=stream),
                'is_playable': True
               }
               for stream in games[game].get('twitch_streams', {'EN': []})['EN']]
    events = reddit.build_tournaments(plugin, game, games[game]['subreddit'])
    streams.extend(events)
    return streams

@plugin.route('/tournament/<game>/api')
def show_api_tournaments(game):
    # note - not used, lolesports api doesn't return correct games
    events = api.build_tournaments(plugin, game, games[game]['api'])
    return events

@plugin.route('/tournament/<game>/api/<tournament>/match')
def show_api_matches(game, tournament):
    return api.build_matches(plugin, tournament)

@plugin.route('/tournament/<game>/reddit/<submission>/match')
def show_reddit_matches(game, submission):
    matches = reddit.build_matches(plugin, game, submission)
    return matches

@plugin.route('/play/youtube/<video_id>')
def youtube_play_match(video_id):
    # maybe accept the url and then figure out the player then?
    url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % video_id
    plugin.set_resolved_url(url)

@plugin.route('/play/twitch/video/<video_id>')
def twitch_play_match(video_id):
    # maybe accept the url and then figure out the player then?
    url = 'plugin://plugin.video.twitch/playVideo/%s' % video_id
    plugin.set_resolved_url(url)

@plugin.route('/play/twitch/stream/<stream>')
def twitch_play_stream(stream):
    # maybe accept the url and then figure out the player then?
    url = 'plugin://plugin.video.twitch/playLive/%s' % stream
    plugin.set_resolved_url(url)

if __name__ == '__main__':
    plugin.run()
