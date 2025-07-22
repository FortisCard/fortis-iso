#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="fortis-iso"
iso_label="FORTIS"
iso_publisher="Fortis <https://www.fortis-card.com>"
iso_application="Fortis Card Setup Environment"
iso_version="1.0.0"
install_dir="arch"
buildmodes=('iso')
bootmodes=('bios.syslinux.mbr' 'bios.syslinux.eltorito'
           'uefi-x64.systemd-boot.esp' 'uefi-x64.systemd-boot.eltorito')
arch="x86_64"
pacman_conf="pacman.conf"
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
)
