import unittest
import mock
import xbmcswift2
from nose.tools import assert_equals

class TournamentsUnitTest(unittest.TestCase):
    @mock.patch('praw.Reddit')
    def test_builds_tournaments(self, reddit_mock):
        sticky_mock = mock.Mock()
        sticky_mock.id = '123'
        sticky_mock.title = 'Recent Tournament'

        normal_mock = mock.Mock()
        normal_mock.id = '456'
        normal_mock.title = 'Old Tournament'

        client_mock = reddit_mock.return_value
        client_mock.get_subreddit.return_value.get_sticky.return_value = sticky_mock
        client_mock.get_subreddit.return_value.get_new.return_value = [normal_mock]


        from addon import plugin
        from resources.lib import reddit
        tournaments = reddit.build_tournaments(plugin, 'Hyped eSport', 'hypedvods')

        expected = [{'label': 'Recent Tournament',
                     'path': 'plugin://plugin.video.eventvods/tournament/Hyped+eSport/reddit/123/match'},
                    {'label': 'Old Tournament',
                     'path': 'plugin://plugin.video.eventvods/tournament/Hyped+eSport/reddit/456/match'}
                   ]
        assert_equals(expected, tournaments)

    def test_builds_tournaments_without_sticky(self):
        # TODO: what happens if there is no sticky on the subreddit?
        pass

class MatchesUnitTest(unittest.TestCase):
    @mock.patch('praw.Reddit')
    def test_builds_matches(self, reddit_mock):
        submission_mock = mock.Mock()
        submission_mock.selftext = """
---

##Week 4, Day 1 - Saturday, June 20^th

* **Full Stream:** [Twitch](http://www.twitch.tv/riotgames/v/6392126)

|#|Team 1|vs.|Team 2|Twitch|Twitch|YouTube|YouTube|Interview|Highlights|Discussion
:--:|--:|:--:|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--:
G1 [](http://www.table_title.com "W4D1, June 20th")| **DIG** [](#dig) | vs | [](#tip) **TIP** | [Picks & Bans](http://www.twitch.tv/riotgames/v/6392126?t=1h13m22s) | [Game Start](http://www.twitch.tv/riotgames/v/6392126?t=1h20m02s) | [Picks & Bans](https://www.youtube.com/watch?v=xTgvsYjxEvk&t=14m19s) | [Game Start](https://www.youtube.com/watch?v=xTgvsYjxEvk&t=20m56s) | [Interview](https://www.youtube.com/watch?v=xTgvsYjxEvk&t=1h03m03s) | [Highlights](https://www.youtube.com/watch?v=_74cY-fGdT0) | [Spoilers!](http://redd.it/3ajfxi)


##Week 4, Day 2 - Sunday, June 21^th
|#|Team 1|vs.|Team 2|Twitch|Twitch|YouTube|YouTube|Interview|Highlights|Discussion
:--:|--:|:--:|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--:
G2 | **TDK** [](#tdk) | vs | [](#clg) **CLG** | [Picks & Bans](http://www.twitch.tv/riotgames/v/6392126?t=2h18m10s) | [Game Start](http://www.twitch.tv/riotgames/v/6392126?t=2h23m21s) | [Picks & Bans](https://www.youtube.com/watch?v=jKtUERIXfBA&t=3m17s) | [Game Start](https://www.youtube.com/watch?v=jKtUERIXfBA&t=8m28s) | [Interview](https://www.youtube.com/watch?v=jKtUERIXfBA&t=48m59s) | [Highlights](https://www.youtube.com/watch?v=QxzsKb_aZWo) | [Spoilers!](http://redd.it/3ajmk2)

* **Patch:** [**5.11**](http://euw.leagueoflegends.com/en/news/game-updates/patch/patch-511-notes)
* **Live Discussion Thread:** [Spoilers!](http://redd.it/3aivui)
* **Recommended Games:** [Strawpoll](http://strawpoll.me/4691377)
*Covered by /u/Punistick*
        """

        client_mock = reddit_mock.return_value
        client_mock.get_submission.return_value = submission_mock

        from addon import plugin
        from resources.lib import reddit
        matches = reddit.build_matches(plugin, 'Hyped eSport', 'whatever')

        expected = [{'label': 'DIG vs TIP - Week 4, Day 1 - Saturday, June 20',
                     'path': 'plugin://plugin.video.eventvods/play/youtube/xTgvsYjxEvk',
                     'is_playable': True},
                    {'label': 'TDK vs CLG - Week 4, Day 2 - Sunday, June 21',
                     'path': 'plugin://plugin.video.eventvods/play/youtube/jKtUERIXfBA',
                     'is_playable': True}]
        assert_equals(expected, matches)

    @mock.patch('praw.Reddit')
    def test_builds_gfinity_masters_matches(self, reddit_mock):
        # TODO: Rename once defect source identified
        submission_mock = mock.Mock()
        submission_mock.selftext = """
* **Gfinity Summer Masters I**
* **Date:** June 26th - 28th
* **Stream:** [Twitch](http://www.twitch.tv/gfinitytv)
* **Teams:** Cloud 9, EnVyUs, Virtus.Pro, Ninjas in Pyjamas, Team Dignitas, Titan, SK Gaming, mousesports
* **Format:** All games except finals are BO3; double elimination

---

##Day 1, Friday - June 26^th

|#|Map|Team 1|vs|Team 2|Twitch|YouTube|HLTV
:--:|:--:|--:|:--:|:--|:--:|:--:|:--:|
A1 | Mirage | **Titan** [](#titan) | vs | [](#dig) **Dignitas** | [RUS](http://www.twitch.tv/starladder10/v/6618163?t=26m1s) | [RUS](https://www.youtube.com/watch?v=zPhbYJ5nQ68) | [HLTV](http://www.hltv.org/match/2296735-titan-dignitas-gfinity-2015-summer-masters-1)
A2 | Overpass | **Titan** [](#titan) | vs | [](#dig) **Dignitas** | [RUS](http://www.twitch.tv/starladder10/v/6618163?t=1h13m13s) | [RUS](https://www.youtube.com/watch?v=Q1ZiUgug_7E) | [HLTV](http://www.hltv.org/match/2296735-titan-dignitas-gfinity-2015-summer-masters-1)
A3 | Cache | **Titan** [](#titan) | vs | [](#dig) **Dignitas** | [RUS](http://cs.eventvods.com) | [RUS](http://cs.eventvods.com) | [HLTV](http://www.hltv.org/match/2296735-titan-dignitas-gfinity-2015-summer-masters-1)
 | 


##Day 2, Saturday - June 27^th

|#|Map|Team 1|vs|Team 2|Twitch|YouTube|HLTV
:--:|:--:|--:|:--:|:--|:--:|:--:|:--:
E1|Cache|[Winner of A](/s "Dignitas")|vs|[Winner of B](/s "NiP")|[**ENG**](http://www.twitch.tv/gfinitytv/v/6648155?t=51m42s)|[**ENG**](https://www.youtube.com/watch?v=IftovJWBBQs)|[HLTV](http://www.hltv.org/match/2296742-dignitas-nip-gfinity-2015-summer-masters-1)
E2|Mirage|[Winner of A](/s "Dignitas")|vs|[Winner of B](/s "NiP")|[**ENG**](http://www.twitch.tv/gfinitytv/v/6648155?t=1h27m28s)|[**ENG**](https://www.youtube.com/watch?v=Y_B2bTzbiBc)|[HLTV](http://www.hltv.org/match/2296742-dignitas-nip-gfinity-2015-summer-masters-1)
 |

*Covered by: /u/iPlain*

####Day 3, Sunday - June 28^th

##Semi Finals and Finals

|#|Map|Team 1|vs|Team 2|Twitch|YouTube|HLTV
:--:|:--:|--:|:--:|:--|:--:|:--:|:--:
K1|Train|[Winner of E](/s "NiP")|vs|[Winner of J](/s "Mouz")|[**ENG**](http://www.twitch.tv/gfinitytv/v/6686745?t=53m59s)|[**ENG**](https://www.youtube.com/watch?v=nba_w1oG33k)|[HLTV](http://www.hltv.org/match/2296748-nip-mousesports-gfinity-2015-summer-masters-1)
K2|Dust 2|[Winner of E](/s "NiP")|vs|[Winner of J](/s "Mouz")|[**ENG**](http://www.twitch.tv/gfinitytv/v/6686745?t=1h48m43s)|[**ENG**](https://www.youtube.com/watch?v=lFTLVL2QdwY)|[HLTV](http://www.hltv.org/match/2296748-nip-mousesports-gfinity-2015-summer-masters-1)
K3|Mirage|[Winner of E](/s "NiP")|vs|[Winner of J](/s "Mouz")|[**ENG**](http://cs.eventvods.com)|[**ENG**](http://cs.eventvods.com)|[HLTV](http://www.hltv.org/match/2296748-nip-mousesports-gfinity-2015-summer-masters-1)
*Covered by: /u/iPlain*

        """

        client_mock = reddit_mock.return_value
        client_mock.get_submission.return_value = submission_mock

        from addon import plugin
        from resources.lib import reddit
        matches = reddit.build_matches(plugin, 'Hyped eSport', 'whatever')

        expected = [{'label': 'Titan vs Dignitas - Day 1, Friday - June 26',
                     'path': 'plugin://plugin.video.eventvods/play/youtube/zPhbYJ5nQ68',
                     'is_playable': True},
                    {'label': 'Titan vs Dignitas - Day 1, Friday - June 26',
                     'path': 'plugin://plugin.video.eventvods/play/youtube/Q1ZiUgug_7E',
                     'is_playable': True},
                    {'label': 'Dignitas vs NiP - Day 2, Saturday - June 27',
                     'path': u'plugin://plugin.video.eventvods/play/youtube/IftovJWBBQs',
                     'is_playable': True},
                    {'label': 'Dignitas vs NiP - Day 2, Saturday - June 27',
                     'path': u'plugin://plugin.video.eventvods/play/youtube/Y_B2bTzbiBc',
                     'is_playable': True},
                    {'label': 'NiP vs Mouz - Semi Finals and Finals',
                     'path': u'plugin://plugin.video.eventvods/play/youtube/nba_w1oG33k',
                     'is_playable': True},
                    {'label': 'NiP vs Mouz - Semi Finals and Finals',
                     'path': u'plugin://plugin.video.eventvods/play/youtube/lFTLVL2QdwY',
                     'is_playable': True},
                   ]
        from pprint import pprint
        assert_equals(expected, matches)

