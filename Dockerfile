# Start from the latest Arch Linux image
FROM archlinux:latest

# Update the system and install necessary packages
RUN pacman -Syu --noconfirm && \
    pacman -S --needed --noconfirm base-devel git sudo grub jdk11-openjdk python archiso

# Create build user
RUN useradd builduser -m && \
    passwd -d builduser && \
    echo 'builduser ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Copy the setup script and custom profile
COPY setup.sh /home/builduser/
COPY fortis-profile /home/builduser/fortis-profile/

# Set ownership
RUN chown -R builduser:builduser /home/builduser

# Switch to build user
USER builduser
WORKDIR /home/builduser

# Run the setup script
CMD ["bash", "setup.sh"]
