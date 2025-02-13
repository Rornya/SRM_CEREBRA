from django.shortcuts import render, get_object_or_404
from .models import Department

def department_list(request):
    departments = Department.objects.all()
    return render(request, 'departments/department_list.html', {'departments': departments})

def department_detail(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    return render(request, 'departments/department_detail.html', {'department': department})
