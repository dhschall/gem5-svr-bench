
set -x -e

sudo apt update

# Install qemu and others
sudo apt install -y \
        qemu-kvm libvirt-clients libvirt-daemon-system bridge-utils virtinst libvirt-daemon pigz \
        pip

pip install numpy matplotlib tqdm

# Check system architecture

ARCH="amd64"

if [ $(uname -m) == "aarch64" ]; then
        ARCH="arm64"
fi

# Install go

wget https://go.dev/dl/go1.23.3.linux-$ARCH.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.23.3.linux-$ARCH.tar.gz
rm go1.23.3.linux-$ARCH.tar.gz
export PATH=$PATH:/usr/local/go/bin
echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc

go version