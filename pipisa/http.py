from .exceptions import *
from html import unescape


class HTTPClient:
    def __init__(self, url, session, logged_in):
        self.url = url
        self.session = session
        self.logged_in = logged_in

    async def close(self):
        await self.session.close()

    async def get_token(self, type):
        url = f"{self.url}?action=query&meta=tokens&type={type}&format=json"
        async with self.session.get(url) as r:
            data = await r.json()

        try:
            return data["query"]["tokens"][f"{type}token"]
        except KeyError:
            raise TGE(data["error"]["info"])

    async def get_random_pages(self, num, namespace):
        url = f"{self.url}?action=query&list=random&rnlimit={num}&rnnamespace={namespace}&format=json"
        async with self.session.get(url) as r:
            data = await r.json()

        return [p["title"] for p in data["query"]["random"]]

    async def create_account(self, json):
        token = await self.get_token("createaccount")
        json["action"] = "createaccount"
        json["format"] = "json"
        json["createreturnurl"] = self.url
        json["createtoken"] = token

        async with self.session.post(self.url, data=json) as r:
            json = await r.json()
        if json["createaccount"]["status"] == "FAIL":
            raise CAE(json["createaccount"]["messagecode"])
        return True

    async def userrights(self, json):
        token = await self.get_token("userrights")
        json["action"] = "userrights"
        json["format"] = "json"
        json["token"] = token
        async with self.session.post(self.url, data=json) as r:
            json = await r.json()
        if "warnings" in json.keys():
            raise IGE(json["warnings"]["userrights"])
        try:
            if not json["userrights"]["added"] and not json["userrights"]["removed"]:
                raise URNCE(
                    "User rights are the same after this action or current session is not allowed to change user rights"
                )

        except KeyError:
            if "error" in json.keys():
                if json["error"]["code"] == "nosuchuser":
                    raise NSUE(json["error"]["info"])

        return True

    async def login(self, json):
         token = await self.get_token("login")
        json["action"] = "clientlogin"
        json["loginreturnurl"] = self.url
        json["format"] = "json"
        json["rememberMe"] = 1
        json["logintoken"] = token

        async with self.session.post(self.url, data=json) as r:
            json = await r.json()
        if json["clientlogin"]["status"] == "FAIL":
            raise LF(json["clientlogin"]["message"])
        self.logged_in = True
        return True

    async def get_html(self, page):
        url = f"{self.url}?action=parse&page={page}&format=json"
        async with self.session.get(url) as r:
            data = await r.json()
        try:
            html = data["parse"]["text"]["*"]
        except KeyError:
            raise PNF("ЛАЛАЛАЛАЛА")
        unescape(html)
        return html

    async def get_markdown(self, page):
        url = f"{self.url}?action=query&titles={page}&prop=revisions&rvprop=content&format=json&formatversion=2"
        async with self.session.get(url) as r:
            data = await r.json()
        try:
            md = data["query"]["pages"][0]["revisions"][0]["content"]
        except KeyError:
            raise PNF("ЛАЛАЛАЛАЛА")
        unescape(md)
        return md

    async def get_summary(self, page):
        url = f"{self.url}?format=json&action=query&prop=extracts&exintro=&explaintext=&titles={page}"
        async with self.session.get(url) as r:
            data = await r.json()
        try:
            pages = data["query"]["pages"]
            summary = pages[list(pages.keys())[0]]["extract"]
        except KeyError:
            raise PNF("ЛАЛАЛАЛАЛА")
        unescape(summary)
        return summary

    async def edit_page(self, json):
         if self.logged_in:
            token = await self.get_token("csrf")
        else:
            token = "+\\"
        json["action"] = "edit"
        json["format"] = "json"
        json["token"] = token
        async with self.session.post(self.url, data=json) as r:
            data = await r.json()
        if data.get("error"):
            raise EE(data["error"]["info"])
        return True

    async def opensearch(self, title, limit, namespace):
        url = f"{self.url}?action=opensearch&search={title}&limit={limit}&namespace={namespace}&format=json"
        async with self.session.get(url) as r:
            data = await r.json()
        return data[1]

    async def get_urls(self, title):
        url = f"{self.url}?action=query&format=json&prop=info&generator=allpages&inprop=url&gapfrom={title}&gaplimit=1"
        async with self.session.get(url) as r:
            data = await r.json()
        pages = data["query"].get("pages")
        if not pages:
            raise PNF("ЛАЛАЛАЛАЛА")
        page = list(pages.items())[0][1]
        return [page["fullurl"], page["editurl"]]

    async def get_media(self, title):
        url = f"{self.url}?action=query&titles={title}&format=json&prop=images"
        async with self.session.get(url) as r:
            data = await r.json()
        pages = data["query"]["pages"]
        images = list(pages.values())[0].get("images")
        if not images:
            return []
        query = "|".join([i["title"] for i in images])
        url = f"{self.url}?action=query&titles={query}&format=json&prop=imageinfo&iiprop=url"
        async with self.session.get(url) as r:
            data = await r.json()
        pages = data["query"]["pages"]
        urls = [
            i["imageinfo"][0]["url"] for i in pages.values()
        ] 
        return urls
