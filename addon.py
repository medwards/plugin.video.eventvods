from xbmcswift2 import Plugin
from collections import OrderedDict

import re
import urlparse
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
            if not match.get('YouTube', None):  # some don't seem to have anything
                continue
            element = {
                'label': '%s vs %s - %s' % (match['Team 1'], match['Team 2'], day),
                'path': plugin.url_for('youtube_play_match', video_id=match['YouTube']),
                'is_playable': True
            }
            match_ui_elements.append(element)
    return match_ui_elements

def parse_matches(reddit_text):
    # dummy value for now
    lines = reddit_text.split('\n')

    matches = OrderedDict()
    day = 'No Section'
    in_table = False
    for line in lines:
        if line.startswith('##'):  # "super-reliable" way of detecting day sections
            day = line.strip('#')
            day = day.replace('^th', '')
            day = day.replace('^st', '')
            day = day.replace('^rd', '')
        if line.startswith('|#|'):  # found a header
            header = line.split('|')
            if not header[0]:  # empty first element, nuke it
                header = header[1:]
            team_1_index = header.index('Team 1')
            team_2_index = header.index('Team 2')
            youtube_index = index_safely(header, 'YouTube')
            twitch_index = index_safely(header, 'Twitch')
            highlights_index = index_safely(header, 'Highlights')
            in_table = True
            continue
        if in_table:
            # TODO: too many mid-loop continues here
            if not line:  # empty line probably means the table is over
                in_table = False
                continue

            match_data = line.split('|')
            if line.startswith(':--:') or len(match_data) != len(header):  # dunno what this is, so skip it
                continue

            print match_data
            match = {'Team 1': team_name(match_data[team_1_index]),
                     'Team 2': team_name(match_data[team_2_index])}
            if youtube_index:
                match['YouTube'] = extract_youtube_id(extract_url(match_data[youtube_index]))
            if twitch_index:
                match['Twitch'] = extract_url(match_data[twitch_index])
            if highlights_index:
                match['Highlights'] = extract_youtube_id(extract_url(match_data[highlights_index]))

            matches.setdefault(day, []).append(match)
    return matches

def index_safely(the_list, elem):
    try:
        return the_list.index(elem)
    except ValueError:
        return None

def team_name(text):
    result = re.search('\*\*(.*)\*\*', text)
    if result and result.groups():
        return result.groups()[0]
    text = re.sub('\((.*)\)', '', text)  # clean up stuff in parens
    text = re.sub('\[(.*)\]', '', text)  # clean up stuff in brackets
    return text.strip()

def extract_url(text):
    # assumes markdown-ish style
    result = re.search('\((.*)\)', text)
    if result and result.groups():
        return result.groups()[0]
    return text  # pray

def extract_youtube_id(url):
    result = urlparse.urlparse(url)
    if result.path == '/watch':  # standard youtube.com url
        params = urlparse.parse_qs(result.query)
        return params['v'][0]
    elif result.netloc == 'youtu.be':  # used an URL shortener, thankfully ID matches
        return result.path.strip('/')


@plugin.route('/play/youtube/<video_id>')
def youtube_play_match(video_id):
    # maybe accept the url and then figure out the player then?
    url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % video_id
    plugin.set_resolved_url(url)

if __name__ == '__main__':
    plugin.run()
