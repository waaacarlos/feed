from Feed import Feed
import asyncio


if __name__ == '__main__':
    _feed = Feed()
    asyncio.run(_feed.run())
