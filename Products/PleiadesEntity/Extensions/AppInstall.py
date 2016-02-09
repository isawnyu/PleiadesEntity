import transaction
from Products.CMFCore.utils import getToolByName

indexes = [
    ('getTimePeriods', 'KeywordIndex'),
    ]

EXTENSION_PROFILES = ('Products.PleiadesEntity:default',)

def install(self):
    portal_quickinstaller = getToolByName(self, 'portal_quickinstaller')
    portal_setup = getToolByName(self, 'portal_setup')
    for extension_id in EXTENSION_PROFILES:
        portal_setup.runAllImportStepsFromProfile(
            'profile-%s' % extension_id, purge_old=False
            )
        product_name = extension_id.split(':')[0]
        portal_quickinstaller.notifyInstalled(product_name)
        transaction.savepoint()
