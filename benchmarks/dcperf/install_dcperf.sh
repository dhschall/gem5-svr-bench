#!/bin/bash

## Install the DCPerf dependencies
sudo apt update && sudo apt -y -o Dpkg::Options::="--force-confold" upgrade
sudo apt install -y python3-pip git lshw bc dmidecode
sudo pip3 install click pyyaml tabulate pandas
sudo apt install linux-tools-common linux-tools-generic linux-cloud-tools-generic numactl -y
sudo apt install linux-tools-5.15.0-122-generic linux-cloud-tools-5.15.0-122-generic -y

#!/bin/bash

for file in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
  echo performance > $file
done

sudo bash -c 'echo kernel.nmi_watchdog=0 >> /etc/sysctl.conf'
sudo bash -c 'echo -1 > /proc/sys/kernel/perf_event_paranoid'
sudo bash -c 'echo 0 > /proc/sys/kernel/nmi_watchdog'
sudo bash -c 'echo off > /sys/devices/system/cpu/smt/control'

VERSION=v0.2.0

# For TaoBench:
python3 -m pip install numpy==1.26.4

git clone https://github.com/facebookresearch/DCPerf.git
cd DCPerf
git checkout $VERSION
git apply ../dcperf.patch

# Install perfspect

wget https://github.com/intel/PerfSpect/releases/download/v1.5.0/perfspect.tgz
tar -xvzf perfspect.tgz

## List available benchmarks
./benchpress_cli.py list

# Install the benchmarks
df / -h
./benchpress_cli.py install tao_bench_autoscale
df / -h
./benchpress_cli.py install feedsim_autoscale
./benchpress_cli.py install django_workload_default

# Install HHVM for mediawiki

cd ..
df / -h
wget https://github.com/facebookresearch/DCPerf/releases/download/hhvm/hhvm-3.30-multplatform-binary-ubuntu.tar.xz
tar -Jxf hhvm-3.30-multplatform-binary-ubuntu.tar.xz
cd hhvm
sudo ./pour-hhvm.sh
export LD_LIBRARY_PATH="/opt/local/hhvm-3.30/lib:$LD_LIBRARY_PATH"

# Install mediawiki
cd ../DCPerf
./benchpress_cli.py install oss_performance_mediawiki_mlp