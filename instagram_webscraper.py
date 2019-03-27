import requests
import re
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


class Error:

    def __init__(self, error: str):
        self.error: str = error

    def log_error(self) -> None:
        print(self.error)


class HTMLGetter:

    def __init__(self, url: str):
        self.url: str = url

    @staticmethod
    def _is_good_response(response) -> bool:
        content_type: str = response.headers["Content-Type"].lower()
        return response.status_code == 200 and content_type and content_type.find("html") > -1

    def get_raw_html(self) -> "bytes":
        try:
            with closing(requests.get(url=self.url, stream=True)) as response:
                if self._is_good_response(response):
                    return response.content
                else:
                    return None

        except RequestException as e:
            Error.log_error("Error during request to {} to {}").format(self.url, str(e))


class InstagramHandler:

    def __init__(self, username: str):
        self.username: str = username

    def instagram_username(self) -> str:
        return "@" + self.username

    def instagram_user_url(self) -> str:
        return "https://www.instagram.com/" + self.username + "/"

    def get_meta_tag_with_followers_and_following(self, meta_tags: list) -> str:
        n: int = len(meta_tags)

        for i in range(1, n):
            if "Following" in meta_tags[i].get("content"):
                meta_tag: str = meta_tags[i].get("content")
                return meta_tag

    def get_number_of_followers(self, meta_tags: list) -> str:
        meta_tag = self.get_meta_tag_with_followers_and_following(meta_tags)
        followers_pattern: "re" = re.compile(r"(\d{1,3}(\.\d[km])?|\d{1,4}) Followers")
        match: "re" = re.search(pattern=followers_pattern, string=meta_tag)
        return match.group(0)

    def get_number_of_following(self, meta_tags: list) -> str:
        meta_tag = self.get_meta_tag_with_followers_and_following(meta_tags)
        following_pattern: "re" = re.compile(r"(\d{1,3}(\.\d[km])?|\d{1,4}) Following")
        match: "re" = re.search(pattern=following_pattern, string=meta_tag)
        return match.group(0)

    def print_user_info(self, meta_tags: list) -> None:
        print("user {} has {} and is {}".format(self.instagram_username(), self.get_number_of_followers(meta_tags),
                                                self.get_number_of_following(meta_tags)))


class Parser:

    def __init__(self, raw_html: "bytes"):
        self.raw_html: "bytes" = raw_html
        self.soup: "bs4.BeautifulSoup" = BeautifulSoup(raw_html, "html.parser")

    def get_all_meta_tags(self):
        return self.soup.find_all("meta")


if __name__ == "__main__":
    print("Enter Username: ")
    user_name: str = input()
    instagram_user: "instagramHandler" = InstagramHandler(user_name)
    url: str = instagram_user.instagram_user_url()
    raw_html: "bytes" = HTMLGetter(url=url).get_raw_html()
    parser: "parser" = Parser(raw_html)
    meta_tags: list = parser.get_all_meta_tags()
    instagram_user.print_user_info(meta_tags)