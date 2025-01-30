import logging
import os
import warnings

from dotenv import load_dotenv

from actions.base import ActionConnector
from actions.tweet.interface import TweetInput


class TweetAPIConnector(ActionConnector[TweetInput]):
    """Connector for Twitter API."""

    def __init__(self):
        super().__init__()
        load_dotenv()

        # Suppress tweepy warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=SyntaxWarning)
            import tweepy

            self.client = tweepy.Client(
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
            )

    async def connect(self, output_interface: TweetInput) -> None:
        """Send tweet via Twitter API."""
        try:
            # Log the tweet we're about to send
            tweet_to_make = {"sentence": output_interface.tweet}
            logging.info(f"SendThisToTwitterAPI: {tweet_to_make}")

            # Send tweet
            response = self.client.create_tweet(text=output_interface.tweet)
            tweet_id = response.data["id"]
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            logging.info(f"Tweet sent successfully! URL: {tweet_url}")

        except Exception as e:
            logging.error(f"Failed to send tweet: {str(e)}")
            raise
