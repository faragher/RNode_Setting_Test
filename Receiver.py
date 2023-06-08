##########################################################
# Based on Announce.py and Echo.py                       #
# Rnode Setting Test receiver                            #
# github.com/faragher/RNode_Setting_Test/                #
##########################################################

import argparse
import random
import RNS

APP_NAME = "setting_test"
rcd_packets = 0
rcd_announce = 0

# This initialisation is executed when the program is started
def program_setup(configpath):
    reticulum = RNS.Reticulum(configpath)
    identity = RNS.Identity()

    destination_1 = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "GP"
    )
    RNS.log(
        "Server addess: "+
        RNS.prettyhexrep(destination_1.hash)
    )

    announce_handler = ExampleAnnounceHandler(
         aspect_filter=None
    )

    # We register the announce handler with Reticulum
    RNS.Transport.register_announce_handler(announce_handler)
    destination_1.set_packet_callback(server_callback)
    # Everything's ready!
    # Let's hand over control to the announce loop
    announceLoop()


def announceLoop():
    global rcd_packets
    global rcd_announce
    print("Setting test receiver: Expects 10 trials.")
    print("Waiting for data. (Enter to end test, Ctrl-C to abort)")

    entered = input()
    print("Recieved "+str(rcd_announce)+" announces. "+str(((10-rcd_announce)/10)*100)+"% lost")
    print("Recieved "+str(rcd_packets)+" packets. "+str(((10-rcd_packets)/10)*100)+"% lost")


class ExampleAnnounceHandler:
    def __init__(self, aspect_filter=None):
        self.aspect_filter = aspect_filter

    def received_announce(self, destination_hash, announced_identity, app_data):
        global rcd_announce

        if app_data:
            rcd_announce = rcd_announce + 1
            print(
                "Received announce "+
                app_data.decode("utf-8")
            )

def server_callback(message, packet):
    global rcd_packets
    rcd_packets = rcd_packets + 1

    print("Received packet "+message.decode("utf-8"))

##########################################################
#### Program Startup #####################################
##########################################################

# This part of the program gets run at startup,
# and parses input from the user, and then starts
# the desired program mode.
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            description="Reticulum setting test receiver. Expects 10 announces and packets from a single source."
        )

        parser.add_argument(
            "--config",
            action="store",
            default=None,
            help="path to alternative Reticulum config directory",
            type=str
        )

        args = parser.parse_args()

        if args.config:
            configarg = args.config
        else:
            configarg = None

        program_setup(configarg)

    except KeyboardInterrupt:
        print("")
        exit()
