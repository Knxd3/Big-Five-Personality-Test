# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
from .forms import survey
from .models import userScore
from django.views.decorators.cache import never_cache


SUPPORTED_LANGUAGES = {
    'ro': 'Română',
    'en': 'English',
}
DEFAULT_LANGUAGE = 'en'

QUESTION_TEXTS = {
    'ro': {
        '1': 'Sunt atent(ă) la detalii',
        '2': 'Îmi place ordinea',
        '3': 'Încurc treburile',
        '4': 'Uit să pun lucrurile la locul lor',
        '5': 'Am un vocabular bogat',
        '6': 'Am idei excelente',
        '7': 'Nu mă interesează ideile abstracte',
        '8': 'Discuțiile filozofice mă plictisesc',
        '9': 'Am un suflet bun',
        '10': 'Respect autoritatea',
        '11': 'Sunt o persoană greu de cunoscut',
        '12': 'Nu mă interesează problemele altora',
        '13': 'Sunt sufletul petrecerii',
        '14': 'Inițiez conversații',
        '15': 'Nu vorbesc mult',
        '16': 'Nu-mi place să atrag atenția asupra mea',
        '17': 'Nu sunt stresat(ă)',
        '18': 'Rareori mă simt deprimat(ă)',
        '19': 'Mă îngrijorez mult',
        '20': 'Oscilez de la o stare emoțională la alta',
    },
    'en': {
        '1': 'Pay attention to details.',
        '2': 'Like order.',
        '3': 'Leave my belongings around.',
        '4': 'Often forget to put things back in their proper place.',
        '5': 'Have a rich vocabulary.',
        '6': 'Have excellent ideas.',
        '7': 'Am not interested in abstract ideas.',
        '8': 'Avoid philosophical discussions.',
        '9': 'Have a soft heart.',
        '10': 'Respect authority.',
        '11': 'Am hard to get to know.',
        '12': 'Am not interested in other people\'s problems.',
        '13': 'Am the life of the party.',
        '14': 'Start conversations.',
        '15': 'Don\'t talk a lot.',
        '16': 'Don\'t like to draw attention to myself.',
        '17': 'Am relaxed most of the time.',
        '18': 'Seldom feel blue.',
        '19': 'Worry about things.',
        '20': 'Change my mood a lot.',
    },
}

RESULT_COPY = {
    'comparison': {
        'ro': "Într-un grup de 100 persoane, sunteți o persoană mai {adjective} decât {percent}% dintre aceștia.",
        'en': "In a group of 100 people, you are more {adjective} than {percent}% of them.",
    },
    'percentile_label': {
        'ro': 'Percentil',
        'en': 'Percentile',
    },
}

DIMENSION_CONTENT = [
    {
        'code': 'c',
        'slug': 'conscientiousness',
        'labels': {
            'ro': 'Conștiinciozitate',
            'en': 'Conscientiousness',
        },
        'adjectives': {
            'ro': 'conștiincioasă',
            'en': 'conscientious',
        },
        'paragraphs': {
            'ro': [
                "Conștiinciozitatea este dimensiunea care măsoară trăsăturile ce țin de productivitate, strictețe, aderență la reguli și tendința de a planifica. Persoanele conștiincioase își elaborează traiectorii pe care le urmează, punând în practică pașii către obiectiv. Ele tind să compartimentalizeze chestiunile după categorii fixe și să păstreze ordinea și curățenia, atât concret, privind spațiul personal, cât și abstract, prin judecățile despre situații sau despre ceilalți. De asemenea, tind să nu procrastineze, mai ales dacă sunt și stabile (în terminologia Big Five). Persoanele conștiincioase pot părea încăpățânate și inflexibile, abătându-se cu greu de la setul de reguli pe care au acceptat să îl urmeze.",
                "Spre deosebire, persoanele de cealaltă parte a spectrului au o abordare flexibilă asupra vieții și tind să nu pună mare preț pe simțul responsabilității, pe abordări procedurale (de rutină) sau pe ordine. Au o atitudine relaxată și sunt rareori caracterizate de trăsături precum o voință puternică sau o atitudine disciplinată. Din această cauză pot manifesta comportamente delăsătoare sau inconsecvente; dacă sunt caracterizate de un grad înalt de deschidere către experiențe, pot începe numeroase proiecte fără să le finalizeze. Avantajele acestei abordări apar în ipostaze în care planificarea pe termen lung nu se justifică: în contextul unor economii instabile, al situațiilor de război sau în preajma unor instituții imprevizibile.",
                "Persoanele conștiincioase tind să predomine în domenii manageriale sau administrative, unde respectarea procedurilor, organizarea resurselor și cerințele ridicate de productivitate sunt esențiale. Persoanele neconștiincioase beneficiază profesional de spontaneitatea lor în domenii precum stand-up-ul sau actoria, mai ales dacă sunt și deschise către experiențe. Pentru că își consumă mai puțină energie în planuri de lungă durată, au un risc mai scăzut de burnout și își fac mai mult timp pentru plăcerile vieții."
            ],
            'en': [
                "Conscientiousness captures productivity, self-discipline, adherence to rules, and the tendency to plan ahead. Conscientious people map out the steps toward their goals and follow through. They like to keep things ordered both in their physical space and in how they organise information about situations or other people. They rarely procrastinate, especially when they are also emotionally stable. From the outside they can seem stubborn or inflexible because they are reluctant to deviate from the standards they have agreed to follow.",
                "People on the other side of the spectrum take a more flexible approach to life and place less value on responsibility, routine, or order. They adopt a relaxed attitude and are less likely to be described as strong-willed or disciplined. As a result they may display inconsistent habits; if they are also open to experience, they can start many projects without finishing them. This flexibility can be advantageous when long-term planning is impossible, such as during economic instability, wartime, or when institutions are unpredictable.",
                "Conscientious people often thrive in managerial or administrative roles where procedures, resource allocation, and productivity targets matter most. Less conscientious people may benefit professionally from their spontaneity in fields such as stand-up comedy or acting, especially if they are also high in openness. Because they invest less energy in long-term goals, they are less susceptible to burnout and often make more room for everyday pleasures."
            ],
        },
    },
    {
        'code': 'a',
        'slug': 'agreeableness',
        'labels': {
            'ro': 'Agreeabilitate',
            'en': 'Agreeableness',
        },
        'adjectives': {
            'ro': 'agreeabilă',
            'en': 'agreeable',
        },
        'paragraphs': {
            'ro': [
                "Agreeabilitatea este dimensiunea Big Five care surprinde cordialitatea, cooperarea și amiabilitatea. Persoanele agreabile sunt calde, primitoare și ușor de abordat, iar atitudinea lor deschisă le face companioni plăcuți în orice context. Ei văd ce este mai bun în ceilalți și se raportează la acea parte atunci când interacționează. Valorizează toleranța și înțelegerea reciprocă, urmăresc cooperarea și evită conflictul. Dorința de a menține relații armonioase îi poate face să renunțe prea ușor la propriile nevoi, ceea ce în timp duce la resentimente și uneori la comportamente pasiv-agresive. Evitarea confruntărilor directe poate agrava problemele, transformându-le în situații greu de gestionat.",
                "Persoanele dezagreabile, în schimb, nu sunt calde sau concesive. Ele vor să facă doar ceea ce decid pentru ele însele, fără a compromite ceva de dragul altora. Pot fi necooperante și preferă conflictul în care există un câștigător și un pierzător clar. Negociază aproape întotdeauna în favoarea lor, chiar dacă asta îi dezavantajează pe ceilalți, motiv pentru care pot părea egoiste. În cazuri extreme, dezagreabilitatea poate evolua în comportamente antisociale sau prădătoare. Pentru că detestă autoritatea, pot ajunge să aibă dificultăți cu regulile instituțiilor sau chiar cu legea.",
                "Persoanele agreabile lucrează excelent în echipă și se potrivesc în roluri care cer empatie și răbdare, precum îngrijirea sau consultanța. Persoanele dezagreabile pot avea succes în domenii competitive, unde fermitatea și negocierea dură sunt apreciate, cum ar fi vânzările sau litigiile. Echipele funcționează cel mai bine atunci când combină ambele stiluri, pentru a echilibra cooperarea cu pragmatismul."
            ],
            'en': [
                "Agreeableness covers warmth, cooperation, and amiability. Agreeable people are welcoming and easy to approach, making them pleasant companions in almost any setting. They try to see the best in others and relate to that side when they interact. They place a high value on tolerance and mutual understanding, aim for cooperation, and avoid conflict whenever possible. Because they want harmonious relationships, they sometimes concede too much of what they personally need, which can lead to resentment and, at times, passive-aggressive behaviour. Avoiding direct confrontation can allow issues to grow more difficult to resolve than if they had been addressed early.",
                "Disagreeable people, by contrast, are not warm or accommodating. They want to do what they decide for themselves, without compromising for others. They can be uncooperative and may prefer conflict in which winners and losers are clearly defined. They often negotiate entirely in their own favour, even at the expense of those around them, which can make them appear selfish. In extreme cases, disagreeableness can develop into antisocial or exploitative behaviour. Given their dislike of authority, they may clash with institutional rules or the law.",
                "Agreeable people tend to thrive in collaborative environments and in roles that require empathy and patience, such as caregiving or client support. Disagreeable people can excel in competitive contexts where tough negotiation and firmness are assets, such as sales or litigation. Teams benefit when they include both styles, balancing cooperation with decisiveness."
            ],
        },
    },
    {
        'code': 'e',
        'slug': 'extraversion',
        'labels': {
            'ro': 'Extraversie',
            'en': 'Extraversion',
        },
        'adjectives': {
            'ro': 'extravertă',
            'en': 'extraverted',
        },
        'paragraphs': {
            'ro': [
                "Extraversia măsoară gradul de excitabilitate la stimuli și apetitul pentru activități sociale. Persoanele extraverte se încarcă din interacțiuni și sunt vioaie, reacționând rapid la tot ce se întâmplă în jur. Caută să îi implice pe ceilalți în ceea ce fac și se alătură instinctiv grupurilor când apare ocazia. De obicei sunt asertive și își doresc să fie în centrul atenției, fie pentru a conduce, fie pentru a se distra împreună cu ceilalți. În cazuri extreme pot fi atât de atrase de socializare încât își pierd concentrarea pe obiective, mai ales dacă au un nivel scăzut de conștiinciozitate.",
                "Introverții reacționează mai puțin intens la stimuli și se pot simți copleșiți de zgomot, agitație sau contexte sociale ample. Preferă concentrarea pe care o oferă solitudinea și își desfășoară activitățile în mod independent. Când interacționează, preferă prieteni sau persoane familiare. Tind să răspundă mai lent, punând accent pe calitatea informației și nu pe rapiditate, iar asta îi face uneori să pară retrași. Pentru că le este mai greu să inițieze conversații sau să își facă vocea auzită, pot rămâne în roluri de sprijin chiar și atunci când competențele le permit să conducă.",
                "Nivelul potrivit de extraversie depinde de context. Extraverții strălucesc în roluri ce cer networking, vânzări sau organizarea de evenimente. Introverții performează remarcabil în poziții ce solicită concentrare și atenție la detaliu, precum programarea sau cercetarea. Indiferent de preferință, fiecare poate învăța abilități sociale sau de lucru individual pentru a răspunde cerințelor mediului."
            ],
            'en': [
                "Extraversion measures how responsive someone is to stimulation and how much they seek out activities involving many people. Extraverts gain energy from social interaction and are lively and quick to respond to whatever is happening around them. They try to involve others in what they are doing and instinctively join groups when opportunities arise. Highly extraverted people are assertive and like being in the spotlight, whether to lead or simply to enjoy the moment with others. In extreme cases they may be so drawn to socialising that it distracts them from pursuing their goals, especially when they are also low in conscientiousness.",
                "Introverts, on the other hand, react less strongly to stimulation and can feel overwhelmed by noise, crowds, or busy social settings. They prefer the focus that solitude provides and often keep activities to themselves. When they do engage socially, they tend to choose close friends or familiar people. They usually respond more slowly to questions, favouring thoughtful answers over quick ones, and may view rapid replies as shallow. Because it is harder for them to initiate conversations or speak up, they might stay in supporting roles even when they have the skills to lead.",
                "The optimal level of extraversion depends on the environment. Extraverts can excel in roles requiring networking, sales, or event management. Introverts shine in positions needing deep concentration and careful attention, such as programming or research. Regardless of their preference, people can learn social or independent-working skills to adapt to their professional context."
            ],
        },
    },
    {
        'code': 'n',
        'slug': 'emotional-stability',
        'labels': {
            'ro': 'Stabilitate Emoțională',
            'en': 'Emotional Stability',
        },
        'adjectives': {
            'ro': 'stabilă emoțional',
            'en': 'emotionally stable',
        },
        'paragraphs': {
            'ro': [
                "Stabilitatea emoțională descrie cât disconfort resimte cineva raportat la nivelul de stres perceput. Persoanele instabile emoțional se îngrijorează, intră în panică sau simt teamă mai intens decât ar cere situația. Trăirile lor oscilează de la calm sau euforie la panică ori deznădejde. Scorurile scăzute indică o predispoziție către anxietate sau depresie, reacții irascibile la afronturi minore și senzația că sunt purtați de circumstanțe. Partea pozitivă este că prudența lor suplimentară îi ferește de multe riscuri nejustificate.",
                "Persoanele stabile emoțional rămân calme sub presiune și nu sunt ușor surprinse de emoții puternice. Se simt confortabil să își asume riscuri calculate și rămân stăpâne pe sine în situații neprevăzute. Chiar și când lucrurile scapă de sub control păstrează un ton echilibrat și rareori cad pradă stărilor negative persistente. În conflicte reacționează tactic, nu impulsiv, ceea ce le oferă un avantaj. Pot gestiona niveluri ridicate de stres pe perioade lungi, cu efecte negative reduse.",
                "Nivelul de stabilitate emoțională influențează modul în care oamenii răspund la evenimente neașteptate. Persoanele stabile sunt adesea ancora echipei, iar cele mai puțin stabile aduc vigilență și atenție la detalii critice. Indiferent de profil, tehnicile de reglare emoțională, odihna suficientă și sprijinul social ajută la gestionarea reacțiilor la stres."
            ],
            'en': [
                "Emotional stability reflects how much distress someone experiences relative to the amount of stress they perceive. Emotionally unstable people feel worry, panic, or fear more intensely than the situation alone would warrant. Their mood can swing from calm or elation to panic or hopelessness. When scores on this dimension are low, people are more prone to anxiety or depression, may react irritably to small provocations, and often feel that circumstances and impulses steer them more than their own choices. The upside is that their extra caution can keep them from taking unnecessary risks.",
                "Emotionally stable people, by contrast, remain calm under pressure and are not easily thrown off balance by strong feelings. They are more comfortable taking calculated risks and stay composed during unexpected events. Even when situations spiral out of control, they keep a level head and rarely fall into persistent negative moods. In conflict they respond strategically instead of impulsively, giving them an advantage. They can handle high levels of stress over long periods while feeling fewer negative effects from that lifestyle.",
                "Emotional stability shapes how people respond to setbacks. Stable individuals are often seen as steady anchors within teams, whereas less stable individuals can contribute heightened vigilance or attention to critical concerns. Regardless of baseline, emotion regulation strategies, adequate rest, and social support help people manage stress responses more effectively."
            ],
        },
    },
    {
        'code': 'o',
        'slug': 'openness',
        'labels': {
            'ro': 'Deschidere Către Experiențe',
            'en': 'Openness to Experience',
        },
        'adjectives': {
            'ro': 'deschisă către experiențe',
            'en': 'open to experience',
        },
        'paragraphs': {
            'ro': [
                "Deschiderea către experiențe măsoară curiozitatea, înclinația artistică, creativitatea și nonconformismul. Persoanele foarte deschise sunt interesate de o gamă largă de subiecte, lucru care poate fi o sabie cu două tăișuri. Poate duce la cunoștințe enciclopedice sau la numeroase abilități, mai ales când se combină cu un nivel ridicat de conștiinciozitate. Poate duce însă și la o identitate difuză, mai ales când persoana este instabilă sau neconștiincioasă. Ei consumă avid materiale culturale și informaționale, participă la dezbateri, spectacole sau prelegeri și au adesea o latură creativă exprimată prin scris, fotografie sau pictură. Nevoia de a explora căi noi poate căpăta uneori forme excentrice, mai ales dacă sunt și dezagreabili.",
                "Persoanele cu scoruri scăzute sunt tradiționaliste și preferă metodele cunoscute. Nu își doresc să inoveze sau să privească altfel lucrurile. Combinate cu conștiinciozitate, aceste trăsături duc la o concentrare puternică pe pașii esențiali ai unui scop, fără abatere către detalii irelevante. După ce își aleg un domeniu, sunt reticente în a-l schimba sau în a-l combina cu arii netangente. În general tolerează rutina mai bine și respectă normele sociale existente.",
                "În mediul profesional, nivelul de deschidere influențează preferința pentru inovație sau tradiție. Persoanele foarte deschise se simt în largul lor în roluri creative, de cercetare sau de strategie. Cele mai puțin deschise pot excela în roluri ce cer consecvență, rigoare procedurală sau expertiză aprofundată într-un singur domeniu."
            ],
            'en': [
                "Openness to experience measures curiosity, artistic inclination, creativity, and nonconformity. People high in openness are interested in a wide array of topics, which can be a double-edged sword. It can lead to encyclopedic knowledge or an impressive range of skills, especially when paired with high conscientiousness. It can also result in a dabbler's profile or a lack of clear direction, particularly when combined with emotional instability or low conscientiousness. They avidly consume cultural and informational material and seek out debates, theatre performances, lectures, or other intellectual events. High openness often comes with a creative side that expresses itself through art forms such as writing, photography, or painting. They feel compelled to experiment and explore new paths, sometimes in eccentric or iconoclastic ways, especially when they are also low in agreeableness.",
                "People who score low on openness are more traditional and prefer familiar approaches. They have little interest in innovating or in reframing how things are done. When paired with conscientiousness, they stay extremely focused on the essential steps required to reach a goal, ignoring distractions. After choosing a field, they are reluctant to switch or to combine it with unrelated domains. They generally tolerate routine well and place a high value on established social frameworks.",
                "In the workplace, openness influences whether someone gravitates toward innovation or tradition. Highly open individuals thrive in creative, research, or strategic roles. Less open individuals can excel in positions requiring consistency, procedural rigour, or deep expertise in a specific area."
            ],
        },
    },
]


def _get_language(request):
    lang = (
        request.GET.get('lang')
        or request.POST.get('lang')
        or request.session.get('lang')
        or DEFAULT_LANGUAGE
    )
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    request.session['lang'] = lang
    return lang


@never_cache
def questionnaire(request):
    lang = _get_language(request)

    context = {
        'n': range(1, 21),
        'm': range(1, 6),
        'q_set': QUESTION_TEXTS[lang],
        'lang': lang,
        'languages': SUPPORTED_LANGUAGES,
        'err': None,
    }

    if request.method == 'POST':
        form = survey(request.POST)
        if form.is_valid():
            qry_dict = request.POST.dict()
            new_dict = {}
            for key, value in qry_dict.items():
                if key not in ('csrfmiddlewaretoken', 'lang'):
                    new_dict[key] = list(value)

            raw_ = pd.DataFrame.from_dict(new_dict, orient='index')
            raw_ = raw_.reset_index()
            raw_['index_id'] = raw_['index'].str.extract(r'(\d{1,3})\D*$')
            raw_.columns = ['index', 'value', 'index_id']
            raw_['index_id'] = raw_['index_id'].astype(int)
            raw_['value'] = raw_['value'].astype(int)
            raw_['facet'] = np.where(
                raw_['index_id'] <= 4,
                'c',
                np.where(
                    raw_['index_id'] <= 8,
                    'o',
                    np.where(
                        raw_['index_id'] <= 12,
                        'a',
                        np.where(raw_['index_id'] <= 16, 'e', 'n'),
                    ),
                ),
            )

            raw_['value'] = raw_['value'].values * np.array(
                [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
            )
            scores_agg = raw_.groupby(['facet']).agg({'value': 'sum'})
            scores_f = scores_agg.transpose()
            scores_f1 = pd.DataFrame(
                {'c': [None], 'o': [None], 'a': [None], 'e': [None], 'n': [None], 'user': [np.random.rand(1)]}
            )

            def check(facet_code, frame):
                if facet_code in frame.columns:
                    return frame[facet_code].values[0]
                return None

            scores_f1['c'] = check('c', scores_f)
            scores_f1['a'] = check('a', scores_f)
            scores_f1['e'] = check('e', scores_f)
            scores_f1['n'] = check('n', scores_f)
            scores_f1['o'] = check('o', scores_f)

            user_entry = userScore(
                c=scores_f1['c'].values[0],
                a=scores_f1['a'].values[0],
                e=scores_f1['e'].values[0],
                n=scores_f1['n'].values[0],
                o=scores_f1['o'].values[0],
            )
            user_entry.save()

            return redirect('results')

        else:
            print('invalid form')
            context['err'] = 0

    return render(request, 'testbigfive/index.html', context)


def results(request):
    lang = _get_language(request)

    db_qs = userScore.objects.all().values()
    db_qs_df = pd.DataFrame.from_records(db_qs)

    if db_qs_df.empty:
        context = {
            'dimensions': [],
            'lang': lang,
            'languages': SUPPORTED_LANGUAGES,
            'percentile_label': RESULT_COPY['percentile_label'][lang],
        }
        return render(request, 'testbigfive/results.html', context)

    latest_db_q = db_qs_df.loc[db_qs_df['id'] == db_qs_df['id'].max(), :]

    def ptile_calc(all_values, latest_value):
        return np.sum(latest_value > all_values) / len(all_values)

    dimensions = []
    for dimension in DIMENSION_CONTENT:
        code = dimension['code']
        percentile_value = ptile_calc(db_qs_df[code].values, latest_db_q[code].values[0])
        percent_display = int(percentile_value * 100)
        adjective = dimension['adjectives'][lang]
        paragraphs = dimension['paragraphs'][lang]
        dimensions.append(
            {
                'slug': dimension['slug'],
                'label': dimension['labels'][lang],
                'percentile': percent_display,
                'adjective': adjective,
                'paragraphs': paragraphs,
                'comparison': RESULT_COPY['comparison'][lang].format(adjective=adjective, percent=percent_display),
            }
        )

    context = {
        'dimensions': dimensions,
        'lang': lang,
        'languages': SUPPORTED_LANGUAGES,
        'percentile_label': RESULT_COPY['percentile_label'][lang],
    }

    return render(request, 'testbigfive/results.html', context)
