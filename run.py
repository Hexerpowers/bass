import time
import sys
import configparser as cfp

from modules.Detect import Detect

start_time = time.time()

print("[bass] Starting...")

config = cfp.ConfigParser()
config.read("config/bass.cfg")
detect = Detect(config).start()

print('[bass] Init finished;')

print('[bass] Waiting for connection on '+config["vidgear"]["host"]+":"+config["vidgear"]["port"]+"...")

if bool(int(config["bass"]["use_timecodes"])):
    print("--- took %s seconds ---" % (time.time() - start_time))
    print()
detect.enable()
