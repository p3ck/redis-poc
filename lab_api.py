import flask
import json
import redis
from jinja2 import Environment, FileSystemLoader, select_autoescape
import settings
from utils import decode_values


app = flask.Flask(__name__)
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

@app.route("/netboots", methods=["GET"])
def get_all_netboots():
    netboots = [v.decode('utf-8') for v in r.scan_iter('netboot:*')]
    nb_netboots = len(netboots)
    return flask.jsonify({"netboots": netboots, "_meta": {"count": nb_netboots}})

def render_template(template_file, metadata):
    jinja_env = Environment(
            loader=FileSystemLoader(settings.TEMPLATE_DIR),
            autoescape=select_autoescape(),
            )
    template = jinja_env.get_template(template_file)
    rendered = template.render(**metadata)
    return rendered

def clear_netboot(values):
    r.expire("netboot:%s" % values["hex_ip"], 10)

@app.route("/netboots/<hex_ip>/pxe", methods=["GET"])
def netboot_pxe(hex_ip):
    template = "pxe_default.j2"
    netboot_values = decode_values(r.hgetall("netboot:%s" % hex_ip))
    if netboot_values:
        clear_netboot(netboot_values)
        template = "pxe_boot.j2"
    return render_template(template, netboot_values)

@app.route("/netboots/<hex_ip>/grub2", methods=["GET"])
def netboot_grub2(hex_ip):
    template = "grub2_default.j2"
    netboot_values = decode_values(r.hgetall("netboot:%s" % hex_ip))
    if netboot_values:
        clear_netboot(netboot_values)
        template = "grub2_boot.j2"
    return render_template(template, netboot_values)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.LAB_PORT, debug=True)

