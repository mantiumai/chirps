"""Views for the policy app."""  
from django.contrib.auth.decorators import login_required  
from django.http import HttpResponse  
from django.shortcuts import get_object_or_404, redirect, render  
from django.views.decorators.http import require_http_methods  
  
from .forms import PolicyForm  
from .models import Policy, PlanVersion, Rule  
  
# Update all instances of 'plan' to 'policy' in view function names and docstrings  
  
@login_required  
def dashboard(request):  
    templates = Policy.objects.filter(is_template=True).order_by('id')  
    user_policies = Policy.objects.filter(user=request.user, archived=False).order_by('id')  
    return render(request, 'policy/dashboard.html', {'user_policies': user_policies, 'templates': templates})  
  
  
@login_required  
def create(request):  
    if request.method == 'POST':  
        form = PolicyForm(request.POST)  
        form.full_clean()  
  
        policy = Policy.objects.create(  
            name=form.cleaned_data['name'], description=form.cleaned_data['description'], user=request.user  
        )  
  
        plan_version = PlanVersion.objects.create(number=1, policy=policy)  
        policy.current_version = plan_version  
        policy.save()  
  
        for rule in form.cleaned_data['rules']:  
            Rule.objects.create(  
                name=rule['rule_name'],  
                query_string=rule['rule_query_string'],  
                regex_test=rule['rule_regex'],  
                severity=rule['rule_severity'],  
                policy=plan_version,  
            )  
  
    return render(request, 'policy/create.html', {})  
  
  
@login_required  
def clone(request, policy_id):  
    policy = get_object_or_404(Policy, id=policy_id, is_template=True)  
  
    cloned_policy = Policy.objects.create(  
        name=policy.name,  
        description=policy.description,  
        user=request.user,  
    )  
  
    plan_version = PlanVersion.objects.create(number=1, policy=cloned_policy)  
    cloned_policy.current_version = plan_version  
    cloned_policy.save()  
  
    for rule in policy.current_version.rules.all():  
        Rule.objects.create(  
            name=rule.name,  
            description=rule.description,  
            query_string=rule.query_string,  
            regex_test=rule.regex_test,  
            severity=rule.severity,  
            policy=plan_version,  
        )  
  
    return redirect('policy_edit', policy_id=cloned_policy.id)  
  
  
@login_required  
def edit(request, policy_id):  
    policy = get_object_or_404(Policy, id=policy_id, user=request.user)  
    if request.method == 'POST':  
        form = PolicyForm(request.POST)  
        form.full_clean()  
        policy.save()  
  
        new_policy_version = PlanVersion.objects.create(number=policy.current_version.number + 1, policy=policy)  
  
        for rule in form.cleaned_data['rules']:  
            Rule.objects.create(  
                name=rule['rule_name'],  
                query_string=rule['rule_query_string'],  
                regex_test=rule['rule_regex'],  
                severity=rule['rule_severity'],  
                policy=new_policy_version,  
            )  
  
        policy.current_version = new_policy_version  
        policy.name = form.cleaned_data['name']  
        policy.description = form.cleaned_data['description']  
        policy.save()  
    else:  
        form = PolicyForm.from_policy(policy=policy)  
  
    return render(request, 'policy/edit.html', {'policy': policy, 'form': form})  
  
  
@login_required  
def create_rule(request):  
    return render(  
        request,  
        'policy/create_rule.html',  
        {'rule_id': request.GET.get('rule_id', 0), 'next_rule_id': int(request.GET.get('rule_id', 0)) + 1},  
    )  
  
  
@login_required  
@require_http_methods(['DELETE'])  
def delete_rule(request, rule_id):  
    if rule_id == 0:
        return HttpResponse('', status=200)

    return render(request, 'policy/delete_rule.html', {})


@login_required
@require_http_methods(['DELETE'])
def archive(request, policy_id):
    """Archive a policy."""
    policy = get_object_or_404(Policy, id=policy_id, user=request.user)
    policy.archived = True
    policy.save()
    return HttpResponse('', status=200)
