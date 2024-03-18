from django.shortcuts import render
import pandas as pd
import json

# Create your views here.

def questionnaire(request):
    ans = request.POST
    # print(request.body)
    qry_dict = ans.dict()
    new_dict = dict()
    for i in qry_dict.keys():
        if i != 'csrfmiddlewaretoken':
            new_dict[i] = list(qry_dict[i])
    df = pd.DataFrame.from_dict(new_dict, orient='index')
    df = df.reset_index()
    df['index_id'] = df['index'].str.extract(r'(\d{1,3})\D*$')
    print(df)
    context = {
        'n': range(1,21),
        'm': range(1,6),
        'answs': ans
    }
    return render(request, "testbigfive/index.html", context)