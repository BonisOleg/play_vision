from django.shortcuts import render

def mentoring_page(request):
    """
    Сторінка Ментор-коучингу
    """
    # Експерти завантажуються через context processor як cms_experts_mentoring
    context = {}
    return render(request, 'pages/mentoring.html', context)
