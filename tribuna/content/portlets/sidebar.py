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
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm


from tribuna.content import _
from tribuna.content.utils import tagsPublished


class TagsList(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        items = tagsPublished()
        terms = [SimpleVocabulary.createTerm(i, i, i) for i in items]
        return SimpleVocabulary(terms)


class ISidebarForm(form.Schema):
    """ Defining form fields for sidebar portlet """

    form.widget(tags=CheckBoxFieldWidget)
    tags = schema.List(
        title=u"Tags",
        value_type=schema.Choice(source=TagsList()),
    )

    sort_choice = schema.Choice(
        vocabulary=SimpleVocabulary([
            SimpleTerm(u'comments', u'comments', u'comments'),
            SimpleTerm(u'latest', u'latest', u'latest'),
        ]),
        title=u"Type of sorting articles",
    )


@form.default_value(field=ISidebarForm['tags'])
def default_tags(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if(u"tags" in session.keys()):
        return session[u"tags"][u"tags"]
    else:
        return []


@form.default_value(field=ISidebarForm['sort_choice'])
def default_sort_choice(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if(u"tags" in session.keys()):
        if(u"sort_choice" in session["tags"].keys()):
            return session[u"tags"][u"sort_choice"]
    else:
        return u"latest"


class SidebarForm(form.SchemaForm):
    """ Defining form handler for sidebar portlet

    """
    grok.name('my-form')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = ISidebarForm
    ignoreContext = True

    label = u"Select appropriate tags"
    description = u"Tags selection form"

    def _handleApply(self, action, is_union):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set("tags", data)
        session.set("is_union", is_union)
        url = api.portal.get().absolute_url()
        self.request.response.redirect("{0}/@@main-page".format(url))

    @button.buttonAndHandler(u'Send-Union')
    def handleApply(self, action):
        self._handleApply(action, True)

    @button.buttonAndHandler(u'Send-Intersection')
    def handleApply(self, action):
        self._handleApply(action, False)

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """


class ISidebarPortlet(IPortletDataProvider):
    pass


class Assignment(base.Assignment):
    implements(ISidebarPortlet)

    heading = _(u"Sidebar navigation")
    description = _(u"Use this portlet for sidebag tag navigation.")

    title = _(u"Sidebar portlet")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('sidebar.pt')

    def tags(self):
        """Return a catalog search result of articles that have this tag
        """
        form1 = SidebarForm(self.context, self.request)
        form1.update()
        return form1


class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()