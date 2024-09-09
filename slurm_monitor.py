from flask import Flask
from flask import render_template
import httpx
import time
from collections import defaultdict

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

resturl='http://slurm/slurm-restapi/'
resturl='/run/slurmrestd/slurmrestd.socket'
API='slurm/v0.0.38'

alloc_states = {'RUNNING', 'CONFIGURING', 'COMPLETED'}
run_states = {'RUNNING', 'CONFIGURING'}

if resturl.startswith('http'):
    client = httpx.Client(base_url=resturl+API)
else:
    transport = httpx.HTTPTransport(uds=resturl)
    client = httpx.Client(transport=transport, 
                          base_url='http://localhost/'+API)

def render_dt(j):
    t = time.time()
    if t > j['end_time']:
        t = j['end_time']
    dt = round(t - j['start_time'])
    if dt <= 0:
        return '0:00'
    if dt<60*60:
        return f'{dt//60:02d}:{dt%60:02d}'
    elif dt<24*60*60:
        return f'{dt//3600:02d}:{dt//60:02d}'
    else :
        return f'{dt//86400:d}-{(dt%86400)//1440:02d}:{((dt%86400)%1440)//60:02d}'


def fill_jobs_dict(jobs, alloc=False):
    return {j['job_id']:{
                'name': j['name'],
                'login': j['user_name'],
                'job_state': j['job_state'],
                'cpus_requested' : (j['node_count'], j['cpus']),
                'run_time_str': render_dt(j) if j['job_state'] in alloc_states else "",
                'cpus_allocated': (j['nodes'], j['job_resources']['allocated_cores'])
                                        if 'job_resources' in j else "",
                'allocations': {a['nodename']:{(int(s), int(c)) for s, cs in a['sockets'].items() for c in cs['cores']}
                                    for a in j['job_resources']['allocated_nodes']} if 'job_resources' in j else {}
            }
            for j in jobs if not alloc or  j['job_state'] in alloc_states}

@app.route("/")
def index():
    return render_template('content.html', selected="")


@app.route("/jobs")
def jobs():
    resp = client.get('/jobs')
    if resp.status_code != 200:
        return render_template('error.html', selected="", 
                                endpnt='/jobs', 
                                code=resp.status_code)
    jobl = fill_jobs_dict(resp.json()['jobs'])
    return render_template('jobs.html', selected="jobs", data=jobl)

@app.route("/nodes")
def nodes():
    resp = client.get('/nodes')
    if resp.status_code != 200:
        return render_template('error.html', selected="", 
                                endpnt='/nodes', 
                                code=resp.status_code)

    nodes = {n['name']:n for n in resp.json()['nodes']}
    for nid, n in nodes.items():
        if n['state'] in {'idle', 'allocated', 'mixed'}:
            n['load'] = n['cpu_load']/n['cpus']
        else:
            n['load'] = 0

        if n['load'] > 110 :
            n['load'] = 0
    
    resp = client.get('/jobs')
    if resp.status_code != 200:
        return render_template('error.html', selected="", 
                                endpnt='/jobs', 
                                code=resp.status_code)
    
    jobs = fill_jobs_dict(resp.json()['jobs'], alloc=True)

    clrl = ('orange','green','blueviolet','crimson','navy','darkgreen', 'purple', 'seagreen')
    colors = {jid:clrl[cn % len(clrl)] for cn, jid in enumerate(jobs)}

    assoc = defaultdict(dict)
    for jid, j in jobs.items():
        if j['job_state'] not in run_states:
            continue
        for n, a in j['allocations'].items():
            for sc in a:
                assoc[n][sc]=jid

    # for n in sorted(assoc):
    #     print(assoc[n])
    # print('Allocated jobs:', list(jobl))
    # for jid, j in jobl.items():
    #     print(jid, j['job_state'], j['allocations'])

    return render_template('nodes.html', selected="nodes", nodes=nodes, 
                            jobs=jobs, colors=colors, assoc=assoc)
