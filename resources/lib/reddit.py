import praw
import re
import urlparse
from collections import OrderedDict

def build_tournaments(plugin, game, subreddit):
    client = praw.Reddit(user_agent="kodi_plugin.video.eventvods")
    subreddit_stickied_post = client.get_subreddit(subreddit).get_sticky()
    sticky = {
        'label': subreddit_stickied_post.title,
        'path': plugin.url_for('show_reddit_matches', game=game, submission=subreddit_stickied_post.id)
    }

    other_posts = client.get_subreddit(subreddit).get_new()

    events = [sticky]
    for post in other_posts:
        event = {
            'label': post.title,
            'path': plugin.url_for('show_reddit_matches', game=game, submission=post.id)
        }
        if event not in events:
            events.append(event)
    return events

def build_matches(plugin, game, submission):
    client = praw.Reddit(user_agent="kodi_plugin.video.eventvods")
    submission = client.get_submission(submission_id=submission)
    all_matches = parse_matches(submission.selftext)
    match_ui_elements = []
    for day, matches in all_matches.iteritems():
        for match in matches:
            if not match.get('YouTube', None):  # some don't seem to have anything
                continue
            series = ''
            if match.get('series_number'):
                series = 'Game %s - ' % match['series_number']
            element = {
                'label': '%s%s vs %s - %s' % (series, match['Team 1'], match['Team 2'], day),
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
            day = day.replace('^nd', '')
            in_table = False
        if re.search('\|([\s#]*)\|', line):  # found header
            line = line.lower()
            header = map(lambda h: h.strip(), line.split('|'))
            if line.startswith('|'):
                header = header[1:]  # leading pipe will cause an extra blank element
            try:
                team_1_index = header.index('team 1')
                team_2_index = header.index('team 2')
            except ValueError: # indexes don't exist
                pass
            youtube_index = index_safely(header, 'youtube')
            twitch_index = index_safely(header, 'twitch')
            highlights_index = index_safely(header, 'highlights')
            in_table = True
            continue
        if in_table:
            # TODO: too many mid-loop continues here
            if not line:  # empty line probably means the table is over
                in_table = False
                continue

            match_data = line.split('|')
            if line.startswith('|'):
                match_data = match_data[1:]  # leading pipe will cause an extra blank element
            if ':--:' in line or len(match_data) != len(header):  # dunno what this is, so skip it
                continue

            team1 = team_name(match_data[team_1_index])
            team2 = team_name(match_data[team_2_index])
            match = {'Team 1': team1,
                     'Team 2': team2}
            if matches.get(day, []):  # check for a series
                previous_match = matches[day][-1]
                previous_teams = (previous_match['Team 1'], previous_match['Team 2'])
                if team1 in previous_teams and team2 in previous_teams:
                    if not previous_match.get('series_number'):
                        previous_match['series_number'] = 1
                    match['series_number'] = previous_match['series_number'] + 1

            if youtube_index:
                match['YouTube'] = extract_youtube_id(extract_url(match_data[youtube_index]))
            if twitch_index:
                match['Twitch'] = extract_twitch_id(extract_url(match_data[twitch_index]))
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
    result = re.search('\*\*(.*)\*\*', text)  # look for bolded names
    if result and result.groups():
        return result.groups()[0]
    result = re.search('\(/s\s?"(.*)"\)', text)  # look for spoiler covered names
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

def extract_twitch_id(url):
    result = urlparse.urlparse(url)
    path = result.path.split('/')
    if len(path) > 2 and path[-2] in ['v', 'a', 'c']:
        twitch_id = '%s%s' % (path[-2], path[-1])
        return twitch_id

