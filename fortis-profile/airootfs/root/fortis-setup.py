#!/usr/bin/env python3

import signal
from FortisCardTUI import FortisCardTUI

# Disable Ctrl+C
signal.signal(signal.SIGINT, signal.SIG_IGN)


if __name__ == '__main__':
    fortis = FortisCardTUI()
    fortis.loop.run()
