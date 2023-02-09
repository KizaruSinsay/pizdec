import aiohttp

from .page import Page
from .http import HTTPClient


class Wiki:

    def __init__(self, base_url: str, session: aiohttp.ClientSession = None):
        session = session or aiohttp.ClientSession()
        self.http = HTTPClient(url=base_url, session=session, logged_in=False)
        self.url = base_url

    def __repr__(self):
        return f"<pipisa.wiki.Wiki url={self.url}>"

    @classmethod
    def wikipedia(cls, language="en", *args, **kwargs):
        return cls(
            f"https://{language.lower()}.wikipedia.org/w/api.php", *args, **kwargs
        )

    async def close(self):
        await self.http.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        await self.close()

    async def get_token(self, type: str = "csrf"):
        return await self.http.get_token(type)

    async def get_random_pages(self, num: int = 1, namespace: str = "*"):
        data = await self.http.get_random_pages(num, namespace)

        return [self.get_page(page) for page in data]

    async def create_account(
        self, username: str, password: str, email: str = None, real_name: str = None
    ):
        json = {
            "username": username,
            "password": password,
            "retype": password,
            "realname": real_name,
        }
        if email:
            json["email"] = email

        await self.http.create_account(json)
        return True

    async def userrights(self, username: str, action: str, group: str):
        if action not in ["add", "remove"]:
            raise ValueError("action must be 'add' or 'remove' only")
        json = {"user": username, action: group}
        return await self.http.userrights(json)

    async def login(self, username: str, password: str):
        json = {"username": username, "password": password}

        await self.http.login(json)
        return True

    def get_page(self, page_title: str):
        return Page(page_title, wiki=self)

    async def opensearch(
        self, search_query: str, limit: int = 10, namespace: str = "0"
    ):
         return [
            Page(title, wiki=self)
            for title in await self.http.opensearch(search_query, limit, namespace)
        ]
