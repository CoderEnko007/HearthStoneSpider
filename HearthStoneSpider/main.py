from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(['scrapy', 'crawl', 'HearthStone'])
# execute(['scrapy', 'crawl', 'HSReport'])
# execute(['scrapy', 'crawl', 'HSDecks', '-a', "params=trending"])
execute(['scrapy', 'crawl', 'HSDecks', '-a', "params=decks"])
# execute(['scrapy', 'crawl', 'HSWildDecks'])
# execute(['scrapy', 'crawl', 'HSWinRate'])
# execute(['scrapy', 'crawl', 'HSArchetype'])
# execute(['scrapy', 'crawlall'])
# execute(['scrapy', 'crawl', 'HSArenaCards'])
# execute(['scrapy', 'crawl', 'HSArenaCards', '-a', "params=extra_data"])
# execute(['scrapy', 'crawl', 'HSRanking'])
