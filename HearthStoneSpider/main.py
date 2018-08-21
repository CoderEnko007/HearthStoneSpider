from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(['scrapy', 'crawl', 'HearthStone'])
# execute(['scrapy', 'crawl', 'HSReport'])
# execute(['scrapy', 'crawl', 'HSDecks'])
# execute(['scrapy', 'crawl', 'HSWinRate'])
execute(['scrapy', 'crawl', 'HSArchetype'])
