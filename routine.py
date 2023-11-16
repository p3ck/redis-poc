import os
import subprocess
import siphon
import redis
import settings
import rq
import requests
from utils import makedirs_ignore

import logging

logger = logging.getLogger(__name__)

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

#Replace with a decorator for which methods can be queued...
actions = ["provision"]


# Validate against actual LABS
def get_jobs_queue(name: str) -> rq.Queue:
    return rq.Queue(
        name=settings.RQ_QUEUES[name],
        default_timeout=settings.RQ_JOBS_TIMEOUT,
        connection=r,
    )

def fetch_file(url, dest):
    # NOTE the stream=True parameter
    req = requests.get(url, stream=True)
    with open(dest, 'wb') as file:
        for chunk in req.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                file.write(chunk)
                #file.flush() commented by recommendation from J.F.Sebastian

def run(command, timeout=60):
    result = subprocess.run(command, timeout=timeout)

def provision(system, action):
    """
    Provision a host..
      Retrieve Kernel and Ramdisk
      Set Netboot entry
      Power cycle Host
    """
    kernel_rel_path = os.path.join(action["hex_ip"], 'kernel')
    kernel_path = os.path.join(settings.TFTP_ROOT, kernel_rel_path)
    makedirs_ignore(os.path.dirname(kernel_path), mode=0o755)
    logger.debug('Fetching file %s for %s', kernel_url, kernel_path)
    fetch_file(action["kernel_url"], kernel_path)

    initrd_rel_path = os.path.join(action["hex_ip"], 'initrd')
    initrd_path = os.path.join(settings.TFTP_ROOT, initrd_rel_path)
    makedirs_ignore(os.path.dirname(initrd_path), mode=0o755)
    logger.debug('Fetching file %s for %s', initrd_url, initrd_path)
    fetch_file(action["initrd_url"], initrd_path)

    values = dict(hex_ip = action["hex_ip"],
                  kernel_path = kernel_rel_path,
                  initrd_path = initrd_rel_path,
                  kernel_options = action.get("kernel_options", '')
    r.hset("netboot:%s" % values["hex_ip"], mapping=values)
    r.expire("netboot:%s" % values["hex_ip"], 3600)
