from xbmcswift2 import Plugin

import praw  # might fail in actual kodi

plugin = Plugin()

# master listing of games /w subreddits
# might also need to track game for subreddit specific scraping
subreddits = {'League of Legends': 'LoLeventVoDs',
              'Counter-Strike: Global Offensive': 'cseventvods'
             }

@plugin.route('/')
def show_games():
    game_items = [{'label': name, 'path': plugin.url_for('show_posts', game=name)}
                  for name in subreddits]
    return game_items

@plugin.route('/show_posts/<game>')
def show_posts(game):
    client = praw.Reddit(user_agent="kodi_plugin.video.eventvods")
    subreddit_stickied_post = client.get_subreddit(subreddits[game]).get_sticky()
    post = {
        'label': subreddit_stickied_post.title,
        'path': plugin.url_for('show_matches', game=game, submission=subreddit_stickied_post.id)
    }

    return [post]

@plugin.route('/show_matches/<game>/<submission>')
def show_matches(game, submission):
    client = praw.Reddit(user_agent="kodi_plugin.video.eventvods")
    submission = client.get_submission(submission_id=submission)
    all_matches = parse_matches(submission.selftext)
    match_ui_elements = []
    for day, matches in all_matches.iteritems():
        for match in matches:
            element = {
                'label': '%s vs %s - %s' % (match['Team 1'], match['Team 2'], day),
                'path': plugin.url_for('youtube_play_match', video_id=match['Highlights']),
                'is_playable': True
            }
            match_ui_elements.append(element)
    return match_ui_elements

def parse_matches(reddit_text):
    # dummy value for now
    return {'Week 5, Day 1 - Thursday, June 25^th': [{'Team 1': 'FNC', 'Team 2': 'SK', 'Highlights': 'Dfo6U_IRcRk'}]}

@plugin.route('/play/youtube/<video_id>')
def youtube_play_match(video_id):
    # maybe accept the url and then figure out the player then?
    url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % video_id
    plugin.set_resolved_url(url)

if __name__ == '__main__':
    plugin.run()
