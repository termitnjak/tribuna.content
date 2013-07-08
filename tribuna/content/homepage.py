from five import grok
from plone import api
from zope.interface import Interface


class HomePageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('home-page')

    def is_text_view(self):
        """
            Get data from session, if it isn't there, send True (text is the
            basic view)
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('view_type' in session.keys()):
            if session['view_type'] == 'drag':
                return False
        return True

    def articles(self):
        """ Return a catalog search result of articles that have this tag
        """

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('content_list' in session.keys()):
            return session['content_list']
        return []

    def only_one_tag(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('portlet_data' in session.keys()):
            return len(session['portlet_data']['tags']) == 1
        return False

    def tag_description(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        title = session['portlet_data']['tags'][0]
        catalog = api.portal.get_tool(name='portal_catalog')
        tag = catalog(
            Title=title,
            portal_type='tribuna.content.tag',
        )[0].getObject()
        return tag.description
