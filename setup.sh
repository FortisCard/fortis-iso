#!/bin/bash

# NOTE: This script is to be run inside the docker container. Do not run this directly.
cd /home/builduser
sudo pacman-key --init
sudo archlinux-java set java-11-openjdk

# Array of AUR packages to install
aur_packages=(
  "globalplatformpro"
  "python-mnemonic"
  "bip39-generator-git"
)

# Function to build an AUR package
build_aur_package() {
  local package=$1
  git clone "https://aur.archlinux.org/${package}.git"
  cd "${package}"
  makepkg -si --noconfirm
  mv *.pkg.tar.zst ../custompkgs
  cd ..
  rm -rf "${package}"
}

# build loop
mkdir -p custompkgs
for package in "${aur_packages[@]}"; do
  echo "Building $package from AUR..."
  build_aur_package "$package"
done

# Create repository database
repo-add custompkgs/custom.db.tar.gz custompkgs/*.pkg.tar.zst
ln -s custompkgs/custom.db.tar.gz custompkgs/custom.db

echo "All AUR packages have been built and added to the custom repository."

# Build the fortis-java-card-applet CAP file
pushd /home/builduser/fortis-java-card-applet
pushd lib/JCMathLib
python3 package.py -c SecP256k1 -p 'com.fortis' -o ../../src/com/fortis/jcmathlib.java
popd
ant
cp build/fortis-1.0.0.cap /home/builduser/fortis-profile/airootfs/root/
popd

# Build the ISO
mkdir -p fortis-iso-workdir
sudo mkarchiso -v -w fortis-iso-workdir -o build fortis-profile

echo "ISO build complete. Check the 'build' directory for the output."
