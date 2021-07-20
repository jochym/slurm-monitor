from flask import Flask
from flask import render_template
import requests
import json

app = Flask(__name__)

resturl='http://10.0.1.20/slurm-restapi/'

@app.route("/")
def index():
    return render_template('content.html', selected="")


@app.route("/jobs")
def jobs():
    resp = requests.get(resturl+'jobs')
    return render_template('jobs.html', selected="jobs", data=json.loads(resp.text))

@app.route("/nodes")
def nodes():
    resp = requests.get(resturl+'nodes')
    nodel = json.loads(resp.text)
    resp = requests.get(resturl+'jobs-by-nodes')
    jobl = {k:v for k, v in json.loads(resp.text).items() if v}
    resp = requests.get(resturl+'jobs')
    jobl_byid = json.loads(resp.text)
    clrl = ('orange','green','blueviolet','crimson','navy','darkgreen', 'purple', 'seagreen')
    colors = {jid:clrl[cn % len(clrl)] for cn, jid in enumerate(jobl_byid)}
    odd = True
    for n, j in jobl.items():
        for jid, v in j.items():
            v['login']=jobl_byid[jid]['login']
            v['username']=jobl_byid[jid]['username']
            v['row'] = 'odd' if odd else 'even'
            odd = not odd
    return render_template('nodes.html', selected="nodes", nodel=nodel, jobl=jobl, colors=colors)

