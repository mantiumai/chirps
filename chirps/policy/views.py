"""Views for the policy app."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from severity.forms import CreateSeverityForm, EditSeverityForm
from severity.models import Severity

from .forms import PolicyForm
from .models import Policy, PolicyVersion, RuleType, rule_classes


def save_rule(rule_type: str, **kwargs) -> None:
    """Create and save an instance of the rule."""
    rule = rule_classes.get(rule_type)
    if rule is None:
        raise ValueError(f'Invalid rule type: {rule_type}')

    rule(**kwargs).save()


def create_rules(rules: list[dict], policy_version: PolicyVersion) -> None:
    """Create and save a list of rules."""
    for rule in rules:
        # Retrieve the Severity instance from the database using the provided value
        severity = rule.pop('severity')
        severity_instance = Severity.objects.get(value=severity)

        type_ = rule.pop('type')
        save_rule(type_, severity=severity_instance, policy=policy_version, **rule)


@login_required
def dashboard(request):
    """Render the dashboard for the policy app.

    Args:
        request (HttpRequest): Django request object
    """
    # Fetch a list of all the available template and custom user policies
    templates = Policy.objects.filter(is_template=True).order_by('id')
    user_policies = Policy.objects.filter(user=request.user, archived=False).order_by('id')
    severities = Severity.objects.filter(archived=False).order_by('id')
    edit_severity_forms = {severity.id: EditSeverityForm(instance=severity) for severity in severities}
    create_severity_form = CreateSeverityForm()

    return render(
        request,
        'policy/dashboard.html',
        {
            'user_policies': user_policies,
            'templates': templates,
            'severities': severities,
            'edit_severity_forms': edit_severity_forms,
            'create_severity_form': create_severity_form,
        },
    )


@login_required
def create(request):
    """Render the create policy form.

    Args:
        request (HttpRequest): Django request object
    """
    if request.method == 'POST':
        form = PolicyForm(request.POST)
        form.full_clean()

        # Create the policy
        policy = Policy.objects.create(
            name=form.cleaned_data['name'], description=form.cleaned_data['description'], user=request.user
        )

        # Create the initial policy version
        policy_version = PolicyVersion.objects.create(number=1, policy=policy)

        # Save off the back reference of the current policy version to the policy.
        policy.current_version = policy_version
        policy.save()

        # Create the rules
        for rule in form.cleaned_data['rules']:
            # Retrieve the Severity instance from the database using the provided value
            severity_instance = Severity.objects.get(value=rule['rule_severity'])

            save_rule(
                rule['rule_type'],
                severity=severity_instance,
                policy=policy_version,
                name=rule['rule_name'],
                query_string=rule['rule_query_string'],
                regex_test=rule['rule_regex'],
            )

        # Add a success message
        messages.success(request, 'Policy created successfully.')

        # Redirect the user back to the dashboard
        return redirect('policy_dashboard')

    rule_types = [{'value': rt.value, 'name': rt.name} for rt in RuleType]
    return render(request, 'policy/create.html', {'rule_types': rule_types})


@login_required
def clone(request, policy_id):
    """Clone a template policy to a custom user policy

    Args:
        request (HttpRequest): Django request object
        policy_id (int): ID of the template policy to clone
    """
    policy = get_object_or_404(Policy, id=policy_id, is_template=True)

    cloned_policy = Policy.objects.create(
        name=policy.name,
        description=policy.description,
        user=request.user,
    )

    # Create the initial policy version
    policy_version = PolicyVersion.objects.create(number=1, policy=cloned_policy)

    # Pin the initial version as the current version
    cloned_policy.current_version = policy_version
    cloned_policy.save()

    # Clone the rules
    for rule in policy.current_version.rules.all():
        save_rule(
            rule.rule_type,
            name=rule.name,
            query_string=rule.query_string,
            regex_test=rule.regex_test,
            severity=rule.severity,
            policy=policy_version,
        )

    # Redirect to the edit page for the new policy
    return redirect('policy_edit', policy_id=cloned_policy.id)


@login_required
def edit(request, policy_id):
    """Render the edit policy form.

    Args:
        request (HttpRequest): Django request object
        policy_id (int): ID of the policy to edit
    """
    policy = get_object_or_404(Policy, id=policy_id, user=request.user)
    if request.method == 'POST':
        form = PolicyForm(request.POST)
        form.full_clean()
        policy.save()

        # Create a new policy version
        new_policy_version = PolicyVersion.objects.create(number=policy.current_version.number + 1, policy=policy)

        # Persist all of the rules against the new version
        for rule in form.cleaned_data['rules']:
            # Retrieve the Severity instance from the database using the provided value
            severity_instance = Severity.objects.get(value=rule['rule_severity'])

            save_rule(
                rule['rule_type'],
                name=rule['rule_name'],
                query_string=rule['rule_query_string'],
                regex_test=rule['rule_regex'],
                severity=severity_instance,
                policy=new_policy_version,
            )

        # Update the current version of the policy as well as the name and description
        policy.current_version = new_policy_version
        policy.name = form.cleaned_data['name']
        policy.description = form.cleaned_data['description']
        policy.save()

        # Add an info message
        messages.info(request, 'Policy changes saved.')

        # Redirect the user back to the dashboard
        return redirect('policy_dashboard')

    form = PolicyForm.from_policy(policy=policy)
    severities = Severity.objects.filter(archived=False)
    rule_types = [{'value': rt.value, 'name': rt.name} for rt in RuleType]
    return render(
        request,
        'policy/edit.html',
        {
            'policy': policy,
            'form': form,
            'severities': severities,
            'rule_types': rule_types,
            'rule_classes': rule_classes,
        },
    )


@login_required
def create_rule(request, rule_type: str):
    """Render a single row of a Rule for the create policy page."""
    severities = Severity.objects.filter(archived=False)
    template_name = rule_classes.get(rule_type).create_template
    rule_id = request.GET.get('rule_id', 0)
    next_rule_id = int(request.GET.get('rule_id', 0)) + 1

    return render(request, template_name, {'rule_id': rule_id, 'next_rule_id': next_rule_id, 'severities': severities})


@login_required
@require_http_methods(['DELETE'])
def delete_rule(request, rule_id):
    """Delete a single rule within a policy."""
    # If the rule_id is 0, then simply return a 200
    # This happens when the UI is deleting a rule that doesn't exist yet (i.e. in the policy create page)
    if rule_id == 0:
        return HttpResponse('', status=200)

    return render(request, 'policy/delete_rule.html', {})


@login_required
def archive(request, policy_id):
    """Archive a policy."""
    policy = get_object_or_404(Policy, id=policy_id, user=request.user)
    policy.archived = True
    policy.save()

    # Add an info message
    messages.info(request, 'Policy has been archived.')

    return redirect('policy_dashboard')
