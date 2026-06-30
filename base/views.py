from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Task, FocusSession, TimerSetting, DailyActivity
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum 
from .predictor import predict_category
from base.task_breakdown import generate_breakdown
from base.models import TaskStep
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import calendar
from datetime import date
# =========================
# HELPER: TASK STATS
# =========================
@login_required
def get_task_stats(request):
    today = timezone.now().date()
    streak = calculate_streak(request.user)
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user,completed=True).count()
    pending_tasks = Task.objects.filter(user=request.user,completed=False).count()
    today_focus = FocusSession.objects.filter(
            user=request.user,
            created__date=today
        ).aggregate(
            total=Sum('duration')
        )['total'] or 0
        # Brain Dump stats
    brain_dump_total = Task.objects.filter(
        user=request.user,
        is_quick_task=True
    ).count()
    brain_dump_completed = Task.objects.filter(
        user=request.user,
        is_quick_task=True,
        completed=True
    ).count()
    main_task_total = Task.objects.filter(
        user=request.user,
        is_quick_task=False
    ).count()
    main_task_completed = Task.objects.filter(
        user=request.user,
        is_quick_task=False,
        completed=True
    ).count()
    brain_dump_progress = 0
    if brain_dump_total > 0:
        brain_dump_progress = (
            brain_dump_completed / brain_dump_total
        ) * 100

    main_task_progress = 0
    if main_task_total > 0:
        main_task_progress = (
            main_task_completed / main_task_total
        ) * 100
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'today_focus': today_focus,
        'streak': streak,
        'brain_dump_total': brain_dump_total,
        'brain_dump_completed': brain_dump_completed,
        'main_task_total': main_task_total,
        'main_task_completed': main_task_completed,
        'brain_dump_progress': brain_dump_progress,
        'main_task_progress': main_task_progress,
    }
# =========================
# DASHBOARD
# =========================

@login_required
def dashboard(request):

    if request.method == "POST":

        title = request.POST.get('title')
        due_date = request.POST.get('due_date')
    
        if due_date == '':
            due_date = None
        
        quick_task_count = Task.objects.filter(
            user=request.user,
            is_quick_task=True,
            completed=False
        ).count()

        if quick_task_count >= 5:
            return JsonResponse({
                "success": False,
                "message": "Maximum 5 Brain Dump tasks allowed."
            })
    
        if title:
            task = Task.objects.create(
            user=request.user,
            title=title,
            due_date=due_date,
            priority="Medium",
            is_quick_task=True
            )
        
            stats = get_task_stats(request)
            return JsonResponse({
                "success": True,
                "task_id": task.id,
                "title": task.title,
                "priority": task.priority,
                "due_date": str(task.due_date) if task.due_date else "No Date",
                "edit_url": reverse("edit_task", args=[task.id]),
                "is_quick_task": task.is_quick_task,

                **stats
            })

    filter_type = request.GET.get('filter')
    
    if filter_type == 'completed':
        tasks = Task.objects.filter(
            user=request.user,
            completed=True,
            is_quick_task=True
        )
    
    elif filter_type == 'pending':
        tasks = Task.objects.filter(
            user=request.user,
            completed=False,
            is_quick_task=True
        )
    
    else:
        tasks = Task.objects.filter(
            user=request.user,
            is_quick_task=True
        )

    context = {
        "tasks": tasks,
        "filter_type": filter_type,
        **get_task_stats(request)
    }

    return render(request, 'dashboard.html', context)

@login_required
def dashboard_filter(request):
    filter_type = request.GET.get("filter", "all")
    tasks = Task.objects.filter(
        user=request.user,
        is_quick_task=True
    )
    if filter_type == "pending":
        tasks = tasks.filter(completed=False)
    elif filter_type == "completed":
        tasks = tasks.filter(completed=True)
    html = render_to_string(
        "partials/task_list.html",
        {
            "tasks": tasks
        },
        request=request
    )
    return JsonResponse({
        "html": html
    })
# =========================
# TASKS PAGE
# =========================
@login_required
def tasks(request):

    if request.method == "POST":

        title = request.POST.get('title')
        desc = request.POST.get('desc')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date')

        if due_date == '':
            due_date = None

        if title:
            category = predict_category(title)
            steps = generate_breakdown(title, category)
            task = Task.objects.create(
                user=request.user,
                title=title,
                description = desc,
                priority=priority,
                due_date=due_date,
                is_quick_task=False,
                category=category,
            )
            for step in steps:

                TaskStep.objects.create(

                    task=task,

                    step_text=step)
            print("Generated steps:", steps)
            return JsonResponse({
                "success": True,
                "task_id": task.id,
                "title": task.title,
                "priority": task.priority,
                "category": task.category,
                "due_date": str(task.due_date) if task.due_date else "No Date",
                "edit_url": reverse("edit_task", args=[task.id]),
                "steps": steps,
                "is_high": task.priority == "High"

            })
    filter_type = request.GET.get('filter')

    if filter_type == 'completed':
        tasks_list = Task.objects.filter(user=request.user,completed=True,is_quick_task=False)
    elif filter_type == 'pending':
        tasks_list = Task.objects.filter(user=request.user,completed=False,is_quick_task=False)
    else:
        tasks_list = Task.objects.filter(user=request.user,is_quick_task=False)

    context = {
        "tasks": tasks_list,
        "filter_type": filter_type,
        **get_task_stats(request)
    }

    return render(request, 'tasks.html', context)


# =========================
# EDIT TASK
# =========================
@login_required
def edit_task(request, task_id):

    task = get_object_or_404(Task, id=task_id,user=request.user)

    if request.method == "POST":

        task.title = request.POST.get("title")
        task.priority = request.POST.get("priority")

        due_date = request.POST.get("due_date")
        if not task.is_quick_task:

            task.description = request.POST.get("desc")

        due_date = request.POST.get("due_date")

        # ✅ CLEAN FIX
        if due_date == "" or due_date is None:
            task.due_date = None
        else:
            task.due_date = due_date

        task.save()


        # Redirect based on task type

        if task.is_quick_task:

            return redirect('dashboard')

        return redirect('tasks')

    return render(request, "edit_task.html", {"task": task})


# =========================
# DELETE TASK
# =========================
@login_required
def delete_task(request, task_id):

    if request.method == "POST":

        task = get_object_or_404(

            Task,

            id=task_id,

            user=request.user

        )
        was_completed = task.completed
        task.delete()
        stats = get_task_stats(request)

        return JsonResponse({

            "success": True,
            "completed": was_completed,
            **stats

        })

    return JsonResponse({

        "success": False

    }, status=400)


# =========================
# COMPLETE TASK
# =========================
@login_required
def complete_task(request, task_id):
    if request.method == "POST":

        task = get_object_or_404(
            Task,
            id=task_id,
            user=request.user
        )

        task.completed = not task.completed
        if task.completed:
            task.completed_at = timezone.now()
        else:
            task.completed_at = None
        task.save()
        today = timezone.now().date()

        activity, created = DailyActivity.objects.get_or_create(
            user=request.user,
            date=today
        )
        activity.had_activity = True
        activity.save()
        show_popup = False

        if task.completed and not activity.streak_popup_shown:
        
            activity.streak_popup_shown = True
            activity.save()

            show_popup = True
        stats = get_task_stats(request)
        streak = calculate_streak(request.user)
        return JsonResponse({
            "success": True,
            "completed": task.completed,
            "show_popup": show_popup,
            "streak": streak,
            **stats
        })

    return JsonResponse({
        "success": False
    }, status=400)


# =========================
# FOCUS TIMER
# =========================
@login_required
def focus_timer(request):

    settings, created = TimerSetting.objects.get_or_create(

    user=request.user,

    defaults={

        "focus_duration": 25,

        "break_duration": 5,

        "total_cycles": 4,

        "sound_enabled": True,

    }
)
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    today_sessions = FocusSession.objects.filter(user=request.user,created__date=today)
    week_sessions = FocusSession.objects.filter(user=request.user,created__date__gte=week_ago)

    today_minutes = sum(s.duration for s in today_sessions)
    week_minutes = sum(s.duration for s in week_sessions)

    return render(request, 'focus_timer.html', {
        "settings": settings,
        "today_focus": today_minutes or 0,
        "today_sessions": today_sessions.count(),
        "week_hours": week_minutes // 60,
        "week_minutes": week_minutes % 60,
        "week_sessions": week_sessions.count(),
    })


# =========================
# SAVE FOCUS SESSION
# =========================
@login_required
def save_focus_session(request):
    print("SAVE FOCUS SESSION CALLED")

    if request.method == "POST":
        
        settings = TimerSetting.objects.filter(user=request.user).first()

        FocusSession.objects.create(

            user=request.user,

            duration=settings.focus_duration

        )
        today = timezone.localdate()

        activity, created = DailyActivity.objects.get_or_create(
            user=request.user,
            date=today
        )

        activity.had_activity = True
        activity.save()
        stats = get_task_stats(request)
        return JsonResponse({
            "status": "success",
            **stats
            })

    return JsonResponse({"status": "failed"})


# =========================
# SETTINGS
# =========================
@login_required
def settings_view(request):

    settings, created = TimerSetting.objects.get_or_create(
        user=request.user,
        defaults={

            "focus_duration": 25,

            "break_duration": 5,

            "total_cycles": 4,

            "sound_enabled": True

        }

    )

    if request.method == "POST":
        settings.focus_duration = int(request.POST.get("focus_duration"))
        settings.break_duration = int(request.POST.get("break_duration"))
        settings.total_cycles = int(request.POST.get("total_cycles"))
        settings.sound_enabled = 'sound_enabled' in request.POST
        settings.save()
        return redirect("focus_timer")
    return render(request, "settings.html", {"settings": settings})


# =========================
# STATS
# =========================
@login_required
def stats(request):
    now = timezone.now()
    today = now.date()
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    total_tasks = Task.objects.filter(
        user=request.user
    ).count()

    completed_tasks = Task.objects.filter(
        user=request.user,
        completed=True
    ).count()

    pending_tasks = Task.objects.filter(
        user=request.user,
        completed=False
    ).count()

    brain_dump_tasks = Task.objects.filter(
    user=request.user,
    is_quick_task=True
    ).count()

    planned_tasks = Task.objects.filter(
        user=request.user,
        is_quick_task=False
    ).count()
    today_sessions = FocusSession.objects.filter(
        user=request.user,
        created__date=today
    )
    week_sessions = FocusSession.objects.filter(
        user=request.user,
        created__gte=week_start
    )

    month_sessions = FocusSession.objects.filter(
        user=request.user,
        created__gte=month_start
    )

    total_sessions = FocusSession.objects.filter(
        user=request.user
    )

    # duration calculations

    today_focus = sum(s.duration for s in today_sessions)

    week_focus = sum(s.duration for s in week_sessions)

    month_focus = sum(s.duration for s in month_sessions)

    today = timezone.localdate()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))
    return render(request, "stats.html", {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "brain_dump_tasks":brain_dump_tasks,
        "planned_tasks":planned_tasks,
        # focus stats

        "today_sessions": today_sessions.count(),
        "week_sessions": week_sessions.count(),
        "month_sessions": month_sessions.count(),
        "today_focus": today_focus,
        "week_focus": week_focus,
        "month_focus": month_focus,
        "total_focus_sessions": total_sessions.count(),
        **stats_streak_card(request.user, year, month),
    })
def about(request):

    return render(request, 'about.html')

@login_required
def summary(request):

    total_sessions = FocusSession.objects.filter(

        user=request.user

    )

    total_focus_minutes = sum(

        session.duration

        for session in total_sessions

    )

    completed_tasks = Task.objects.filter(

        user=request.user,

        completed=True

    ).count()

    pending_tasks = Task.objects.filter(

        user=request.user,

        completed=False

    ).count()

    context = {

        "total_sessions": total_sessions.count(),

        "total_focus_time":

            f"{total_focus_minutes // 60}h {total_focus_minutes % 60}m",

        "completed_tasks": completed_tasks,

        "pending_tasks": pending_tasks,

    }

    return render(request,"summary.html",context)

# STREAK:-->
def calculate_streak(user):
    streak = 0
    today = timezone.localdate()

    if DailyActivity.objects.filter(
        user=user,
        date=today,
        had_activity=True
    ).exists():
        current_day = today

    elif DailyActivity.objects.filter(
        user=user,
        date=today - timedelta(days=1),
        had_activity=True
    ).exists():
        current_day = today - timedelta(days=1)

    else:
        return 0

    while DailyActivity.objects.filter(
        user=user,
        date=current_day,
        had_activity=True
    ).exists():

        streak += 1
        current_day -= timedelta(days=1)

    return streak

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(
            request.user,
            request.POST
        )
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(
                request,
                user
            )
            messages.success(
                request,
                "Password changed successfully."
            )
            return redirect("change_password.html",)
    else:
        form = PasswordChangeForm(
            request.user
        )
    return render(
        request,
        "change_password.html",
        {"form": form}
    )

def stats_streak_card(user, year, month):
    today = timezone.localdate()

    days_in_month = calendar.monthrange(year, month)[1]

    month_days = []

    for day in range(1, days_in_month + 1):

        current_date = date(year, month, day)

        completed = DailyActivity.objects.filter(
            user=user,
            date=current_date,
            had_activity=True
        ).exists()

        month_days.append({
            "date": current_date,
            "completed": completed,
            "is_today": current_date == today,
        })

    return {
        "month_days": month_days,
        "current_month": date(year, month, 1).strftime("%B %Y"),
        "streak": calculate_streak(user),
    }