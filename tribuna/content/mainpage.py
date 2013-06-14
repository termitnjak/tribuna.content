from five import grok
from plone import api
from zope.interface import Interface

from tribuna.content import _


class MainPageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('main-page')

    def articles(self):
        """ Return a catalog search result of articles that have this tag
        """

        catalog = api.portal.get_tool(name='portal_catalog')

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        tags = session["portlet_data"]["tags"]
        if session["portlet_data"]["sort_type"] is u'union':
            articles = catalog(
                portal_type="tribuna.content.article",
                review_state="published",
                sort_on="Date",
                Subject={"query": tags, "operator": "or"}
            )
            articles = [article.getObject() for article in articles]
            return articles
        else:
            articles = catalog(
                portal_type="tribuna.content.article",
                review_state="published",
                sort_on="Date",
                Subject={"query": tags, "operator": "and"}
            )
            articles = [article.getObject() for article in articles]
            return articles
