# -*- coding: utf-8 -*-
"""Tag content type."""

from five import grok
from plone import api
from plone.directives import form
from plone.indexer.decorator import indexer
from zope import schema
from zope.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from tribuna.content import _


class ITag(form.Schema):
    """Interface for the Tag content type."""

    title = schema.TextLine(
        title=_(u"Name"),
    )

    highlight_in_navigation = schema.Bool(
        title=_(u"Highlight tag in navigation?")
    )


@indexer(ITag)
def highlight_in_navigation_indexer(obj):
    """Indexed for highlight_in_navigation for Tags."""
    return obj.highlight_in_navigation


@grok.subscribe(ITag, IObjectModifiedEvent)
def object_edited(context, event):
    """
    Method that sets the subject when a tag is modified.

    :param    context: Current context
    :type     context: Context object
    :param    event:   Event that gets called when object is modified
    :type     event:   IEvent
    """
    context.subject = (context.title, )


@grok.subscribe(ITag, IObjectAddedEvent)
def object_added(context, event):
    """
    Method that sets the subject when a tag is created.

    :param    context: Current context
    :type     context: Context object
    :param    event:   Event that gets called when object is created
    :type     event:   IEvent
    """
    context.subject = (context.title, )


# XXX: Right now, we don't want to delete tags from all content. The tags will
# be saved and everything will "magically" appear again if we re-add the tag
# with the same name. Need to decide if we want to give the option to delete
# tag from all content on deletion and what to do on tag renaming.

# @grok.subscribe(ITag, IObjectRemovedEvent)
# def object_deleted(context, event):
#     # First time it's called, before the "delete or no" popup
#     if(context.REQUEST.method == 'GET'):
#         pass
#     # Second and third time it's called, after popup
#     elif(context.REQUEST.method == 'POST'):
#         try:
#             context.REQUEST.form['form.submitted']
#             # Second time
#         except:
#             # Third time
#             catalog = api.portal.get_tool(name='portal_catalog')
#             all_tags = [i.getObject() for i in catalog(Subject={
#                 'query': (context.title, ),
#                 'operator': 'and',
#             })]
#             for item in all_tags:
#                 item.setSubject(tuple((
#                     i for i in item.Subject() if i != context.title
#                 )
#                 ))


class View(grok.View):
    grok.context(ITag)
    grok.require('zope2.View')

    def articles(self):
        """
        Method for getting all articles that belong to this tag.

        :returns: Articles of this tag
        :rtype:   list
        """
        catalog = api.portal.get_tool(name='portal_catalog')
        all_articles = catalog(portal_type="tribuna.content.article",
                               Subject=[self.context.title])
        return [article for article in all_articles
                if article.review_state == 'published']
