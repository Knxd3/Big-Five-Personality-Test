from django.shortcuts import render

# Create your views here.

def questionnaire(request):
    ans = request.POST
    print(ans)
    context = {
        'n': range(1,21),
        'm': range(1,6),
        'answs': ans
    }
    return render(request, "testbigfive/index.html", context)