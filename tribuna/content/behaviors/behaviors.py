"""Behaviours to assign tags (to ideas).

Includes a form field and a behaviour adapter that stores the data in the
standard Subject field.
"""

from collective.miscbehaviors.behavior.utils import context_property
from five import grok
from plone import api
from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from plone.indexer.decorator import indexer
from plone.namedfile import field as namedfile
from Products.CMFCore.interfaces import IDublinCore
from rwproperty import getproperty, setproperty
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from tribuna.content import _


class ITermitnjakLeadImage(form.Schema):
    """Add tags to content
    """

    image = namedfile.NamedBlobImage(
        title=_(u"Lead Image"),
        description=u"",
        required=True,
    )

    imageCaption = schema.TextLine(
        title=_(u"Lead Image Caption"),
        description=u"",
        required=True,
    )

alsoProvides(ITermitnjakLeadImage, form.IFormFieldProvider)


class TermitnjakLeadImage(object):
    """
       Adapter for Lead Image
    """
    implements(ITermitnjakLeadImage)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    imageCaption = context_property('imageCaption')
    image = context_property('image')


class TagsList(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog({
            'portal_type': 'tribuna.content.tag',
            'review_state': 'published',
        })

        terms = []

        for item in items:
            term = item.Title
            terms.append(SimpleVocabulary.createTerm(term, term, term))

        return SimpleVocabulary(terms)


# class ITags(form.Schema):
#     """Add tags to content
#     """

#     form.widget(tags=CheckBoxFieldWidget)
#     tags = schema.List(
#         title=_(u'label_tags'),
#         description=_(
#             u'help_tags',
#             default=u'Mine test.'
#         ),
#         value_type=schema.Choice(source=TagsList()),
#     )

from collective.z3cform.widgets.token_input_widget import TokenInputFieldWidget


class ITags(form.Schema):
    """
        Auto-complete tags
    """

    form.widget(tags_old=CheckBoxFieldWidget)
    tags_old = schema.List(
        title=_(u'label_tags'),
        description=_(
            u'help_tags',
            default=u'Mine test.'
        ),
        value_type=schema.Choice(source=TagsList()),
    )

    form.widget(tags_new=TokenInputFieldWidget)
    tags_new = schema.List(
        title=_(u"Categories"),
        value_type=schema.TextLine(),
        default=[],
    )

alsoProvides(ITags, form.IFormFieldProvider)


class Tags(object):
    """Store tags in the Dublin Core metadata Subject field. This makes
    tags easy to search for.
    """
    implements(ITags)
    adapts(IDublinCore)

    def __init__(self, context):
        self.context = context

    @getproperty
    def tags_old(self):
        return set(self.context.Subject())
    @setproperty
    def tags_old(self, value):
        if value is None:
            value = ()
        self.context.setSubject(tuple(value))

    @getproperty
    def tags_new(self):
        return set(self.context.Subject())
    @setproperty
    def tags_new(self, value):
        if value is None:
            value = ()
        old_tags = set(self.context.Subject())
        # Set Subject as an union of  tags in tags_old and tags_new
        self.context.setSubject(tuple(old_tags.union(value)))

        # Get all 'new' tags
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog({
            'portal_type': 'tribuna.content.tag',
        })
        titles = set(i.Title for i in items)
        svalue = set(value)
        svalue -= titles

        site = api.portal.get()
        for title in svalue:
            name = title.replace(' ', '-').lower()
            site['tags'].invokeFactory('tribuna.content.tag', name)
            site['tags'][name].title = title


class ILockOnHomePage(form.Schema):
    """Behavior for locking our content item on home page
    """

    locked_on_home = schema.Bool(
        title=_(u"Is article locked on first page?")
    )

alsoProvides(ILockOnHomePage, form.IFormFieldProvider)


class LockOnHomePage(object):
    """
       Adapter for LockOnHomePage
    """
    implements(ILockOnHomePage)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    locked_on_home = context_property('locked_on_home')


@indexer(ILockOnHomePage)
def lock_on_home_page_indexer(obj):
    """
    """
    return obj.locked_on_home