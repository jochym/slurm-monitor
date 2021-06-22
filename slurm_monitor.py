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
    jobl = json.loads(resp.text)
    resp = requests.get(resturl+'jobs')
    clrl = ('orange','green','blueviolet','crimson','navy','darkgreen', 'purple', 'seagreen')
    colors = {jid:clrl[cn % len(clrl)] for cn, jid in enumerate(json.loads(resp.text))}
    return render_template('nodes.html', selected="nodes", nodel=nodel, jobl=jobl, colors=colors)

