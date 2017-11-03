# minidx3

Bought a minidx3 card reader. Pretty nice reader - cheap, tiny, and battery powered.

Sadly, the software is Windows only and made by a sketchy company based in China...
I refuse to run it on anything but a VM with no network...as it opens network connections...for seemingly unknwon reasons...
I'm also a pretty paranoid person...so it might be nothing...

So I reversed engineered the USB HID protocol it uses and created a partially implemented python library that does the following:

  Logs into the device.
  Logs out of the device.
  Get the number of entries in the device.
  Get an entry in the device.
  Get product version of the device.
  Get firmware date of the device.
  Get any sort of register of the device (maybe?)

This hasn't been REALLY looked at in a LONG time...over a year...so this is more for developers that are looking for a place to start.

Uses the hid python library.

I'd be happy to answer questions...this was more for fun than anything else.
