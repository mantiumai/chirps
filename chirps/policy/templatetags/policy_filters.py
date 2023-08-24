from django import template

register = template.Library()


@register.filter
def get_edit_rule_template(rule_class_templates, rule_type):
    """Get the edit template for the rule type."""
    return rule_class_templates[rule_type]['templates']['edit']
