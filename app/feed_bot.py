import os

import feedparser
from dateutil import parser
from markdownify import markdownify
from utils import utils


def main():
    feed_bot_path = os.environ.get("FEED_BOT_PATH", "posts/feed_bot")
    config_name = "feeds"
    utils_obj = utils(feed_bot_path, config_name)

    for feed in utils_obj.list:
        if feed.get("url") is None:
            raise ValueError(f"No url found in the file for feed {feed}")
        try:
            feed_data = feedparser.parse(feed.get("url"))
        except Exception as e:
            print(f"Error in parsing feed {feed.get('url')}: {e}")
            continue

        folder = feed_data.feed.title.replace(" ", "_").lower()
        format_string = feed.get("format")
        feeds_processed = []
        for entry in feed_data.entries:
            date_entry = (
                entry.get("published") or entry.get("pubDate") or entry.get("updated")
            )
            published_date = parser.isoparse(date_entry).date()

            if entry.link is None:
                print(f"No link found: {entry.title}")
                continue

            file_name = entry.link.split("/")[-1] or entry.link.split("/")[-2]

            entry["content"] = (
                markdownify(entry.content[0].value).strip()
                if "content" in entry
                else ""
            )

            formatted_text = format_string.format(**entry)

            entry_data = {
                "title": entry.title,
                "config": feed,
                "date": published_date,
                "rel_file_path": f"{folder}/{file_name}.md",
                "formatted_text": formatted_text,
            }
            if utils_obj.process_entry(entry_data):
                feeds_processed.append(f"[{entry.title}]({entry.link})")

    title = (
        f"Update from feeds input bot since {utils_obj.start_date.strftime('%Y-%m-%d')}"
    )
    feeds_processed_str = "- " + "\n- ".join(feeds_processed)
    body = f"This PR created automatically by feed bot.\n\nFeeds processed:\n{feeds_processed_str}"
    utils_obj.create_pull_request(title, body)


if __name__ == "__main__":
    main()