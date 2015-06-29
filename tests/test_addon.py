import unittest
from nose.plugins.attrib import attr

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

@attr('slow')
class AddonSanityTest(unittest.TestCase):
    def test_games(self):
        import addon
        addon.show_games()

    def test_subreddit_tournaments(self):
        import addon
        addon.show_posts('Counter-Strike: Global Offensive')
        addon.show_posts('League of Legends')

    def test_api_games(self):
        import addon
        addon.show_riot_api_tournament(226)

    def test_subreddit_games(self):
        import addon
        addon.show_matches('Counter-Strike: Global Offensive', '3b49mi')
        addon.show_matches('League of Legends', '37v9mt')



