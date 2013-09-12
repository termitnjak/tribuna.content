#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Portlet for filterting/searching the content."""

from five import grok
from plone import api
from plone.app.portlets.portlets import base
from plone.directives import form
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from tribuna.content import _
from tribuna.content.utils import get_articles
from tribuna.content.utils import TagsList
from tribuna.content.utils import TagsListHighlighted

# SimpleTerm(value (actual value), token (request), title (shown in browser))
# tags, sort_on, content_filters, operator


class ISidebarForm(form.Schema):
    """ Defining form fields for sidebar portlet """

    form.widget(tags=CheckBoxFieldWidget)
    tags = schema.List(
        title=_(u"Tags"),
        value_type=schema.Choice(source=TagsListHighlighted()),
        required=False,
        default=[],
    )

    form.widget(all_tags=CheckBoxFieldWidget)
    all_tags = schema.List(
        title=_(u"All tags"),
        value_type=schema.Choice(source=TagsList()),
        required=False,
        default=[],
    )

    sort_on = schema.Choice(
        title=_(u"Type of sorting"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('latest', 'latest', _(u'Latest')),
            SimpleTerm('comments', 'comments', _(u'Nr. of comments')),
        ]),
    )

    form.widget(content_filters=CheckBoxFieldWidget)
    content_filters = schema.List(
        title=_(u"Content filters"),
        value_type=schema.Choice(source=SimpleVocabulary([
            SimpleTerm('all', 'all', _(u'All')),
            SimpleTerm('article', 'article', _(u'Article')),
            SimpleTerm('comment', 'comment', _(u'Comment')),
            SimpleTerm('image', 'image', _(u'Image')),
        ])),
        required=False,
    )


@form.default_value(field=ISidebarForm['tags'])
def default_tags(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if "portlet_data" in session.keys():
        return session["portlet_data"]["tags"]
    else:
        return []


@form.default_value(field=ISidebarForm['all_tags'])
def default_all_tags(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if "portlet_data" in session.keys():
        return session["portlet_data"]["tags"]
    else:
        return []


@form.default_value(field=ISidebarForm['sort_on'])
def default_sort_on(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if "portlet_data" in session.keys():
        return session["portlet_data"]["sort_on"]
    else:
        return "latest"


@form.default_value(field=ISidebarForm['content_filters'])
def default_content_filters(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if "portlet_data" in session.keys():
        if 'all' in session['portlet_data']['content_filters']:
            session['portlet_data']['content_filters'].remove('all')
        all_filters = ['article', 'comment', 'image']
        if session['portlet_data']['content_filters'] == all_filters:
            return session["portlet_data"]["content_filters"] + ['all']
        return session["portlet_data"]["content_filters"]
    else:
        return []


class SidebarForm(form.SchemaForm):
    """ Defining form handler for sidebar portlet

    """
    grok.name('my-form')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = ISidebarForm
    ignoreContext = True

    label = _(u"Select appropriate tags")
    description = _(u"Tags selection form")

    def buildGetArgs(self):
            st = ""
            name = 'form.widgets.all_tags'
            if name in self.request.form:
                st += '/' + ','.join(self.request.form[name])

            name = 'form.widgets.content_filters'
            st += '&filters='
            if name in self.request.form:
                st += ','.join((i for i in self.request.form[name]
                                if i != 'all'))
            else:
                st += "None"

            name = 'form.widgets.sort_on'
            if name in self.request.form:
                st += '&sort_on=' + ','.join(self.request.form[name])

            first_letter = st.find('&')
            if first_letter != -1:
                st = st[:first_letter] + '?' + st[first_letter + 1:]
            return st

    @button.buttonAndHandler(_(u'Filter'))
    def handleApply(self, action):
        """
        Method for setting selected filters in session and setting correct
        articles

        :param    action: action selected on form
        :type     action: str
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set("portlet_data", data)
        session["search-view"] = {}
        session["search-view"]['active'] = False
        get_articles(session)
        get_args = self.buildGetArgs()
        url = self.context.url().split('/')
        if url[-1] == 'home':
            url[-1] = 'tags'
        url = '/'.join(url)
        self.request.response.redirect(url + get_args)

    @button.buttonAndHandler(_(u'Text'))
    def handleApply(self, action):
        """
        Method for setting text view

        :param    action: action selected on form
        :type     action: str
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set('view_type', 'text')
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_(u'Drag'))
    def handleApply(self, action):
        """
        Method for setting drag view

        :param    action: action selected on form
        :type     action: str
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set('view_type', 'drag')
        self.request.response.redirect(self.request.getURL())


class ISidebarPortlet(IPortletDataProvider):
    pass


class Assignment(base.Assignment):
    implements(ISidebarPortlet)

    heading = _(u"Sidebar navigation")
    description = _(u"Use this portlet for tag navigation.")

    title = _(u"Sidebar portlet")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('sidebar.pt')

    def portlet_data(self):
        """
        Method for getting sidebar form for rendering

        :returns: our sidebar form
        :rtype:   Form object
        """
        form1 = SidebarForm(self.context, self.request)
        form1.update()
        return form1


class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()
