import sys
import time
import configparser as cfp

from modules.Service import Service
from modules.StreamWriter import StreamWriter


start_time = time.time()
config = cfp.ConfigParser()
config.read("config/bass.cfg")
service = Service(config).check_config()
service.print_log("Bass", 0, "Starting...")
stream = StreamWriter(service).start()

if bool(int(config["bass"]["use_timecodes"])):
    service.print_log("Bass", 2, "--- took %s seconds ---" % (time.time() - start_time))
    print()
