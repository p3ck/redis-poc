import flask
import json
import redis
from jinja2 import Environment, FileSystemLoader, select_autoescape
import settings
import routine
import socket
from utils import decode_values


app = flask.Flask(__name__)
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def pxe_basename(fqdn):
    # pxelinux uses upper-case hex IP address for config filename
    ipaddr = socket.gethostbyname(fqdn)
    return '%02X%02X%02X%02X' % tuple(int(octet) for octet in ipaddr.split('.'))

@app.route("/systems", methods=["GET"])
def systems_list():
    systems = [v.decode('utf-8') for v in r.scan_iter('system:*')]
    nb_systems = len(systems)
    return flask.jsonify({"systems": systems, "_meta": {"count": nb_systems}})

@app.route("/systems/<fqdn>", methods=["GET"])
def system(fqdn):
    k_v = decode_values(r.hgetall("system:%s" % fqdn))
    if len(k_v) == 0:
        return flask.Response(
            json.dumps(
                {
                    "message": f"{fqdn} system does not exist. Please query GET /systems."
                }
            ),
            status=404,
            content_type="application/json",
        )
    else:
        return flask.jsonify({fqdn: k_v})

@app.route("/systems/<fqdn>", methods=["POST"])
def system_create(fqdn):
    k_v = decode_values(r.hgetall("system:%s" % fqdn))
    if len(k_v) == 0:
        values = flask.request.json
        r.hset("system:%s" % fqdn, mapping=values)
        return flask.Response(
            json.dumps(
                {
                    "status": "OK",
                    "message": f"{fqdn} system has been created.",
                }
            ),
            status=201,
            content_type="application/json",
        )
    else:
        return flask.Response(
            json.dumps(
                {
                    "message": f"{fqdn} system already exists."
                }
            ),
            status=409,
            content_type="application/json",
        )

@app.route("/systems/<fqdn>/actions", methods=["POST"])
def system_actions(fqdn):
    k_v = decode_values(r.hgetall("system:%s" % fqdn))
    if len(k_v) == 0:
        return flask.Response(
            json.dumps(
                {
                    "message": f"{fqdn} system does not exist. Please query GET /systems."
                }
            ),
            status=404,
            content_type="application/json",
        )
    else:
        values = flask.request.json
        action = values.pop("action", None)

        values['hex_ip'] = pxe_basename(fqdn)

        action_args = dict(system = k_v, action = values)

        if action in routine.actions:
            job = routine.get_jobs_queue(k_v["lab"]).enqueue(
                    getattr(routine, action), kwargs=action_args
                    )
            print("job=%s" % job)
            print("dir=%s" % dir(job))
            return flask.Response(
                    json.dumps(
                        {
                            "status": "OK",
                            "message": f"Action for {fqdn} has been started.",
                            "job": "job",
                        }
                    ),
                    status=201,
                    content_type="application/json",
            )
        else:
            return flask.Response(
                    json.dumps(
                        {
                            "message": f"Missing or invalid action. Please query GET /systems/{fqdn}/actions."
                        }
                    ),
                    status=404,
                    content_type="application/json",
                    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.BACKEND_PORT, debug=True)

