import time
import configparser as cfp
from modules.Detect import Detect

start_time = time.time()

config = cfp.ConfigParser()
config.read("config/bass.cfg")
detect = Detect(config).start()

print('Init finished')

if bool(int(config["bass"]["use_timecodes"])):
    print("--- took %s seconds ---" % (time.time() - start_time))
    print()
detect.enable()
