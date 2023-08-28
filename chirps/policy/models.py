"""Models for the policy application."""
import re
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from asset.models import SearchResult
from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
from embedding.utils import create_embedding
from fernet_fields import EncryptedTextField
from polymorphic.models import PolymorphicModel
from severity.models import Severity


class Policy(models.Model):
    """Model for what to do when scanning an asset."""

    # True to hide this policy from the user
    archived = models.BooleanField(default=False)

    name = models.CharField(max_length=256)
    description = models.TextField()

    # True if this policy is a template for other policies
    is_template = models.BooleanField(default=False)

    # Bind this policy to a user if it isn't a template
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # The current version of the policy
    current_version = models.ForeignKey(
        'PolicyVersion', on_delete=models.CASCADE, related_name='current_version', null=True, blank=True
    )

    def __str__(self):
        """Stringify the name"""
        return self.name


class PolicyVersion(models.Model):
    """Model to track a revision of the policy."""

    number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)

    @property
    def is_template(self):
        """Convenience method to check if the parent policy is a template"""
        return self.policy.is_template


@dataclass
class RuleExecuteArgs:
    """Dataclass for passing in arguments to the rule executor."""

    scan_asset: 'asset.ScanAsset'
    asset: 'asset.BaseAsset'


class BaseRule(PolymorphicModel):
    """Base class that all rules will inherit from."""

    name = models.CharField(max_length=256)

    rule_type = None

    # ForeignKey relationship to the Severity model
    severity = models.ForeignKey(Severity, on_delete=models.CASCADE)

    # Foreign Key to the policy this rule belongs to
    policy = models.ForeignKey(PolicyVersion, on_delete=models.CASCADE, related_name='rules')

    def __str__(self):
        """Stringify the name"""
        return self.name

    def execute(self, args: RuleExecuteArgs) -> None:
        """Execute the rule against an asset."""
        raise NotImplementedError(f'{self.__class__.__name__} does not implement execute()')


class RegexRule(BaseRule):
    """A step to execute within a policy."""

    rule_type = 'regex'
    edit_template = 'policy/edit_regex_rule.html'
    create_template = 'policy/create_regex_rule.html'

    # Query to run against the asset
    query_string = models.TextField()

    # Embedding of the query string
    query_embedding = models.TextField(null=True, blank=True)

    # Regular expression to run against the response documents
    regex_test = models.TextField()

    def execute(self, args: RuleExecuteArgs) -> None:
        """Execute the rule against an asset."""
        if args.asset.REQUIRES_EMBEDDINGS:

            # If using a template policy, we don't need to filter by user
            add_user_filter = not self.policy.is_template
            user = args.scan_asset.scan.scan_version.scan.user if add_user_filter else None
            embedding = create_embedding(
                self.query_string, args.asset.embedding_model, args.asset.embedding_model_service, user
            )
            query = embedding.vectors
        else:
            query = self.query_string

        # Issue the search query to the asset provider
        results: list[SearchResult] = args.asset.search(query, max_results=100)

        for search_result in results:

            # Create the result. We'll flip the result flag to True if any findings are found
            result = RegexResult(rule=self, text=search_result.data, scan_asset=args.scan_asset)
            result.save()

            # Run the regex against the text
            for match in re.finditer(self.regex_test, search_result.data):

                # Persist the finding
                finding = RegexFinding(
                    result=result,
                    offset=match.start(),
                    length=match.end() - match.start(),
                    source_id=search_result.source_id,
                )
                finding.save()


class BaseResult(models.Model):
    """Base model for a single result from a rule."""

    # Scan asset that the result belongs to
    scan_asset = models.ForeignKey('scan.ScanAsset', on_delete=models.CASCADE, related_name='results')

    # The rule that was used to scan the text
    rule = models.ForeignKey(BaseRule, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def has_findings(self) -> bool:
        """Return True if the result has findings, False otherwise."""
        if self.findings_count():
            return True

        return False

    @abstractmethod
    def findings_count(self) -> int:
        """Return the number of findings associated with this result."""
        raise NotImplementedError

    def __str__(self):
        """Stringify the rule name and scan ID"""
        return f'{self.rule.name} - {self.scan_asset.scan.id}'


class RegexResult(BaseResult):
    """Model for a single result from a Regex rule."""

    # The rule that was used to scan the text
    rule = models.ForeignKey(RegexRule, on_delete=models.CASCADE)

    # The raw text (encrypted at REST) that was scanned
    text = EncryptedTextField()

    def findings_count(self) -> int:
        """Convenience method to get the number of findings associated with this result."""
        return self.findings.count()


class BaseFinding(models.Model):
    """Base model to identify the location of a finding within a result."""

    result = models.ForeignKey(BaseResult, on_delete=models.CASCADE, related_name='findings')

    class Meta:
        abstract = True

    def __str__(self):
        """Stringify the finding"""
        return f'{self.result}'


class RegexFinding(BaseFinding):
    """Model to identify the location of a finding within a Regex result."""

    result = models.ForeignKey(RegexResult, on_delete=models.CASCADE, related_name='findings')
    source_id = models.TextField(blank=True, null=True)
    offset = models.IntegerField()
    length = models.IntegerField()

    def text(self):
        """Return the text of the finding."""
        return self.result.text[self.offset : self.offset + self.length]

    def surrounding_text(self, preview_size: int = 20):
        """return the text of the finding, with some surrounding context."""
        buffer = self.result.text[self.offset - preview_size : self.offset - 1]
        buffer += "<span class='text-danger'>"
        buffer += self.result.text[self.offset : self.offset + self.length]
        buffer += '</span>'
        buffer += self.result.text[self.offset + self.length + 1 : self.offset + self.length + preview_size - 1]
        return mark_safe(buffer)

    def with_highlight(self):
        """return the entire text searched by the finding's rule - highlight the finding."""
        buffer = self.result.text[0 : self.offset - 1]
        buffer += "<span class='bg-danger text-white'>"
        buffer += self.result.text[self.offset : self.offset + self.length]
        buffer += '</span>'
        buffer += self.result.text[self.offset + self.length + 1 :]
        return mark_safe(buffer)


class MultiQueryRule(BaseRule):
    """Multi-query rule."""

    rule_type = 'multiquery'
    edit_template = 'policy/edit_multiquery_rule.html'
    create_template = 'policy/create_multiquery_rule.html'

    # Description of the task to be completed
    task_description = models.TextField(max_length=256)

    # Success outcome of the task
    success_outcome = models.CharField(max_length=256)


def rule_classes(base_class: Any) -> dict[str, type]:
    """Get all subclasses of a given class recursively."""
    subclasses_dict = {}
    for subclass in base_class.__subclasses__():
        subclasses_dict[subclass.rule_type] = subclass
        subclasses_dict.update(rule_classes(subclass))
    return subclasses_dict


RULES = rule_classes(BaseRule)
