from import_export import resources
from .models import AntiCheating, ANTLRScore, QuestionProductionScore,School


class AntiCheatingResource(resources.ModelResource):
    class Meta:
        model = AntiCheating
        exclude = []


class ANTLRScoreResource(resources.ModelResource):
    class Meta:
        model = ANTLRScore
        exclude = ['id']


class QuestionProductionScoreResource(resources.ModelResource):
    class Meta:
        model = QuestionProductionScore
        exclude = []


class AntiCheatingSummaryResource(resources.ModelResource):
    class Meta:
        model = AntiCheating
        fields = ['user', ]

class SchoolAdminResource(resources.ModelResource):
    class Meta:
        model = School
        skip_unchanged = True
        report_skipped = True
        exclude = ('id',)
        import_id_fields = ('school_name',)
        # fileds = ['school_name']