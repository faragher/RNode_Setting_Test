##########################################################
# Based on Announce.py and Echo.py                       #
# Rnode Setting Test Sender                              #
# github.com/faragher/RNode_Setting_Test/                #
##########################################################

import argparse
import RNS
from time import sleep

APP_NAME = "setting_test"
tests_sent = 0

def client(destination_hexhash, configpath, timeout=None):
    global reticulum
    global tests_sent

    duty_cycle = 0.25 #There are legal ramifications to this line.
    # Refer to https://www.ti.com/lit/an/swra048/swra048.pdf for
    # first order advice. 25% is not warranted to be legal in
    # any jurisdiction

    # These variables are overwritten, and are only failsafes
    packet_delay = 1
    announce_delay = 1
    path_delay = 5
    baud = 500
    RNodeInt = None
    print("")
    print("=============================================================")
    print("Ensure current Reticulum settings are prepared for your test.")
    print("In particular, ensure autointerface is disabled .")
    print("=============================================================")
    print("")

    # We need a binary representation of the destination
    # hash that was entered on the command line
    try:
        dest_len = (RNS.Reticulum.TRUNCATED_HASHLENGTH//8)*2
        if len(destination_hexhash) != dest_len:
            raise ValueError(
                "Destination length is invalid, must be {hex} hexadecimal characters ({byte} bytes).".format(hex=dest_len, byte=dest_len//2)
            )

        destination_hash = bytes.fromhex(destination_hexhash)
    except Exception as e:
        RNS.log("Invalid destination entered. Check your input!")
        RNS.log(str(e)+"\n")
        exit()
    identity = RNS.Identity()
    
    reticulum = RNS.Reticulum(configpath)
    destination_1 = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "GP"
    )

    for I in RNS.Transport.interfaces:
        if "RNode" in I.name:
            RNS.log("Found RNode interface: "+I.name)
            if RNodeInt != None:
                RNS.log("WARNING: Multiple RNodes detected. Replacing old interface.")
            RNodeInt = I

    if RNodeInt == None:
        RNS.Log("No RNode found. Terminating.")
        exit()

    RNS.log("  BW: "+str(RNodeInt.bandwidth))
    RNS.log("  SF: "+str(RNodeInt.sf))
    RNS.log("  CR: "+str(RNodeInt.cr))
    baud = RNodeInt.bitrate
    RNS.log("  BitRate: "+str(baud))
    packet_delay = ((20 * 8) / (baud * duty_cycle))
    announce_delay = ((168*8) / (baud * duty_cycle))
    path_delay = ((51*8) / (baud * duty_cycle)) + 10
    RNS.log("Packet delay: "+str(packet_delay))
    RNS.log("Announce delay: "+str(announce_delay))
    RNS.log("Path delay: "+str(path_delay))
    total_time = (10 * packet_delay)+(10*announce_delay)+path_delay
    print("----------------------------------------")
    RNS.log("Estimated task time: "+str(total_time)+" S")



    RNS.log(
        "Beginning test - sending to "+
        destination_hexhash+
        " (Ctrl-C to abort)"
    )

    while tests_sent < 10:
        sleep(1)
        if RNS.Transport.has_path(destination_hash):
            server_identity = RNS.Identity.recall(destination_hash)

            request_destination = RNS.Destination(
                server_identity,
                RNS.Destination.OUT,
                RNS.Destination.SINGLE,
                APP_NAME,
                "GP"
            )

            tests_sent = tests_sent + 1
            echo_request = RNS.Packet(request_destination, str(tests_sent).encode("utf-8"))

            packet_receipt = echo_request.send()
            RNS.log("Sent packet "+str(tests_sent)+" to "+RNS.prettyhexrep(request_destination.hash))
            sleep(packet_delay)
            destination_1.announce(str(tests_sent).encode("utf-8"))
            RNS.log("Sent Announce "+str(tests_sent))
            sleep(announce_delay)
        else:
            RNS.log("Destination is not yet known. Requesting path...")
            RNS.Transport.request_path(destination_hash)
            sleep(path_delay)
    RNS.log("Task complete. Shutting down.")


##########################################################
#### Program Startup #####################################
##########################################################

# This part of the program gets run at startup,
# and parses input from the user, and then starts
# the desired program mode.
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Simple echo server and client utility")

        parser.add_argument("--config",
            action="store",
            default=None,
            help="path to alternative Reticulum config directory",
            type=str
        )

        parser.add_argument(
            "destination",
            nargs="?",
            default=None,
            help="hexadecimal hash of the server destination",
            type=str
        )

        args = parser.parse_args()

        if args.config:
            configarg = args.config
        else:
            configarg = None

        if (args.destination == None):
            print("")
            parser.print_help()
            print("")
        else:
            client(args.destination, configarg)
    except KeyboardInterrupt:
        print("")
        exit()
