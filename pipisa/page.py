import re
from collections import namedtuple


class Page:
    def __init__(self, page_title, wiki):
        self.title = page_title
        self.wiki = wiki

    def __repr__(self):
        return f"<aiowiki.page.Page title={self.title}>"

    def _cleanhtml(self, raw_html):
        cleantext = re.sub(r"<.*?>", "", raw_html)

        cleantext = re.sub("(<!--.*?-->)", "", cleantext, flags=re.DOTALL)

        cleantext = "\n".join([r.strip() for r in cleantext.split("\n")])

        cleantext = re.sub(r"\n\n+", "\n\n", cleantext)

        cleantext = cleantext.replace("[edit]", "")
        cleantext = cleantext.replace("(edit)", "")

        return cleantext

    async def html(self):
        return await self.wiki.http.get_html(self.title)

    async def markdown(self):
        return await self.wiki.http.get_markdown(self.title)

    async def text(self):
        raw_html = await self.html()
        return self._cleanhtml(raw_html)

    async def summary(self):
        return await self.wiki.http.get_summary(self.title)

    async def urls(self):
        url_tuple = namedtuple("WikiURLs", ["view", "edit"])
        urls = await self.wiki.http.get_urls(self.title)
        return url_tuple(urls[0], urls[1])

    async def media(self):
        return await self.wiki.http.get_media(self.title)

    async def edit(self, content: str):
        json = {"title": self.title, "text": content}
        await self.wiki.http.edit_page(json)
        return True
