from django.db import models 
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    CATEGORY_CHOICES = [

        ('Study', 'Study'),

        ('Health', 'Health'),

        ('Shopping', 'Shopping'),

        ('Professional', 'Professional'),

        ('Personal', 'Personal'),

        ('Finance', 'Finance'),

        ('Household', 'Household'),

    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)

    description = models.TextField(
        blank=True,
        null=True
    )
    category = models.CharField(

        max_length=20,

        choices=CATEGORY_CHOICES,

        blank=True,

        null=True

    )

    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    due_date = models.DateField(
        null=True,
        blank=True
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    is_quick_task = models.BooleanField(
        default=False
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
    
class TaskStep(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    step_text = models.TextField()
    order = models.IntegerField(default=0)

class FocusSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    duration = models.IntegerField(default=25)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Focus Session {self.id}"

class TimerSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    focus_duration = models.IntegerField(default=25)
    break_duration = models.IntegerField(default=5)
    total_cycles = models.IntegerField(default=4)
    sound_enabled = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.user.username}'s Timer Settings"

class DailyActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    had_activity = models.BooleanField(default=False)

    streak_popup_shown = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "date")