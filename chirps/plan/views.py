"""Views for the plan app."""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import PlanForm
from .models import Plan, PlanVersion, Rule


@login_required
def dashboard(request):
    """Render the dashboard for the plan app.

    Args:
        request (HttpRequest): Django request object
    """
    # Fetch a list of all the available template and custom user plans
    templates = Plan.objects.filter(is_template=True).order_by('id')
    user_plans = Plan.objects.filter(user=request.user, archived=False).order_by('id')
    return render(request, 'plan/dashboard.html', {'user_plans': user_plans, 'templates': templates})


@login_required
def create(request):
    """Render the create plan form.

    Args:
        request (HttpRequest): Django request object
    """
    if request.method == 'POST':
        form = PlanForm(request.POST)
        form.full_clean()

        # Create the plan
        plan = Plan.objects.create(
            name=form.cleaned_data['name'], description=form.cleaned_data['description'], user=request.user
        )

        # Create the initial plan version
        plan_version = PlanVersion.objects.create(number=1, plan=plan)

        # Save off the back reference of the current plan version to the plan.
        plan.current_version = plan_version
        plan.save()

        # Create the rules
        for rule in form.cleaned_data['rules']:
            Rule.objects.create(
                name=rule['rule_name'],
                query_string=rule['rule_query_string'],
                regex_test=rule['rule_regex'],
                severity=rule['rule_severity'],
                plan=plan_version,
            )

    return render(request, 'plan/create.html', {})


@login_required
def clone(request, plan_id):
    """Clone a template plan to a custom user plan

    Args:
        request (HttpRequest): Django request object
        plan_id (int): ID of the template plan to clone
    """
    plan = get_object_or_404(Plan, id=plan_id, is_template=True)

    cloned_plan = Plan.objects.create(
        name=plan.name,
        description=plan.description,
        user=request.user,
    )

    # Create the initial plan version
    plan_version = PlanVersion.objects.create(number=1, plan=cloned_plan)

    # Pin the initial version as the current version
    cloned_plan.current_version = plan_version
    cloned_plan.save()

    # Clone the rules
    for rule in plan.current_version.rules.all():
        Rule.objects.create(
            name=rule.name,
            description=rule.description,
            query_string=rule.query_string,
            regex_test=rule.regex_test,
            severity=rule.severity,
            plan=plan_version,
        )

    # Redirect to the edit page for the new plan
    return redirect('plan_edit', plan_id=cloned_plan.id)


@login_required
def edit(request, plan_id):
    """Render the edit plan form.

    Args:
        request (HttpRequest): Django request object
        plan_id (int): ID of the plan to edit
    """
    plan = get_object_or_404(Plan, id=plan_id, user=request.user)
    if request.method == 'POST':
        form = PlanForm(request.POST)
        form.full_clean()
        plan.save()

        # Create a new plan version
        new_plan_version = PlanVersion.objects.create(number=plan.current_version.number + 1, plan=plan)

        # Persist all of the rules against the new version
        for rule in form.cleaned_data['rules']:
            Rule.objects.create(
                name=rule['rule_name'],
                query_string=rule['rule_query_string'],
                regex_test=rule['rule_regex'],
                severity=rule['rule_severity'],
                plan=new_plan_version,
            )

        # Update the current version of the plan as well as the name and description
        plan.current_version = new_plan_version
        plan.name = form.cleaned_data['name']
        plan.description = form.cleaned_data['description']
        plan.save()
    else:

        form = PlanForm.from_plan(plan=plan)

    return render(request, 'plan/edit.html', {'plan': plan, 'form': form})


@login_required
def create_rule(request):
    """Render a single row of a Rule for the create plan page."""
    return render(
        request,
        'plan/create_rule.html',
        {'rule_id': request.GET.get('rule_id', 0), 'next_rule_id': int(request.GET.get('rule_id', 0)) + 1},
    )


@login_required
@require_http_methods(['DELETE'])
def delete_rule(request, rule_id):
    """Delete a single rule within a plan."""
    # If the rule_id is 0, then simply return a 200
    # This happens when the UI is deleting a rule that doesn't exist yet (i.e. in the plan create page)
    if rule_id == 0:
        return HttpResponse('', status=200)

    return render(request, 'plan/delete_rule.html', {})


@login_required
@require_http_methods(['DELETE'])
def archive(request, plan_id):
    """Archive a plan."""
    plan = get_object_or_404(Plan, id=plan_id, user=request.user)
    plan.archived = True
    plan.save()
    return HttpResponse('', status=200)
