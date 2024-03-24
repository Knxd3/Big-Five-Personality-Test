from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
import numpy as np
from .forms import survey
from .models import userScore
from django.views.decorators.cache import never_cache

@never_cache
def questionnaire(request):
    # ans = request.POST
    # print(request.POST)
    # print(request.user)
    #### check form is valid 

    context = {
        'n': range(1,21),
        'm': range(1,6),
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

    #### move logic here for prod
    if request.method == 'POST':
        form = survey(request.POST)
        print(form.errors)
        print('post')
        if form.is_valid():
            print('valid')

            qry_dict = request.POST.dict()
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
            
            scores_f1['c'] = check('c', scores_f) 
            scores_f1['a'] = check('a', scores_f)
            scores_f1['e'] = check('e', scores_f) 
            scores_f1['n'] = check('n', scores_f)
            scores_f1['o'] = check('o', scores_f) 
             
             

            # print(scores_f1)

            user_entry = userScore(c = scores_f1['c'].values[0],
                                   a = scores_f1['a'].values[0],
                                   e = scores_f1['e'].values[0],
                                   n = scores_f1['n'].values[0],
                                   o = scores_f1['o'].values[0])
            user_entry.save()

            print(user_entry.id)
            return redirect('results')

            # print('errors')
            # context['form'] = form
            # return render(request, 'testbigfive/index.html', context)
        else:
            # form = survey()
            # context['err'] = 1
            # print(form.errors)
            print('invalid form')
            # alert('Please fill out all the questions.')
            # return render(request, context)
            context['err'] = 0
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

    # ptiles = {
    #      'Conștiinciozitate': ptile_calc(db_qs_df['c'].values, latest_db_q['c'].values[0]),
    #      'Agreeabilitate': ptile_calc(db_qs_df['a'].values, latest_db_q['a'].values[0]),
    #      'Extraversie': ptile_calc(db_qs_df['e'].values, latest_db_q['e'].values[0]),
    #      'Stabilitate Emoțională': ptile_calc(db_qs_df['n'].values, latest_db_q['n'].values[0]),
    #      'Deschidere Către Experiențe': ptile_calc(db_qs_df['o'].values, latest_db_q['o'].values[0])
    # }

    ptiles = {
         'Conștiinciozitate': 
             [
            'conștiincioasă',     
            ptile_calc(db_qs_df['c'].values, latest_db_q['c'].values[0]),
             [f"""Conștiinciozitatea este dimensiunea care măsoară trăsăturile ce țin de productivitate, strictețe, aderența la reguli și de tendința de a planifica. Persoanele conștiincioase își elaborează traiectorii pe care le urmează, punând în practică pașii către obiectiv. Ele tind să compartimentalizeze chestiunile după categorii fixe și să păstreze ordinea și curățenia; acestea din urmă atât concret, cu privire la spațiul personal, cât și abstract, cu privire la judecățile despre situații sau despre ceilalți. De asemenea, tind să nu procrastineze, mai ales dacă sunt și stabile (în terminologia Big Five). Persoanele conștiincioase pot părea încăpățânate și inflexibile, abătându-se cu greu de la setul de reguli pe care au acceptat să îl urmeze.""",
                               f"""Spre deosebire, persoanele de celalată parte a spectrului au o abordare flexibilă asupra vieții și tind să nu pună mare preț pe simțul responsabilității, pe abordări procedurale (de rutină) sau pe ordine. Au o atitudine relaxată și pot fi rar caracterizați de trăsături precum o voință puternică sau o atitudine disciplinată. Din această cauză, pot des manifestă comportamente delăsătoare sau inconsecvente; dacă sunt caracterizați de un grad înalt de deschidere către experiențe, pot începe numeroase proiecte fără să le și finalizeze. Avantajele acestei abordări se ivesc în ipostaze în care planificarea de termen lung nu se justifică: în contextul unităților monetare instabile, situațiilor de război, în preajma guvernelor cu comportament imprevizibil sau altele de acest fel.""",
                               f"""Persoanele conștiincioase tind să predomine în domenii manageriale sau administrative, unde respectarea procedurilor, organizarea resurselor și cerințele exigente pe productivitate sunt de prim ordin. Persoanele neconștiincioase beneficiază profesional de pe urmă spontaneității lor în domenii precum stand-up-ul sau actoria, mai ales dacă sunt caracterizați și de un grad ridicat de deschidere către experiențe. Nefiind preocupați în așa mare măsură cu obiectivele profesionale, ei tind să nu cadă pradă burn-out-ului și să se bucure mai mult de plăcerile vieții."""],   
             ],
         'Agreeabilitate': 
             [
            'agreeabilă',
             ptile_calc(db_qs_df['a'].values, latest_db_q['a'].values[0]),
                            [f"""Agreabilitatea este dimensiunea Big Five care surprinde trăsăturile de cordialitate, cooperare și amiabilitate. Persoanele agreabile sunt calde, primitoare și ușor de abordat, iar atitudinea lor deschisă îi face să fie o companie de dorit oriunde s-ar afla. Ei văd mereu ce este mai bun în ceilalți și se raportează acelei părți din om atunci când interacționează cu alții. De asemenea, valorifică extrem de mult toleranța și înțelegerea reciprocă. Doresc să ajungă la cooperare și să evite conflictul cu orice preț. Datorită dorinței puternice de a menține relații amiabile cu toate persoanele pe care le cunosc, persoanele agreabile pot concesiona foarte mult din ceea ce își doresc, fapt ce duce des la resentimente. Acest fapt poate da naștere comportamentelor pasiv-agresive. Mai apoi, în anumite cazuri, evitarea abordării directe pentru rezolvarea problemelor poate duce la agregarea lor în situații mult mai greu de depășit decât ar fi fost cazul dacă s-ar fi rezolvat prompt încă din faza incipientă.""",
                            f"""Spre deosebire, persoanele dizagreabile nu sunt deloc calde, concesionare sau ușor de abordat. Persoanele dizagreabile tind să vrea să facă doar ceea ce decid ele însele, fără a compromite vreun aspect de dragul altor oameni. În multe cazuri nu sunt cooperante și preferă mai degrabă conflictul, unde disputele se rezolvă cu un învingător și un pierzător clar hotărâți. De asemenea, persoanele cu această trăsătură tind să negocieze în favoarea propriei persoane, chiar și în detrimentul celorlalte părți implicate. Din acest motiv, pot părea egoiști. În cazuri extreme, dezagreabilitatea poate evolua în comportament antisocial sau prădător. Considerând și faptul că persoanele dezagreabile detestă autoritatea, ei pot ajunge să aibă probleme pronunțate cu legea sau formele de autoritate din instituții."""],
         ],

         'Extraversie': [
             'extravertă',
             ptile_calc(db_qs_df['e'].values, latest_db_q['e'].values[0]),
                         [f"""Extraversia este dimensiunea care măsoară excitabilitatea la stimuli și propensiunea către activități care implică un număr mare de oameni. Persoanele extraverte prosperă de pe urmă socializării și tind să fie vivace și agere în a observa și reacționa rapid la toate situațiile cu care se confruntă. Urmăresc să implice alți oameni în activitățile pe care le întreprind și se alătură instictiv altora atunci când oportunitatea se ivește. Persoanele caracterizate puternic de această dimensiune a personalității sunt asertive și caută să fie în centrul atenției, fie pentru a conduce, fie pentru se distra împreună cu ceilalți. În cazuri extreme, pot să fie prea tentați de nevoia de a se alătura altora pentru a putea să-și urmeze în mod eficace scopurile. Aceasta este cu atât mai adevărată cu cât nivelul lor de conștiinciozitate este mai scăzut.""",
                         f"""Pe de cealaltă parte, persoanele introverte sunt mult mai puțin excitabile la stimuli și se simt copleșite de agitație, zgomot sau contexte sociale ample. Persoanele introverte nu implică alți oameni în activitățile pe care le întreprind, preferând concentrarea permisă de solitudine. Atunci când interacționează cu alți oameni, preferă să o facă alături de prieteni sau cunoscuți. De asemenea, tind să conceapă răspunsuri la întrebări mai încet, punând mai mare preț pe calitatea informației oferite decât pe rapiditatea oferirii informației; consideră acest acest al doilea tip de răspuns ca fiind impropriu și expedient. Introverților le este mai greu să inițieze conversații sau să își facă vocea auzită, fapt pentru care pot rămâne într-un rol secundar chiar și atunci când calificările le-ar permite să se afirme."""],
         ],
         
         'Stabilitate Emoțională': [
             'stabilă emoțional',
             ptile_calc(db_qs_df['n'].values, latest_db_q['n'].values[0]),
                                    
                                    [f"""Stabilitatea emoțională se referă la gradul de discomfort resimțit raportat la gradul de stres perceput. Persoanele instabile emoțional trăiesc senzații de îngrijorare, panică sau teamă într-o măsură mai pronunțată decât ar sugera drept necesar stimulul cu care se confruntă. Ei fluctuează sporadic între stări cu valențe opuse, de la elație ori calm absolut până la panică sau deznădejde deplină. Persoanele cu un scor ridicat la această dimensiune tind să cadă pradă afecțiunilor precum anxietatea sau depresia. Pot fi irascibile, răbufnind din cele mai mici afronturi sau remarci. De asemenea, persoanele instabile simt în mai mică măsură că dețin controlul asupra propriei persoane și că, mai degrabă, sunt purtați și împinși ici-colo de circumstanțe și impulsuri. Cu toate acestea, grijile suplimentare care îi preocupă îi feresc des de la a își asuma riscuri nefondate.""",
                                    f"""Spre deosebire de ei, persoanele stabile emoțional sunt relaxate, nu își pierd cumpătul sub presiune și nu se lasă luați prin surprindere de emoții. Sunt mult mai comfortabile cu ideea de a își asuma un risc și nu se panichează în situații neprevăzute. De asemenea, își mențin calmul chiar și când lucrurile ies cu totul de sub control în jurul lor și pot astfel rămâne cu picioarele pe pământ atunci când sunt puși sub presiune. Rareori cad pradă trăirilor negative și mențin o perspectivă optimistă asupra vieții. În cazuri de conflict, răspund mereu mai degrabă tactic decât impulsiv, ceea ce le conferă un avantaj în astfel de situații. Pot tolera un nivel ridicat de stres, extins pe o perioadă îndelungată de timp, resimțind în mai mică măsură efectele negative ale acestui stil de viață."""],
         ],
         
         'Deschidere Către Experiențe': [
             'deschisă către experiențe',
             ptile_calc(db_qs_df['o'].values, latest_db_q['o'].values[0]),
                                         
                                         [f"""Deschiderea către experiențe este dimensiunea care măsoară trăsăturile ce țin de curiozitate, propensiune artistică, creativitate și nonconformism. Persoanele deschise către experiențe sunt des interesate de o gamă extrem de largă de subiecte, fapt care poate fi o lamă cu două tăișuri pentru ei. Pe de-o parte, poate duce la o personalitate enciclopedică sau spre dobândirea unui număr neobișnuit de mare de abilități; aceasta din urmă este în special probabilă atunci când persoana este caracterizată și de un grad înalt de conștiinciozitate. Pe de altă parte, poate duce la o personalitate diletantă sau nedefinită; aceste trăsături se manifestă mai ales dacă persoană este instabilă și neconștiincioasă. În oricare din cazuri, ei tind să fie consumatori vorace de materiale culturale sau informative, căutand activ să asiste la dezbateri, piese de teatru, prelegeri teoretice sau alte evenimente culturale. Persoanele deschise către experiențe au deseori o latură creativă care se manifestă prin producerea de obiecte de artă precum poezia, fotografia sau pictatul. Ei simt nevoia să se exprime în mod creativ și să se aventureze pe căi necunoscute, ceea ce deseori poate lua o formă excentrică sau iconoclastă, în special dacă persoană este caracterizată și de un grad înalt de dezagreabilitate.""",
                                         f"""Persoanele care scorează scăzut în această dimensiune sunt tradiționaliste și preferă să urmeze calea cunoscută de a face ceva. Nu doresc să inoveze sau să gasească moduri noi de a privi lucrurile sau a acționa. Dacă sunt și conștiincioase, au un grad extrem de pronunțat de concetrare pe esențialul de acțiuni care trebuie urmate pentru a ajunge la scopul propus, fără să se abată atrași de chestiuni irelevante. După ce și-au ales un domeniu de activitate, vor fi reticenți în a îl schimba sau în a îl complementa cu aspecte din domenii netangențiale. În general, pot tolera rutina mai bine și pun mare preț pe a urma categoriile sociale deja stabilite."""]

         ]
    }

    print(ptiles)
    
    context = {
        #  'c':ptiles['c'] * 100,
        #  'a':ptiles['a'] * 100,
        #  'e':ptiles['e'] * 100,
        #  'n':ptiles['n'] * 100,
        #  'o':ptiles['o'] * 100,
         'ptiles': {k: [v[0], int(v[1] * 100), v[2]] for k, v in ptiles.items()},
     }
    
    # print({k: v * 100 for k, v in ptiles.items()})/
    # print(ptiles['c'] * 100)
    

    # if want to generate random scores

    # for i in range(100):
    #     userScore(
             
    #           user = '',
    #           c = np.random.binomial(16, 0.5) - 8, 
    #           a = np.random.binomial(16, 0.5) - 8, 
    #           e = np.random.binomial(16, 0.5) - 8, 
    #           n = np.random.binomial(16, 0.5) - 8, 
    #           o = np.random.binomial(16, 0.5) - 8).save()
    
    return render(request, 'testbigfive/results.html', context)