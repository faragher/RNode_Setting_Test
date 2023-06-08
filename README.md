# RNode_Setting_Test
Simple test for RNode settings for use in Reticulum

**Usage:**

  Configure Reticulum as required - disable all but tested interface

  Start Receiver.py on receiving machine. Note "Server address: <xxx>" line. This is your address.
  
  Start Sender with "python3 Sender.py xxx" where xxx is the address noted above.
  
  When Sender reports complete, press enter on receiving unit.
  
  
**Notes:**
  * You may need to use "python" instead of "python3" depending on your system
  * The address does not include <>
  * If the "server address" line does not appear, set your Reticulum log level to at least 4
  
