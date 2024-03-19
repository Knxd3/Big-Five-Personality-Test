from django.shortcuts import render
import pandas as pd
import numpy as np
from .forms import survey
from .models import userScore

# Create your views here.

def questionnaire(request):
    ans = request.POST
    # print(request.POST)
    # print(request.user)
    #### check form is valid 
    form = survey(request.POST)
    #### move logic here for prod
    if form.is_valid():
            # print('ok')

            qry_dict = ans.dict()
            new_dict = dict()
            for i in qry_dict.keys():
                if i != 'csrfmiddlewaretoken':
                    new_dict[i] = list(qry_dict[i])
            raw_ = pd.DataFrame.from_dict(new_dict, orient='index')
            raw_ = raw_.reset_index()
            raw_['index_id'] = raw_['index'].str.extract(r'(\d{1,3})\D*$')
            raw_.columns = ['index', 'value', 'index_id']
            raw_['index_id'] = raw_['index_id'].astype('int')
            raw_['value'] = raw_['value'].astype('int')
            raw_['facet'] = np.where(raw_['index_id'] <= 4, 'c', 
                                   np.where(raw_['index_id'] <= 8, 'o',
                                            np.where(raw_['index_id'] <= 12, 'a',
                                                     np.where(raw_['index_id'] <= 16, 'e', 'n'))))

            scores_agg = raw_.groupby(['facet']).agg({'value' : 'sum'})
            scores_f = scores_agg.transpose()
            scores_f1 = pd.DataFrame({'c':[None], 'o':[None], 'a':[None], 'e':[None], 'n':[None], 'user':[request.user]})
            # print(scores_f)
            # # print(scores_f['a'].values[0])
            def check(p, scr):
                if p in scores_f.columns:
                    return scores_f[p].values[0]

            scores_f1['a'] = check('a', scores_f) 
            scores_f1['c'] = check('c', scores_f) 
            scores_f1['o'] = check('o', scores_f) 
            scores_f1['n'] = check('n', scores_f) 
            scores_f1['e'] = check('e', scores_f) 

            # print(scores_f1)

            user_entry = userScore(c = scores_f1['c'].values[0],
                                   a = scores_f1['a'].values[0],
                                   n = scores_f1['n'].values[0],
                                   e = scores_f1['e'].values[0],
                                   o = scores_f1['o'].values[0])
            user_entry.save()

            print(user_entry.id)
    else:
        print('form not ok')

    db_qs = userScore.objects.all().values()
    db_qs_df = pd.DataFrame.from_records(db_qs)
    print(db_qs_df)

    context = {
        'n': range(1,21),
        'm': range(1,6),
        'answs': ans
    }
    return render(request, "testbigfive/index.html", context)