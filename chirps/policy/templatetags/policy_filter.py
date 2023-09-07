"""Policy template filters."""
from django import template

register = template.Library()


@register.filter
def group_by_rule_type(rules):
    """Group a list of rules by their rule type."""
    regex_rules = []
    multiquery_rules = []

    for rule in rules:
        if rule.rule_type == 'regex':
            regex_rules.append(rule)
        elif rule.rule_type == 'multiquery':
            multiquery_rules.append(rule)

    return {'regex': regex_rules, 'multiquery': multiquery_rules}
