from pymavlink import mavutil
import configparser as cfp

config = cfp.ConfigParser()
config.read("config/bass.cfg")

the_connection = mavutil.mavlink_connection("udpin:" + config["mavlink"]["address"] + ":" + config["mavlink"]["port"],
                                            dialect='common')
while True:
    msg = the_connection.recv_match(blocking=True)
    print(msg)
