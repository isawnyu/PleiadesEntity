from Products.PleiadesEntity.browser import portlets
from Products.PleiadesEntity.tests.base import PleiadesEntityTestCase
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility, getMultiAdapter


class TestLinkedDataPortlet(PleiadesEntityTestCase):

    def afterSetUp(self):
        self.setRoles(("Manager",))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType, name="Products.PleiadesEntity.LinkedDataPortlet"
        )
        self.assertEquals(portlet.addview, "Products.PleiadesEntity.LinkedDataPortlet")

    def test_interfaces(self):
        portlet = portlets.LinkedDataPortletAssignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType, name="Products.PleiadesEntity.LinkedDataPortlet"
        )
        mapping = self.portal.restrictedTraverse("++contextportlets++plone.rightcolumn")
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse("+/" + portlet.addview)

        addview()

        self.assertEquals(len(mapping), 1)
        self.assertTrue(
            isinstance(mapping.values()[0], portlets.LinkedDataPortletAssignment)
        )

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse("@@plone")
        manager = getUtility(
            IPortletManager, name="plone.rightcolumn", context=self.portal
        )

        assignment = portlets.LinkedDataPortletAssignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )
        self.assertTrue(isinstance(renderer, portlets.LinkedDataPortletRenderer))
