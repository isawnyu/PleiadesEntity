from . import ContentExportAdapter
from . import TemporalExportAdapter
from . import WorkExportAdapter
from . import archetypes_getter
from . import memoize_all_methods


@memoize_all_methods
class NameExportAdapter(
        WorkExportAdapter, TemporalExportAdapter, ContentExportAdapter):

    def title(self):
        raise NotImplementedError

    attested = archetypes_getter('nameAttested')
    language = archetypes_getter('nameLanguage')
    romanized = archetypes_getter('nameTransliterated')
    nameType = archetypes_getter('nameType')
    transcriptionAccuracy = archetypes_getter('accuracy')
    transcriptionCompleteness = archetypes_getter('completeness')
    associationCertainty = archetypes_getter('associationCertainty')
    details = archetypes_getter('text')
