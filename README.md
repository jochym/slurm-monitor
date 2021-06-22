# slurm-monitor
Web monitor for the slurm cluster. This project is born out of the frustration with brittleness and complication of slurm-web project which looks nice and when it works is very useful but it is enough to look at it the wrong way for it to brake. 

So I decided to build simpler solution for my cluster. I have used [HTMX](http://htmx.org/) to build active parts (without single javascript line), Flask and jinja for application server and slurm-web's slurm rest api server. The final product is highly specific to my environment - especially the nodes display template and logic. But it is very easy to adapt to different circumstances.

In the future I intend to make it configurable and cut the dependence from pyslurm/slurm-web restapi server - probably by moving to the new api service included in the newer slurm releases. 

Beware - this is a weekend hack project. I got it working in literal 12 hours, so it is not polished, documented etc. But, I believe you can adapt it to your own cluster (if you have slurm-web restapi server running) by simply modifying nodes.html and node.html templates to fit your setup. I would welcome contributions: particularly some replacement for the restapi server/pyslurm and configuration system.

## Installation

You need to install it from source for now. I know this is suboptimal. It is a standard Flask app you. You need Flask, Jinja, requests and pyjason in your venv. Otherwise, just follow standard Flask install docs.

## Configuration

As a minimum you will need to change restapi server URL in `app.py` and probably modify `templates/nodes.html` and `templates/node.html` to fit your setup.