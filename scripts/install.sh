
set -x -e

sudo apt update

# Install qemu and others
sudo apt install -y \
        qemu-kvm libvirt-clients libvirt-daemon-system bridge-utils virtinst libvirt-daemon \
        pip


# Install go

pip install numpy matplotlib

wget https://go.dev/dl/go1.23.3.linux-amd64.tar.gz

sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.23.3.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc

go version