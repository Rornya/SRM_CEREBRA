from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DiaryEntry
from .forms import DiaryEntryForm

@login_required
def diary_list(request):
    entries = DiaryEntry.objects.filter(user=request.user).order_by('-entry_date')
    return render(request, 'diary/diary_list.html', {'entries': entries})

@login_required
def diary_entry_create(request):
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST)
        if form.is_valid():
            diary_entry = form.save(commit=False)
            diary_entry.user = request.user
            diary_entry.save()
            return redirect('diary_list')
    else:
        form = DiaryEntryForm()
    return render(request, 'diary/diary_entry_form.html', {'form': form})

@login_required
def diary_entry_detail(request, entry_id):
    entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)
    return render(request, 'diary/diary_entry_detail.html', {'entry': entry})

@login_required
def mark_completed(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    entry.is_completed = True
    entry.save()
    return redirect('diary_list')

@login_required
def delete_entry(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    entry.delete()
    return redirect('diary_list')
