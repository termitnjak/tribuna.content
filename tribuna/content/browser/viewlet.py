#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Viewlets."""


from plone import api
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets import common as base
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from tribuna.content.homepage import HomePageView
from tribuna.content.mainpage import MainPageView
from tribuna.content.utils import get_articles


class NavbarViewlet(base.ViewletBase):
    """Our custom global navigation viewlet."""
    implements(IViewlet)

    def default_page_url(self):
        portal = api.portal.get()
        entry_pages = portal["entry-pages"]
        default_page = entry_pages[entry_pages.getDefaultPage()]

        return default_page.absolute_url()


class DefaultSessionViewlet(BrowserView):
    """Viewlet for managing the session"""

    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(DefaultSessionViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        pass

    def set_default_content_list(self, session):
        get_articles(session)

    def set_default_view_type(self, session):
        session.set('view_type', 'drag')

    def reset_session(self):
        """Check if we have the data, if we don't, initialize session
        parameters.
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        get_default = self.request.get('default')
        if get_default and "portlet_data" in session.keys():
            del session["portlet_data"]
        if get_default or 'content_list' not in session.keys():
            self.set_default_content_list(session)
        if get_default or 'view_type' not in session.keys():
            self.set_default_view_type(session)

    def render(self):
        if (isinstance(self.__parent__, HomePageView)
                or isinstance(self.__parent__, MainPageView)):
            self.reset_session()
        return ""