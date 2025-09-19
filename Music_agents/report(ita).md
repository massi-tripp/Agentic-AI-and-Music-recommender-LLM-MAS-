Cos’è adopted

Quel numero è la somma delle adozioni registrate in memoria: ad ogni apply_adoption(...) aggiungo il song_id in env.history[receiver]. Nel banner stampo:
adopted = sum(len(h) for h in env.history.values())
Se resta 0, significa che nessun PROPOSE è stato elaborato con esito positivo (più probabilmente: gli agenti stanno crashando durante la policy e quindi non spediscono proprio messaggi).

 $py = @"
>> import json, pathlib
>> p = sorted(pathlib.Path('runs').rglob('messages.jsonl'))[-1]
>> prop=adopt=err=0
>> for ln in open(p,'rb'):
>>     rec=json.loads(ln)
>>     t=rec.get('type')
>>     if t=='PROPOSE': prop+=1
>>     elif t=='ADOPT': adopt+=1
>>     elif t=='ERROR': err+=1
>> print(f'LOG: {p} | PROPOSE: {prop} | ADOPT: {adopt} | ERRORS: {err}')
>> "@
>> python -c $py
>>

Primo test con LLM disabled, (adoption_prob= max(0.0, min(1.0, 0.2 + 0.6*sim + 0.2*t)))
parametri:
# ==== RUN / CORE ====
random_seed: 42
max_steps: 4000
dt: 0.1                 # step time (s)
log_every: 50

# ==== AGENTS / GRAPH ====
n_agents: 120
attention_budget: 5
graph:
  type: small_world     # small_world | erdos | barabasi
  k: 6
  p: 0.1
poisson_rate:
  lambda_base: 0.2      # proattività media per agente

Risultati :
(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> python -m src.simulate                   
Run dir: C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents\runs\demo-20250827-165201 | agents=120 | songs=400 | steps=4000 | dt=0.1
[step 0/4000] adopted=0
[step 50/4000] adopted=67
[step 100/4000] adopted=142
[step 150/4000] adopted=235
[step 200/4000] adopted=307
[step 250/4000] adopted=404
[step 300/4000] adopted=487
[step 350/4000] adopted=561
[step 400/4000] adopted=645
[step 450/4000] adopted=718
[step 500/4000] adopted=790
[step 550/4000] adopted=874
[step 600/4000] adopted=954
[step 650/4000] adopted=1041
[step 700/4000] adopted=1139
[step 750/4000] adopted=1217
[step 800/4000] adopted=1290
[step 850/4000] adopted=1390
[step 900/4000] adopted=1470
[step 950/4000] adopted=1550
[step 1000/4000] adopted=1639
[step 1050/4000] adopted=1732
[step 1100/4000] adopted=1844
[step 1150/4000] adopted=1926
[step 1200/4000] adopted=2031
[step 1250/4000] adopted=2119
[step 1300/4000] adopted=2207
[step 1350/4000] adopted=2301
[step 1400/4000] adopted=2399
[step 1450/4000] adopted=2501
[step 1500/4000] adopted=2597
[step 1550/4000] adopted=2670
[step 1600/4000] adopted=2754
[step 1650/4000] adopted=2843
[step 1700/4000] adopted=2930
[step 1750/4000] adopted=3021
[step 1800/4000] adopted=3108
[step 1850/4000] adopted=3204
[step 1900/4000] adopted=3293
[step 1950/4000] adopted=3403
[step 2000/4000] adopted=3488
[step 2050/4000] adopted=3589
[step 2100/4000] adopted=3677
[step 2150/4000] adopted=3791
[step 2200/4000] adopted=3921
[step 2250/4000] adopted=4032
[step 2300/4000] adopted=4142
[step 2350/4000] adopted=4239
[step 2400/4000] adopted=4336
[step 2450/4000] adopted=4420
[step 2500/4000] adopted=4504
[step 2550/4000] adopted=4607
[step 2600/4000] adopted=4701
[step 2650/4000] adopted=4786
[step 2700/4000] adopted=4900
[step 2750/4000] adopted=4999
[step 2800/4000] adopted=5104
[step 2850/4000] adopted=5175
[step 2900/4000] adopted=5273
[step 2950/4000] adopted=5362
[step 3000/4000] adopted=5460
[step 3050/4000] adopted=5548
[step 3100/4000] adopted=5638
[step 3150/4000] adopted=5766
[step 3200/4000] adopted=5880
[step 3250/4000] adopted=5992
[step 3300/4000] adopted=6084
[step 3350/4000] adopted=6189
[step 3400/4000] adopted=6265
[step 3450/4000] adopted=6360
[step 3500/4000] adopted=6454
[step 3550/4000] adopted=6562
[step 3600/4000] adopted=6670
[step 3650/4000] adopted=6758
[step 3700/4000] adopted=6864
[step 3750/4000] adopted=6969
[step 3800/4000] adopted=7066
[step 3850/4000] adopted=7177
[step 3900/4000] adopted=7270
[step 3950/4000] adopted=7369
Done.

(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> 
$py = @"
import json, pathlib
p = sorted(pathlib.Path('runs').rglob('messages.jsonl'))[-1]
prop=adopt=err=0
for ln in open(p,'rb'):
    rec=json.loads(ln)
    t=rec.get('type')
    if t=='PROPOSE': prop+=1
    elif t=='ADOPT': adopt+=1
    elif t=='ERROR': err+=1
print(f'LOG: {p} | PROPOSE: {prop} | ADOPT: {adopt} | ERRORS: {err}')
"@

python -c $py

LOG: runs\demo-20250827-165201\messages.jsonl | PROPOSE: 19210 | ADOPT: 7480 | ERRORS: 0

(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> python -m src.quick_eval

log: runs\demo-20250827-165201\messages.jsonl | ADOPT events: 7480
Top-5 songs by adoption: per ogni canzone, quante adozioni ha generato.
Top-5 songs by adoption: [(275, 215), (257, 210), (314, 194), (167, 174), (385, 168)]
Gini (popolarità): disuguaglianza moderata. 0 = perfetta equità (tutte le canzoni adottate uguale), 1 = tutto concentrato su pochissime. 0.35 suggerisce che non è troppo skewed, quindi (se i dati fossero della run lunga) la popolarità è piuttosto diffusa.
Gini(popularity): 0.312
Top-5 cascades: dimensione della componente più grande del grafo di diffusione per ogni brano. Valori 3–4 sono cascate piccole ⇒ adozioni tante, ma spesso “locali” (con pochi salti); potrebbe essere dovuto a base di adozione alta (adozioni “quasi indipendenti”) o a grafi poco profondi. È un indizio utile: conviene misurare profondità media, struttural virality e R (numero riproduttivo) per capire se le canzoni si propagano “a catena” o “sparpagliato”.
Top-5 cascades (song_id, size): [(326, 4), (134, 4), (224, 4), (118, 4), (257, 4)]

Inequality: Gini + Herfindahl + punti Lorenz (se vuoi plottarli).

Efficienza: tasso di accettazione complessivo e per canzone (adopt / propose).

Cascade: top-5 per grandezza, profondità massima, ampiezza massima, structural virality (media delle distanze tra nodi nella “spanning tree” della cascata).

R (numero riproduttivo): figli medi per adottante (out-degree medio nei grafi di adozione).

Exposure: quante proposte precedono un’adozione (media, mediana, 95° percentile).

(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> python -m src.metrics_advanced

---- Popularity ----
{'total_adopts': 7480, 'unique_songs_adopted': 100, 'top5': [(275, 215), (257, 210), (314, 194), (167, 174), (385, 168)], 'gini': 0.312, 'herfindahl': 0.013, 'lorenz': [(0.0, 0.0), (0.01, 0.00026737967914438503), (0.02, 0.0008021390374331551), (0.03, 0.0022727272727272726), (0.04, 0.004411764705882353), (0.05, 0.007085561497326203), (0.06, 0.009759358288770054), (0.07, 0.01270053475935829), (0.08, 0.015775401069518715), (0.09, 0.018850267379679143), (0.1, 0.02232620320855615), (0.11, 0.026336898395721925), (0.12, 0.03048128342245989), (0.13, 0.03462566844919786), (0.14, 0.03890374331550802), (0.15, 0.04331550802139037), (0.16, 0.04772727272727273), (0.17, 0.05227272727272727), (0.18, 0.056818181818181816), (0.19, 0.06163101604278075), (0.2, 0.06684491978609626), (0.21, 0.07205882352941176), (0.22, 0.07727272727272727), (0.23, 0.08262032085561498), (0.24, 0.08796791443850267), (0.25, 0.09358288770053476), (0.26, 0.09919786096256684), (0.27, 0.10494652406417113), (0.28, 0.11082887700534759), (0.29, 0.11671122994652407), (0.3, 0.12286096256684492), (0.31, 0.12914438502673797), (0.32, 0.1358288770053476), (0.33, 0.14278074866310161), (0.34, 0.1498663101604278), (0.35, 0.156951871657754), (0.36, 0.16417112299465242), (0.37, 0.171524064171123), (0.38, 0.17901069518716578), (0.39, 0.18663101604278076), (0.4, 0.19438502673796793), (0.41, 0.2021390374331551), (0.42, 0.21016042780748664), (0.43, 0.21831550802139038), (0.44, 0.2266042780748663), (0.45, 0.23529411764705882), (0.46, 0.24411764705882352), (0.47, 0.2529411764705882), (0.48, 0.2620320855614973), (0.49, 0.2712566844919786), (0.5, 0.28048128342245987), (0.51, 0.2898395721925134), (0.52, 0.299331550802139), (0.53, 0.3089572192513369), (0.54, 0.3185828877005348), (0.55, 0.3286096256684492), (0.56, 0.3390374331550802), (0.57, 0.3498663101604278), (0.58, 0.3606951871657754), (0.59, 0.3716577540106952), (0.6, 0.382620320855615), (0.61, 0.39371657754010697), (0.62, 0.40494652406417114), (0.63, 0.4163101604278075), (0.64, 0.42780748663101603), (0.65, 0.4393048128342246), (0.66, 0.45093582887700534), (0.67, 0.4625668449197861), (0.68, 0.474331550802139), (0.69, 0.48622994652406415), (0.7, 0.4983957219251337), (0.71, 0.5105614973262033), (0.72, 0.5227272727272727), (0.73, 0.5351604278074866), (0.74, 0.5475935828877005), (0.75, 0.5600267379679145), (0.76, 0.5727272727272728), (0.77, 0.5855614973262032), (0.78, 0.5983957219251337), (0.79, 0.6114973262032085), (0.8, 0.6245989304812835), (0.81, 0.638235294117647), (0.82, 0.652139037433155), (0.83, 0.6660427807, (0.83, 0.6660427807486631), (0.84, 0.6800802139037433), (0.85, 0.6942513368983957), (0.86, 0.7096256684491978), (0.87, 0.725), (0.88, 0.7405080213903743), (0.89, 0.7564171122994653), (0.9, 0.774331550802139), (0.91, 0.7926470588235294), (0.92, 0.811096256684492), (0.93, 0.8295454545454546), (0.94, 0.8501336898395722), (0.95, 0.871524064171123), (0.96, 0.8939839572192514), (0.97, 0.9172459893048128), (0.98, 0.9431818181818182), (0.99, 0.9712566844919787), (1.0, 1.0)]}
---- Efficiency ----
{'proposes': 19210, 'adopts': 7480, 'overall_acceptance': 0.389, 'top5_acceptance_songs': [(293, 0.8787878787878788), (377, 0.6956521739130435), (323, 0.6933333333333334), (257, 0.6774193548387096), (303, 0.6621621621621622)]}
---- Cascades ----
{'top5_cascades': [(290, 9, 1, 6, 1.333), (276, 8, 1, 5, 1.286), (385, 8, 1, 5, 1.286), (126, 8, 1, 5, 1.286), (118, 7, 1, 5, 1.444)], 'avg_depth': 0.98, 'avg_virality': 1.299}
---- Reproduction ----
{'R_mean': 0.663, 'R_median': 0}
---- Exposure ----
{'mean_exposures': 41.233, 'median_exposures': 41.0, 'p95': 79}


Secondo test, uguale al primo ma con LLM enabled, utilizziamo PHI3 mini.
Risultati:

Run dir: C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents\runs\demo-20250911-151127 | agents=120 | songs=400 | steps=4000 | dt=0.1
[step 0/4000] adopted=0
[step 50/4000] adopted=0
[step 100/4000] adopted=0
[step 150/4000] adopted=0
[step 200/4000] adopted=0
[step 250/4000] adopted=0
[step 300/4000] adopted=0
[step 350/4000] adopted=0
[step 400/4000] adopted=0
[step 450/4000] adopted=0
[step 500/4000] adopted=0
[step 550/4000] adopted=1
[step 600/4000] adopted=1
[step 650/4000] adopted=1
[step 700/4000] adopted=1
[step 750/4000] adopted=1
[step 800/4000] adopted=1
[step 850/4000] adopted=1
[step 900/4000] adopted=1
[step 950/4000] adopted=2
[step 1000/4000] adopted=2
[step 1050/4000] adopted=3
[step 1100/4000] adopted=3
[step 1150/4000] adopted=3
[step 1200/4000] adopted=3
[step 1250/4000] adopted=3
[step 1300/4000] adopted=4
[step 1350/4000] adopted=4
[step 1400/4000] adopted=4
[step 1450/4000] adopted=4
[step 1500/4000] adopted=4
[step 1550/4000] adopted=4
[step 1600/4000] adopted=4
[step 1650/4000] adopted=4
[step 1700/4000] adopted=4
[step 1750/4000] adopted=4
[step 1800/4000] adopted=4
[step 1850/4000] adopted=4
[step 1900/4000] adopted=5
[step 1950/4000] adopted=5
[step 2000/4000] adopted=7
[step 2050/4000] adopted=7
[step 2100/4000] adopted=7
[step 2150/4000] adopted=7
[step 2200/4000] adopted=9
[step 2250/4000] adopted=9
[step 2300/4000] adopted=9
[step 2350/4000] adopted=10
[step 2400/4000] adopted=12
[step 2450/4000] adopted=12
[step 2500/4000] adopted=12
[step 2550/4000] adopted=13
[step 2600/4000] adopted=13
[step 2650/4000] adopted=13
[step 2700/4000] adopted=13
[step 2750/4000] adopted=13
[step 2800/4000] adopted=13
[step 2850/4000] adopted=14
[step 2900/4000] adopted=14
[step 2950/4000] adopted=14
[step 3000/4000] adopted=14
[step 3050/4000] adopted=14
[step 3100/4000] adopted=14
[step 3150/4000] adopted=15
[step 3200/4000] adopted=15
[step 3250/4000] adopted=15
[step 3300/4000] adopted=19
[step 3350/4000] adopted=21
[step 3400/4000] adopted=21
[step 3450/4000] adopted=21
[step 3500/4000] adopted=24
[step 3550/4000] adopted=25
[step 3600/4000] adopted=25
[step 3650/4000] adopted=26
[step 3700/4000] adopted=27
[step 3750/4000] adopted=27
[step 3800/4000] adopted=27
[step 3850/4000] adopted=28
[step 3900/4000] adopted=28
[step 3950/4000] adopted=28
Done.

$py = @"
import json, pathlib
p = sorted(pathlib.Path('runs').rglob('messages.jsonl'))[-1]
prop=adopt=err=0
for ln in open(p,'rb'):
    rec=json.loads(ln)
    t=rec.get('type')
    if t=='PROPOSE': prop+=1
    elif t=='ADOPT': adopt+=1
    elif t=='ERROR': err+=1
print(f'LOG: {p} | PROPOSE: {prop} | ADOPT: {adopt} | ERRORS: {err}')
"@
python -c $py
LOG: runs\demo-20250911-151127\messages.jsonl | PROPOSE: 127 | ADOPT: 30 | ERRORS: 0

(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> python -m src.quick_eval 
log: runs\demo-20250911-151127\messages.jsonl | ADOPT events: 30
Top-5 songs by adoption: [(145, 2), (291, 2), (178, 2), (205, 2), (137, 1)]
Gini(popularity): 0.113
Top-5 cascades (song_id, size): [(145, 3), (291, 3), (205, 3), (137, 2), (25, 2)]

(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> python -m src.metrics_advanced
Log: runs\demo-20250911-151127\messages.jsonl
---- Popularity ----
{'total_adopts': 30, 'unique_songs_adopted': 26, 'top5': [(145, 2), (291, 2), (178, 2), (205, 2), (137, 1)], 'gini': 0.113, 'herfindahl': 0.042, 'lorenz': [(0.0, 0.0), (0.038461538461538464, 0.03333333333333333), (0.07692307692307693, 0.06666666666666667), (0.11538461538461539, 0.1), (0.15384615384615385, 0.13333333333333333), (0.19230769230769232, 0.16666666666666666), (0.23076923076923078, 0.2), (0.2692307692307692, 0.23333333333333334), (0.3076923076923077, 0.26666666666666666), (0.34615384615384615, 0.3), (0.38461538461538464, 0.3333333333333333), (0.4230769230769231, 0.36666666666666664), (0.46153846153846156, 0.4), (0.5, 0.43333333333333335), (0.5384615384615384, 0.4666666666666667), (0.5769230769230769, 0.5), (0.6153846153846154, 0.5333333333333333), (0.6538461538461539, 0.5666666666666667), (0.6923076923076923, 0.6), (0.7307692307692307, 0.6333333333333333), (0.7692307692307693, 0.6666666666666666), (0.8076923076923077, 0.7), (0.8461538461538461, 0.7333333333333333), (0.8846153846153846, 0.8), (0.9230769230769231, 0.8666666666666667), (0.9615384615384616, 0.9333333333333333), (1.0, 1.0)]}
---- Efficiency ----
{'proposes': 127, 'adopts': 30, 'overall_acceptance': 0.236, 'top5_acceptance_songs': [(135, 1.0), (142, 1.0), (145, 1.0), (150, 1.0), (291, 1.0)]}
---- Cascades ----
{'top5_cascades': [(178, 4, 1, 2, 1.0), (145, 3, 1, 2, 1.333), (291, 3, 1, 2, 1.333), (205, 3, 1, 2, 1.333), (137, 2, 1, 1, 1.0)], 'avg_depth': 1, 'avg_virality': 1.038}
---- Reproduction ----
{'R_mean': 0.526, 'R_median': 0}
---- Exposure ----
{'mean_exposures': 1.033, 'median_exposures': 1.0, 'p95': 1}

$py = @"
import json, pathlib
p = sorted(pathlib.Path('runs').rglob('messages.jsonl'))[-1]
dec=llm=heur=0; examples=[]
with open(p,'rb') as f:
    for ln in f:
        rec=json.loads(ln)
        if rec.get('type')=='DECISION':
            dec += 1
            src = rec.get('source','?')
            if src=='llm':
                llm += 1
                if len(examples)<3:
                    examples.append({k:rec.get(k) for k in ('step','agent','song_id','targets','explain')})
            elif src=='heuristic':
                heur += 1
print('Log:', p)
print('DECISION total:', dec, '| LLM:', llm, '| Heuristic:', heur)
print('LLM examples:', examples)
"@
python -c $py

Log: runs\demo-20250911-151127\messages.jsonl
DECISION total: 90 | LLM: 90 | Heuristic: 0
LLM examples: [{'step': 67, 'agent': '97', 'song_id': 128, 'targets': ['20'], 'explain': 'high trust and low load candidates selected'}, {'step': 91, 'agent': '0', 'song_id': 137, 'targets': ['1'], 'explain': ''}, {'step': 134, 'agent': '15', 'song_id': 159, 'targets': ['14', '16'], 'explain': "recommended song for user 305 based on their recent listens and neighbors' trust scores"}]


$py = @"
import json, pathlib
p = sorted(pathlib.Path('runs').rglob('messages.jsonl'))[-1]

heur = 0
nonheur = 0
examples = []

with open(p,'rb') as f:
    for ln in f:
        rec = json.loads(ln)
        if rec.get('type') == 'DECISION':
            exp = rec.get('explain','')
            if exp == 'heuristic':
                heur += 1
            else:
                nonheur += 1
                if len(examples) < 16:
                    examples.append({
                        'step': rec.get('step'),
                        'agent': rec.get('agent'),
                        'song_id': rec.get('song_id'),
                        'explain': exp
                    })

print('Log file:', p)
print('DECISION with explain="heuristic":', heur)
print('DECISION with explain != "heuristic":', nonheur)
print('Examples of non-heuristic explains:')
for e in examples:
    print(e)
"@
python -c $py

Log file: runs\demo-20250911-151127\messages.jsonl
DECISION with explain=heuristic: 0
DECISION with explain != heuristic: 90
Examples of non-heuristic explains:
{'step': 67, 'agent': '97', 'song_id': 128, 'explain': 'high trust and low load candidates selected'}
{'step': 91, 'agent': '0', 'song_id': 137, 'explain': ''}
{'step': 134, 'agent': '15', 'song_id': 159, 'explain': "recommended song for user 305 based on their recent listens and neighbors' trust scores"}
{'step': 158, 'agent': '29', 'song_id': 84, 'explain': ''}
{'step': 182, 'agent': '64', 'song_id': 1, 'explain': 'highly trusted users recommended this song'}
{'step': 205, 'agent': '115', 'song_id': 109, 'explain': 'high trust and low load candidates'}
{'step': 240, 'agent': '17', 'song_id': 291, 'explain': 'short'}
{'step': 268, 'agent': '42', 'song_id': 219, 'explain': 'recommended song for user 3 based on neighbors with highest trust and load'}
{'step': 287, 'agent': '71', 'song_id': 39, 'explain': 'highly recommended song'}
{'step': 323, 'agent': '74', 'song_id': 42, 'explain': ''}
{'step': 346, 'agent': '103', 'song_id': 150, 'explain': ''}
{'step': 382, 'agent': '22', 'song_id': 10, 'explain': ''}
{'step': 405, 'agent': '44', 'song_id': 185, 'explain': 'high trust and low load candidates'}
{'step': 460, 'agent': '85', 'song_id': 145, 'explain': 'short'}
{'step': 501, 'agent': '86', 'song_id': 118, 'explain': "recommended song for user 1 based on their recent listens and neighbors' trust scores"}
{'step': 524, 'agent': '2', 'song_id': 181, 'explain': 'recommended song for user 17 based on their recent listens and trust score'}


Grande — adesso che hai il logging, i numeri ti dicono già cosa sistemare: solo 15 decisioni con LLM significa che il ramo LLM viene chiamato pochissimo rispetto al totale. Ecco cosa fare subito (pratico, a prova di errore) per:

aumentare il numero di decisioni LLM,

verificare che non stai silenziando errori,

fare prove “scientifiche” da mostrare al prof.

Le DECISION (LLM o euristica) si attivano solo quando poisson_fire() è True. Se il tuo lambda_base è piccolo, quasi nessun agente decide.

Nel tuo configs/base.yaml, alza:

poisson_rate:
  lambda_base: 0.02   # prova 0.02–0.05 (prima era verosimilmente << 0.01)
dt: 0.1               # ok
steps: 4000           # ok per un run standard


Aspettativa: expected_decisions_per_agent ≈ steps * lambda_base * dt.
Con 0.02 * 0.1 * 4000 = 8 decisioni / agente → ~960 decisioni su 120 agenti (molto più di 15).

2) Non “inghiottire” errori nel policy (così li vedi nel log)

Adesso il tuo policy_phi.py ha un try/except che ritorna euristica se qualcosa va storto → nel log non vedrai mai errori e conterai meno LLM. Meglio lasciar propagare l’eccezione (l’Agent la logga come type:"ERROR").

In questo modo, se l’LLM fallisce, vedi ERROR nel log (grazie al try/except in Agent.proactive) e non confondi l’errore con una decisione “euristica”.

4) Aumenta la % di decisioni LLM effettive

Anche con più “pensate”, potresti vedere poche source:"llm" se:

gating troppo severo (gate_threshold alto) → tante DECISION ma poi poche PROPOSE (ok),
però noi contiamo LLM sulle DECISION, quindi questo non spiega le 15.

In realtà il problema era il poisson (punto 1) o errori silenziati (punto 2).

Comunque, parametri da provare per esplorare:

gate_threshold: 0.40 → 0.55 (più severo ⇒ meno spam, acceptance ↑).

cooldown: 20 → 30–40 (meno ripetizioni ⇒ exposure ↓).

attention_budget: 2 (o anche 1) per forte scarsità di attenzione.

Cosa fa ogni parametro (e quando alzarlo)

max_steps

↑ = processi più lunghi ⇒ più adozioni/cascade mature, ma run più lenti.

Ha senso alzarlo se vuoi osservare code lunghe delle cascades e convergenza delle metriche (Gini/Herfindahl).

Range suggerito: 1 000 (debug) · 4 000 (default) · 10 000 (studio/stress).

n_agents

↑ = rete più grande ⇒ più interazioni, molte più chiamate LLM.

Ha senso alzarlo se vuoi vedere fenomeni di viralità su scala o misurare robustezza/throughput.

Attento: raddoppiare gli agenti può moltiplicare le chiamate ⇒ valuta OLLAMA_NUM_PARALLEL e un semaforo nel codice.

Range: 60 (fast) · 120 (default) · 300–500 (stress).

attention_budget

Quante message slot/step ogni agente riesce a processare.

↑ = meno code e più adozioni “non perse”, ma più “pressione” sociale; ↓ = scarsità di attenzione, più realistica.

In genere 1–3 è più “realistico” per studiare esposizione e saturazione; 5 è generoso (va bene per sbloccare).

Suggerimento: usa 2–3 per esperimenti su exposure e acceptance.

graph (topologia influenza fortemente le cascades)

small_world con k (grado iniziale) e p (random rewiring):

k ↑ = più vicini ⇒ più proposte e adozioni;

p ↑ = più scorciatoie ⇒ cascades più globali (salita di virality).

Se vuoi reti scale-free, prova barabasi (hubs ⇒ super diffusers).

Regola pratica: small_world (k=6, p=0.1) è un buon default; per più “salti” globali prova p=0.2–0.3.

sample.n_songs

↑ = mercato più ampio ⇒ diversità ↑, cascades più frammentate;

↓ = competizione più concentrata ⇒ top songs si polarizzano (Gini ↑).

200–400 è comodo; salire oltre 800 ha senso solo per esperimenti di diversità.

by_popularity_quantile

0.5 = metà più popolari. Abbassarlo (es. 0.3) rende l’ambiente più difficile per l’adozione (meno ovvi “hit”).

Se vuoi testare la capacità di scoperta (exploration), prova 0.3–0.4.

filters.exclude_explicit

Lascialo a false salvo requisiti etici; non influisce molto sulle dinamiche (a meno che il dataset sia sbilanciato).

Facciamo queste modifiche:
Virality stress (cercare cascades profonde)
max_steps: 6000
n_agents: 200
graph: {type: small_world, k: 8, p: 0.25}
sample: {n_songs: 400, by_popularity_quantile: 0.5}

In teoria:
Più shortcut globali ⇒ aumentano depth/virality; attenzione al carico LLM.

LLM false
(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> python -m src.simulate
Run dir: C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents\runs\demo-20250908-143932 | agents=200 | songs=400 | steps=6000 | dt=0.1
[step 0/6000] adopted=0
[step 50/6000] adopted=53
[step 100/6000] adopted=116
[step 150/6000] adopted=182
[step 200/6000] adopted=256
[step 250/6000] adopted=328
[step 300/6000] adopted=397
[step 350/6000] adopted=459
[step 400/6000] adopted=542
[step 450/6000] adopted=616
[step 500/6000] adopted=684
[step 550/6000] adopted=755
[step 600/6000] adopted=815
[step 650/6000] adopted=876
[step 700/6000] adopted=962
[step 750/6000] adopted=1015
[step 800/6000] adopted=1098
[step 850/6000] adopted=1175
[step 900/6000] adopted=1252
[step 950/6000] adopted=1319
[step 1000/6000] adopted=1395
[step 1050/6000] adopted=1487
[step 1100/6000] adopted=1569
[step 1150/6000] adopted=1638
[step 1200/6000] adopted=1719
[step 1250/6000] adopted=1796
[step 1300/6000] adopted=1876
[step 1350/6000] adopted=1952
[step 1400/6000] adopted=2029
[step 1450/6000] adopted=2107
[step 1500/6000] adopted=2190
[step 1550/6000] adopted=2253
[step 1600/6000] adopted=2328
[step 1650/6000] adopted=2397
[step 1700/6000] adopted=2477
[step 1750/6000] adopted=2549
[step 1800/6000] adopted=2612
[step 1850/6000] adopted=2692
[step 1900/6000] adopted=2759
[step 1950/6000] adopted=2831
[step 2000/6000] adopted=2915
[step 2050/6000] adopted=3006
[step 2100/6000] adopted=3081
[step 2150/6000] adopted=3147
[step 2200/6000] adopted=3239
[step 2250/6000] adopted=3317
[step 2300/6000] adopted=3411
[step 2350/6000] adopted=3489
[step 2400/6000] adopted=3578
[step 2450/6000] adopted=3671
[step 2500/6000] adopted=3749
[step 2550/6000] adopted=3830
[step 2600/6000] adopted=3913
[step 2650/6000] adopted=3988
[step 2700/6000] adopted=4070
[step 2750/6000] adopted=4154
[step 2800/6000] adopted=4235
[step 2850/6000] adopted=4324
[step 2900/6000] adopted=4400
[step 2950/6000] adopted=4478
[step 3000/6000] adopted=4557
[step 3050/6000] adopted=4630
[step 3100/6000] adopted=4711
[step 3150/6000] adopted=4794
[step 3200/6000] adopted=4881
[step 3250/6000] adopted=4970
[step 3300/6000] adopted=5045
[step 3350/6000] adopted=5130
[step 3400/6000] adopted=5198
[step 3450/6000] adopted=5280
[step 3500/6000] adopted=5369
[step 3550/6000] adopted=5441
[step 3600/6000] adopted=5518
[step 3650/6000] adopted=5605
[step 3700/6000] adopted=5691
[step 3750/6000] adopted=5768
[step 3800/6000] adopted=5839
[step 3850/6000] adopted=5912
[step 3900/6000] adopted=6002
[step 3950/6000] adopted=6083
[step 4000/6000] adopted=6162
[step 4050/6000] adopted=6253
[step 4100/6000] adopted=6338
[step 4150/6000] adopted=6410
[step 4200/6000] adopted=6482
[step 4250/6000] adopted=6565
[step 4300/6000] adopted=6632
[step 4350/6000] adopted=6715
[step 4400/6000] adopted=6803
[step 4450/6000] adopted=6875
[step 4500/6000] adopted=6964
[step 4550/6000] adopted=7032
[step 4600/6000] adopted=7122
[step 4650/6000] adopted=7190
[step 4700/6000] adopted=7280
[step 4750/6000] adopted=7367
[step 4800/6000] adopted=7435
[step 4850/6000] adopted=7515
[step 4900/6000] adopted=7600
[step 4950/6000] adopted=7682
[step 5000/6000] adopted=7761
[step 5050/6000] adopted=7842
[step 5100/6000] adopted=7941
[step 5150/6000] adopted=8013
[step 5200/6000] adopted=8093
[step 5250/6000] adopted=8175
[step 5300/6000] adopted=8271
[step 5350/6000] adopted=8348
[step 5400/6000] adopted=8430
[step 5450/6000] adopted=8502
[step 5500/6000] adopted=8591
[step 5550/6000] adopted=8673
[step 5600/6000] adopted=8749
[step 5650/6000] adopted=8831
[step 5700/6000] adopted=8918
[step 5750/6000] adopted=8983
[step 5800/6000] adopted=9064
[step 5850/6000] adopted=9142
[step 5900/6000] adopted=9220
[step 5950/6000] adopted=9308
Done.

$py = @"
import json, pathlib
p = sorted(pathlib.Path('runs').rglob('messages.jsonl'))[-1]
prop=adopt=err=0
for ln in open(p,'rb'):
    rec=json.loads(ln)
    t=rec.get('type')
    if t=='PROPOSE': prop+=1
    elif t=='ADOPT': adopt+=1
    elif t=='ERROR': err+=1
print(f'LOG: {p} | PROPOSE: {prop} | ADOPT: {adopt} | ERRORS: {err}')
"@

python -c $py

LOG: runs\demo-20250908-143932\messages.jsonl | PROPOSE: 12871 | ADOPT: 9387 | ERRORS: 0

python -m src.quick_eval      
log: runs\demo-20250908-143932\messages.jsonl | ADOPT events: 9387
Top-5 songs by adoption: [(385, 295), (273, 228), (0, 211), (276, 197), (212, 191)]
Gini(popularity): 0.284
Top-5 cascades (song_id, size): [(190, 4), (212, 3), (58, 3), (18, 3), (335, 3)]

python -m src.metrics_advanced
Log: runs\demo-20250908-143932\messages.jsonl
---- Popularity ----
{'total_adopts': 9387, 'unique_songs_adopted': 99, 'top5': [(385, 295), (273, 228), (0, 211), (276, 197), (212, 191)], 'gini': 0.284, 'herfindahl': 0.013, 'lorenz': [(0.0, 0.0), (0.010101010101010102, 0.0031959092361776927), (0.020202020202020204, 0.007244060935336103), (0.030303030303030304, 0.011824864173857462), (0.04040404040404041, 0.01640566741237882), (0.050505050505050504, 0.02098647065090018), (0.06060606060606061, 0.02588686481303931), (0.0707070707070707, 0.03078725897517844), (0.08080808080808081, 0.03568765313731757), (0.09090909090909091, 0.04069457760732929), (0.10101010101010101, 0.04570150207734101), (0.1111111111111111, 0.050921487163097905), (0.12121212121212122, 0.0561414722488548), (0.13131313131313133, 0.061361457334611694), (0.1414141414141414, 0.06679450303611377), (0.15151515151515152, 0.07233407904548844), (0.16161616161616163, 0.0779801853627357), (0.1717171717171717, 0.08362629167998295), (0.18181818181818182, 0.08927239799723022), (0.1919191919191919, 0.09502503462235005), (0.20202020202020202, 0.1007776712474699), (0.21212121212121213, 0.10663683818046234), (0.2222222222222222, 0.11249600511345478), (0.23232323232323232, 0.11835517204644722), (0.24242424242424243, 0.12432086928731224), (0.25252525252525254, 0.13039309683604985), (0.26262626262626265, 0.13646532438478748), (0.2727272727272727, 0.14264408224139768), (0.2828282828282828, 0.1488228400980079), (0.29292929292929293, 0.15521465857036326), (0.30303030303030304, 0.16171300735059124), (0.31313131313131315, 0.16821135613081922), (0.32323232323232326, 0.1747097049110472), (0.3333333333333333, 0.18120805369127516), (0.3434343434343434, 0.18770640247150314), (0.35353535353535354, 0.1943112815596037), (0.36363636363636365, 0.20102269095557687), (0.37373737373737376, 0.20773410035155002), (0.3838383838383838, 0.21444550974752316), (0.3939393939393939, 0.22115691914349633), (0.40404040404040403, 0.22797485884734206), (0.41414141414141414, 0.23479279855118781), (0.42424242424242425, 0.24171726856290615), (0.43434343434343436, 0.24874826888249707), (0.4444444444444444, 0.255779269202088), (0.45454545454545453, 0.2632363907531693), (0.46464646464646464, 0.27069351230425054), (0.47474747474747475, 0.27825716416320445), (0.48484848484848486, 0.2858208160221583), (0.494949494949495, 0.2934909981889848), (0.5050505050505051, 0.30116118035581124), (0.5151515151515151, 0.3090444231383829), (0.5252525252525253, 0.3169276659209545), (0.5353535353535354, 0.32481090870352614), (0.5454545454545454, 0.3328006817939704), (0.5555555555555556, 0.3408969851922872), (0.5656565656565656, 0.34909981889847663), (0.5757575757575758, 0.3574091829125386), (0.5858585858585859, 0.3658250772344732), (0.5959595959595959, 0.3743475018642804), (0.6060606060606061, 0.38297645680196013), (0.6161616161616161, 0.39224459358687547), (0.6262626262626263, 0.4021519122190263), (0.6363636363636364, 0.4129114733141579), (0.6464646464646465, 0.4240971556407798), (0.6565656565656566, 0.4353893682752743), (0.6666666666666666, 0.4467881112176414), (0.6767676767676768, 0.4582933844678811), (0.6868686868686869, 0.47001171833386596), (0.696969696969697, 0.48194311281559604), (0.7070707070707071, 0.49430062852881645), (0.7171717171717171, 0.5070842654735273), (0.7272727272727273, 0.5200809630339832), (0.7373737373737373, 0.5336103121338021), (0.7474747474747475, 0.5472461915414936), (0.7575757575757576, 0.5609886012570576), (0.7676767676767676, 0.5747310109726217), (0.7777777777777778, 0.5887930116118035), (0.7878787878787878, 0.6032811334824758), (0.797979797979798, 0.6178757856610205), (0.8080808080808081, 0.6336422712261638), (0.8181818181818182, 0.6494087567913072), (0.8282828282828283, 0.6651752423564504), (0.8383838383838383, 0.6815809097688292), (0.8484848484848485, 0.698519228720571), (0.8585858585858586, 0.7155640779801854), (0.8686868686868687, 0.7327154575476723), (0.8787878787878788, 0.7503994886545222), (0.8888888888888888, 0.7680835197613721), (0.898989898989899, 0.785767550868222), (0.9090909090909091, 0.8043038244380526), (0.9191919191919192, 0.8228400980078833), (0.9292929292929293, 0.8418024928092043), (0.9393939393939394, 0.8609779482262704), (0.9494949494949495, 0.8804729945669543), (0.9595959595959596, 0.9008202833706189), (0.9696969696969697, 0.9218067540215191), (0.9797979797979798, 0.9442846489826355), (0.98989898989899, 0.968573559177586), (1.0, 1.0)]}        
---- Efficiency ----
{'proposes': 12871, 'adopts': 9387, 'overall_acceptance': 0.729, 'top5_acceptance_songs': [(243, 0.9805825242718447), (162, 0.9666666666666667), (323, 0.9512195121951219), (234, 0.9298245614035088), (389, 0.9294117647058824)]}
---- Cascades ----
{'top5_cascades': [(273, 7, 1, 4, 1.2), (385, 7, 1, 4, 1.2), (139, 6, 1, 3, 1.0), (0, 6, 1, 3, 1.0), (212, 5, 1, 3, 1.25)], 'avg_depth': 1, 'avg_virality': 1.088}
---- Reproduction ----
{'R_mean': 0.555, 'R_median': 0.0}
---- Exposure ----
{'mean_exposures': 44.214, 'median_exposures': 44, 'p95': 85}

DECISION total: 24077 | LLM: 0 | Heuristic: 24077

DECISION with explain=heuristic: 24077
DECISION with explain != heuristic: 0


ora LLM True

(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> python -m src.simulate        
Run dir: C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents\runs\demo-20250911-163711 | agents=200 | songs=400 | steps=6000 | dt=0.1
[step 0/6000] adopted=0
[step 50/6000] adopted=0
[step 100/6000] adopted=0
[step 150/6000] adopted=0
[step 200/6000] adopted=0
[step 250/6000] adopted=0
[step 300/6000] adopted=0
[step 350/6000] adopted=0
[step 400/6000] adopted=0
[step 450/6000] adopted=0
[step 500/6000] adopted=1
[step 550/6000] adopted=1
[step 600/6000] adopted=1
[step 650/6000] adopted=1
[step 700/6000] adopted=1
[step 750/6000] adopted=1
[step 800/6000] adopted=1
[step 850/6000] adopted=1
[step 900/6000] adopted=1
[step 950/6000] adopted=1
[step 1000/6000] adopted=2
[step 1050/6000] adopted=2
[step 1100/6000] adopted=2
[step 1150/6000] adopted=2
[step 1200/6000] adopted=2
[step 1250/6000] adopted=2
[step 1300/6000] adopted=2
[step 1350/6000] adopted=2
[step 1400/6000] adopted=2
[step 1450/6000] adopted=3
[step 1500/6000] adopted=3
[step 1550/6000] adopted=3
[step 1600/6000] adopted=3
[step 1650/6000] adopted=3
[step 1700/6000] adopted=4
[step 1750/6000] adopted=5
[step 1800/6000] adopted=5
[step 1850/6000] adopted=5
[step 1900/6000] adopted=5
[step 1950/6000] adopted=6
[step 2000/6000] adopted=6
[step 2050/6000] adopted=6
[step 2100/6000] adopted=7
[step 2150/6000] adopted=7
[step 2200/6000] adopted=7
[step 2250/6000] adopted=7
[step 2300/6000] adopted=7
[step 2350/6000] adopted=7
[step 2400/6000] adopted=9
[step 2450/6000] adopted=9
[step 2500/6000] adopted=9
[step 2550/6000] adopted=11
[step 2600/6000] adopted=11
[step 2650/6000] adopted=11
[step 2700/6000] adopted=11
[step 2750/6000] adopted=11
[step 2800/6000] adopted=11
[step 2850/6000] adopted=11
[step 2900/6000] adopted=13
[step 2950/6000] adopted=13
[step 3000/6000] adopted=13
[step 3050/6000] adopted=13
[step 3100/6000] adopted=14
[step 3150/6000] adopted=15
[step 3200/6000] adopted=15
[step 3250/6000] adopted=15
[step 3300/6000] adopted=15
[step 3350/6000] adopted=16
[step 3400/6000] adopted=17
[step 3450/6000] adopted=17
[step 3500/6000] adopted=17
[step 3550/6000] adopted=17
[step 3600/6000] adopted=17
[step 3650/6000] adopted=17
[step 3700/6000] adopted=19
[step 3750/6000] adopted=19
[step 3800/6000] adopted=19
[step 3850/6000] adopted=20
[step 3900/6000] adopted=22
[step 3950/6000] adopted=22
[step 4000/6000] adopted=22
[step 4050/6000] adopted=24
[step 4100/6000] adopted=24
[step 4150/6000] adopted=24
[step 4200/6000] adopted=25
[step 4250/6000] adopted=27
[step 4300/6000] adopted=27
[step 4350/6000] adopted=28
[step 4400/6000] adopted=29
[step 4450/6000] adopted=29
[step 4500/6000] adopted=30
[step 4550/6000] adopted=30
[step 4600/6000] adopted=30
[step 4650/6000] adopted=30
[step 4700/6000] adopted=30
[step 4750/6000] adopted=30
[step 4800/6000] adopted=31
[step 4850/6000] adopted=31
[step 4900/6000] adopted=31
[step 4950/6000] adopted=32
[step 5000/6000] adopted=33
[step 5050/6000] adopted=33
[step 5100/6000] adopted=34
[step 5150/6000] adopted=34
[step 5200/6000] adopted=34
[step 5250/6000] adopted=35
[step 5300/6000] adopted=35
[step 5350/6000] adopted=37
[step 5400/6000] adopted=37
[step 5450/6000] adopted=37
[step 5500/6000] adopted=38
[step 5550/6000] adopted=38
[step 5600/6000] adopted=38
[step 5650/6000] adopted=38
[step 5700/6000] adopted=38
[step 5750/6000] adopted=38
[step 5800/6000] adopted=38
[step 5850/6000] adopted=38
[step 5900/6000] adopted=38
[step 5950/6000] adopted=38
Done.
(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents>
(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> $py = @"
>> import json, pathlib
>> p = sorted(pathlib.Path('runs').rglob('messages.jsonl'))[-1]
>> prop=adopt=err=0
>> for ln in open(p,'rb'):
>>     rec=json.loads(ln)
>>     t=rec.get('type')
>>     if t=='PROPOSE': prop+=1
>>     elif t=='ADOPT': adopt+=1
>>     elif t=='ERROR': err+=1
>> print(f'LOG: {p} | PROPOSE: {prop} | ADOPT: {adopt} | ERRORS: {err}')
>> "@
>> python -c $py
>>
LOG: runs\demo-20250911-163711\messages.jsonl | PROPOSE: 164 | ADOPT: 39 | ERRORS: 0
(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> python -m src.quick_eval 
log: runs\demo-20250911-163711\messages.jsonl | ADOPT events: 39
Top-5 songs by adoption: [(240, 3), (1, 3), (175, 2), (273, 2), (340, 2)]
Gini(popularity): 0.204
Top-5 cascades (song_id, size): [(240, 3), (175, 3), (1, 3), (273, 3), (340, 3)]
(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> python -m src.metrics_advanced
Log: runs\demo-20250911-163711\messages.jsonl
---- Popularity ----
{'total_adopts': 39, 'unique_songs_adopted': 28, 'top5': [(240, 3), (1, 3), (175, 2), (273, 2), (340, 2)], 'gini': 0.204, 'herfindahl': 0.043, 'lorenz': [(0.0, 0.0), (0.03571428571428571, 0.02564102564102564), (0.07142857142857142, 0.05128205128205128), (0.10714285714285714, 0.07692307692307693), (0.14285714285714285, 0.10256410256410256), (0.17857142857142858, 0.1282051282051282), (0.21428571428571427, 0.15384615384615385), (0.25, 0.1794871794871795), (0.2857142857142857, 0.20512820512820512), (0.32142857142857145, 0.23076923076923078), (0.35714285714285715, 0.2564102564102564), (0.39285714285714285, 0.28205128205128205), (0.42857142857142855, 0.3076923076923077), (0.4642857142857143, 0.3333333333333333), (0.5, 0.358974358974359), (0.5357142857142857, 0.38461538461538464), (0.5714285714285714, 0.41025641025641024), (0.6071428571428571, 0.4358974358974359), (0.6428571428571429, 0.46153846153846156), (0.6785714285714286, 0.48717948717948717), (0.7142857142857143, 0.5384615384615384), (0.75, 0.5897435897435898), (0.7857142857142857, 0.6410256410256411), (0.8214285714285714, 0.6923076923076923), (0.8571428571428571, 0.7435897435897436), (0.8928571428571429, 0.7948717948717948), (0.9285714285714286, 0.8461538461538461), (0.9642857142857143, 0.9230769230769231), (1.0, 1.0)]}
---- Efficiency ----
{'proposes': 164, 'adopts': 39, 'overall_acceptance': 0.238, 'top5_acceptance_songs': [(37, 1.0), (81, 1.0), (137, 1.0), (139, 1.0), (175, 1.0)]}
---- Cascades ----
{'top5_cascades': [(240, 5, 1, 3, 1.25), (1, 5, 1, 3, 1.25), (233, 4, 1, 2, 1.0), (175, 3, 1, 2, 1.333), (273, 3, 1, 2, 1.333)], 'avg_depth': 1, 'avg_virality': 1.089}
---- Reproduction ----
{'R_mean': 0.557, 'R_median': 0.0}
---- Exposure ----
{'mean_exposures': 1, 'median_exposures': 1, 'p95': 1}
(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> $py = @"
>> import json, pathlib
>> p = sorted(pathlib.Path('runs').rglob('messages.jsonl'))[-1]
>> dec=llm=heur=0; examples=[]
>> with open(p,'rb') as f:
>>     for ln in f:
>>         rec=json.loads(ln)
>>         if rec.get('type')=='DECISION':
>>             dec += 1
>>             src = rec.get('source','?')
>>             if src=='llm':
>>                 llm += 1
>>                 if len(examples)<3:
>>                     examples.append({k:rec.get(k) for k in ('step','agent','song_id','targets','explain')})
>>             elif src=='heuristic':
>>                 heur += 1
>> print('Log:', p)
>> print('DECISION total:', dec, '| LLM:', llm, '| Heuristic:', heur)
>> print('LLM examples:', examples)
>> "@
>> python -c $py
Log: runs\demo-20250911-163711\messages.jsonl
DECISION total: 124 | LLM: 124 | Heuristic: 0
LLM examples: [{'step': 72, 'agent': '97', 'song_id': 244, 'targets': ['94'], 'explain': 'highly trusted user recommended this song'}, {'step': 103, 'agent': '123', 'song_id': 174, 'targets': ['121', '120'], 'explain': 'high trust and low load candidates'}, {'step': 132, 'agent': '134', 'song_id': 198, 'targets': ['135', '132'], 'explain': "recommended song for user 198 based on their recent listens and neighbors' trust scores"}]
(.venv) PS C:\Universita\Sistemi_complessi_modelli_e_simulazione\Music_agents> $py = @"
>> import json, pathlib
>> p = sorted(pathlib.Path('runs').rglob('messages.jsonl'))[-1]
>>
>> heur = 0
>> nonheur = 0
>> examples = []
>>
>> with open(p,'rb') as f:
>>     for ln in f:
>>         rec = json.loads(ln)
>>         if rec.get('type') == 'DECISION':
>>             exp = rec.get('explain','')
>>             if exp == 'heuristic':
>>                 heur += 1
>>             else:
>>                 nonheur += 1
>>                 if len(examples) < 16:
>>                     examples.append({
>>                         'step': rec.get('step'),
>>                         'agent': rec.get('agent'),
>>                         'song_id': rec.get('song_id'),
>>                         'explain': exp
>>                     })
>>
>> print('Log file:', p)
>> print('DECISION with explain="heuristic":', heur)
>> print('DECISION with explain != "heuristic":', nonheur)
>> print('Examples of non-heuristic explains:')
>> for e in examples:
>>     print(e)
>> "@
>> python -c $py
Log file: runs\demo-20250911-163711\messages.jsonl
DECISION with explain=heuristic: 0
DECISION with explain != heuristic: 124
Examples of non-heuristic explains:
{'step': 72, 'agent': '97', 'song_id': 244, 'explain': 'highly trusted user recommended this song'}
{'step': 103, 'agent': '123', 'song_id': 174, 'explain': 'high trust and low load candidates'}
{'step': 132, 'agent': '134', 'song_id': 198, 'explain': "recommended song for user 198 based on their recent listens and neighbors' trust scores"}
{'step': 201, 'agent': '164', 'song_id': 83, 'explain': ''}
{'step': 228, 'agent': '0', 'song_id': 137, 'explain': 'high trust and low load candidates'}
{'step': 313, 'agent': '167', 'song_id': 289, 'explain': ''}
{'step': 342, 'agent': '15', 'song_id': 37, 'explain': "recommended song for user 12 based on their recent listens and neighbors' trust scores"}
{'step': 403, 'agent': '64', 'song_id': 25, 'explain': 'high trust and low load candidates'}
{'step': 430, 'agent': '115', 'song_id': 227, 'explain': 'high trust and low load candidates selected'}
{'step': 474, 'agent': '132', 'song_id': 81, 'explain': 'high trust and low load candidates selected'}
{'step': 499, 'agent': '141', 'song_id': 240, 'explain': 'short'}
{'step': 528, 'agent': '155', 'song_id': 126, 'explain': 'high trust and low load candidates selected'}
{'step': 570, 'agent': '159', 'song_id': 246, 'explain': 'recommended song for user 103 and 118 based on their recent listens'}
{'step': 595, 'agent': '169', 'song_id': 143, 'explain': 'short'}
{'step': 618, 'agent': '171', 'song_id': 0, 'explain': 'highly recommended song'}
{'step': 650, 'agent': '17', 'song_id': 291, 'explain': "recommended song for user 276 based on their recent listens and neighbors' trust scores"}