#!/bin/bash

dmesg -n 3
systemctl start pcscd
chmod +x ~/fortis-setup.py
~/fortis-setup.py
