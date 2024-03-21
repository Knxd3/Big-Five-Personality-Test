from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
from .forms import survey
from .models import userScore



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

            # adjust sign #
            # raw_ = 
            raw_['value'] = raw_['value'].values * np.array([1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1])
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
    
    if request.method == 'POST':
         return redirect('results')

    context = {
        'n': range(1,21),
        'm': range(1,6),
        'answs': ans,
        'q_set': {'1' : 'Sunt atent(ă) la detalii',
                  '2' : 'Îmi place ordinea',
                  '3' : 'Încurc treburile',
                  '4' : 'Uit să pun lucrurile la locul lor',
                  '5' : 'Am un vocabular bogat',
                  '6' : 'Am idei excelente',
                  '7' : 'Nu mă interesează ideile abstracte',
                  '8' : 'Discuțiile filozofice mă plictisesc',
                  '9' : 'Am un suflet bun',
                  '10' : 'Respect autoritatea',
                  '11' : 'Sunt o persoană greu de cunoscut',
                  '12' : 'Nu mă interesează problemele altora',
                  '13' : 'Sunt sufletul petrecerii',
                  '14' : 'Inițiez conversații',
                  '15' : 'Nu vorbesc mult',
                  '16' : 'Nu-mi place să atrag atenția asupra mea',
                  '17' : 'Nu sunt stresat',
                  '18' : 'Rareori mă simt deprimat(ă)',
                  '19' : 'Mă ingrijorez mult',
                  '20' : 'Oscilez de la o stare emoțională la alta'}
    }
    return render(request, "testbigfive/index.html", context)




#### RESULTS PAGE ####
def results(request):
    db_qs = userScore.objects.all().values()
    db_qs_df = pd.DataFrame.from_records(db_qs)
    print(db_qs_df)

    latest_db_q = db_qs_df.loc[db_qs_df['id'] == max(db_qs_df['id'].values), :]
    print(latest_db_q)

    # print(np.percentile([1,2,3,4,5,6,7,8,9], [50]))

    # vals = np.array([1,2,3,4,5,6,7,8,9])
    # p_bigger = np.sum(4 > vals)
    # k_list = len(vals)
    # print(p_bigger/k_list)
    

    ###### add percentile calculator #####

    def ptile_calc(all, latest):
         return np.sum(latest > all) / len(all)

    ptiles = {
         'Conștiinciozitate': ptile_calc(db_qs_df['c'].values, latest_db_q['c'].values[0]),
         'Agreeabilitate': ptile_calc(db_qs_df['a'].values, latest_db_q['a'].values[0]),
         'Extraversie': ptile_calc(db_qs_df['e'].values, latest_db_q['e'].values[0]),
         'Stabilitate Emoțională': ptile_calc(db_qs_df['n'].values, latest_db_q['n'].values[0]),
         'Deschidere Către Experiențe': ptile_calc(db_qs_df['o'].values, latest_db_q['o'].values[0])
    }

    print(ptiles)
    
    context = {
        #  'c':ptiles['c'] * 100,
        #  'a':ptiles['a'] * 100,
        #  'e':ptiles['e'] * 100,
        #  'n':ptiles['n'] * 100,
        #  'o':ptiles['o'] * 100,
         'ptiles': {k: v * 100 for k, v in ptiles.items()}
     }
    
    print({k: v * 100 for k, v in ptiles.items()})
    # print(ptiles['c'] * 100)
    
    return render(request, 'testbigfive/results.html', context)