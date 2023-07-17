from flask import Flask
from flask import render_template
import json
import httpx
import time

app = Flask(__name__)

resturl='http://slurm/slurm-restapi/'
resturl='/run/slurmrestd/slurmrestd.socket'
API='slurm/v0.0.38'

if resturl.startswith('http'):
    client = httpx.Client(base_url=resturl+API)
else:
    transport = httpx.HTTPTransport(uds=resturl)
    client = httpx.Client(transport=transport, 
                          base_url='http://localhost/'+API)

def render_dt(t):
    dt = round(t)
    if dt<60*60:
        return f'{dt//60:02d}:{dt%60:02d}'
    elif dt<24*60*60:
        return f'{dt//3600:02d}:{dt//60:02d}'
    else :
        return f'{dt//86400:d}-{(dt%86400)//1440:02d}:{((dt%86400)%1440)//60:02d}'




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
    jobl = {j['job_id']:{
                'name': j['name'],
                'login': j['user_name'],
                'job_state': j['job_state'],
                'run_time_str': render_dt(time.time() - j['start_time']),
                'cpus_allocated': (j['nodes'], j['job_resources']['allocated_cores'])
                                        if 'job_resources' in j else "",
            }
            for j in resp.json()['jobs']}
    return render_template('jobs.html', selected="jobs", data=jobl)

@app.route("/nodes")
def nodes():
    resp = client.get('/nodes')
    if resp.status_code != 200:
        return render_template('error.html', selected="", 
                                endpnt='/nodes', 
                                code=resp.status_code)
    nodes = resp.json()['nodes']
    
    resp = client.get('/jobs')
    if resp.status_code != 200:
        return render_template('error.html', selected="", 
                                endpnt='/jobs', 
                                code=resp.status_code)
    jobs = resp.json()['jobs']

    clrl = ('orange','green','blueviolet','crimson','navy','darkgreen', 'purple', 'seagreen')

    nodel = {n['name']:n for n in nodes}
    jobl = {j["batch_host"]:j for j in jobs}
    jobl_alloc = {}
    colors = {}
    return render_template('nodes.html', selected="nodes", 
                            nodel=nodel, jobl=jobl, colors=colors, 
                            jalloc=jobl_alloc)


    resp = client.get('/jobs-by-nodes')
    jobl = {k:v for k, v in json.loads(resp.text).items() if v}
    resp = client.get('/jobs')
    jobl_byid = json.loads(resp.text)
    clrl = ('orange','green','blueviolet','crimson','navy','darkgreen', 'purple', 'seagreen')
    colors = {jid:clrl[cn % len(clrl)] for cn, jid in enumerate(jobl_byid)}
    jobl_alloc = {i:j for i, j in jobl_byid.items() if 'nodeset' in j and j['nodeset']}
    return render_template('nodes.html', selected="nodes", nodel=nodel, jobl=jobl, colors=colors, jalloc=jobl_alloc)

