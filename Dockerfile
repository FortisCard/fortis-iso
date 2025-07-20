# Start from the latest Arch Linux image
FROM archlinux:latest

# Update the system and install necessary packages
RUN pacman -Syu --noconfirm && \
    pacman -S --needed --noconfirm base-devel git sudo grub jdk11-openjdk java-runtime-common ant python archiso

# Create build user
RUN useradd builduser -m && \
    passwd -d builduser && \
    echo 'builduser ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Copy the setup script, custom profile, and fortis-java-card-applet source code
COPY setup.sh /home/builduser/
COPY fortis-profile /home/builduser/fortis-profile/
COPY lib/fortis-java-card-applet /home/builduser/fortis-java-card-applet/

# Set ownership
RUN chown -R builduser:builduser /home/builduser

# Switch to build user
USER builduser
WORKDIR /home/builduser

# Run the setup script
CMD ["bash", "setup.sh"]
