# gem5 Server Benchmarks

This repo contains various server and data center workloads runnable in gem5 full-sytem mode

> [!IMPORTANT]
> This repo is in development phase. Please raise issues or propose PR if you encounter problems. We appreciate any feedback.






## Prerequisites

Use the `install.sh` to install qemu along with other packages needed to build the disk image for gem5.

```bash
./scripts/install.sh
```



## Prepare the benchmark disk image

### Build base disk image (x86)

To create a fresh base image with docker and all gem5 tools installed use the `build-<x86/arm>.sh` script in the image folder. This step has done only once and the same base disk image can be used for different workloads.

> [!TIP]
> The building process from the base disk image is inherited from [gem5-resources](https://github.com/gem5/gem5-resources). For further details refer to the build [README](./image/BUILDING.md).

Use the corresponding script to build the x86 or Arm disk image. Note as the build process uses KVM you need to be on a Arm machine to build the arm disk image.

```bash
cd image
# Build the disk image for x86 Ubuntu 22.04
sudo ./build-x86.sh 22.04   
cd ..
```

The build process should take less than 10 min after which the new base image will be placed in the `x86-disk-image-22-04` directory.

### Build base disk image (ARM)

We pull the base disk image from the vSwarm-u repository. We only pull the image once, and we can then use it for all benchmarks. The image is downloaaded in parts and then merged, and the process can take a while. Use the following command to download the image:

```bash
cd gem5-svr-bench
# Download the base disk image for ARM
python3 image/scripts/arm_artifacts.py
```

The image will be stored in the base gem5-svr-bench directory.

### Install the benchmarks on the disks

The base image has only docker installed and all necessary tools. However, the docker images for the benchmarks are not pulled which needs to be done outside of gem5.

Run the install script to automatically install the benchmarks onto the disk image.
```bash

./image/install.sh
```
The script will create a new working directory `wkdir` and copy all files needed for the gem5 simulation needed (disk-image, kernel, http-client) into it.
Afterwards the disk is booted with QEMU and the benchmarks installed onto the disk. QEMU might give errors when booting ARM, or stall, and you can check the `qemu.log` file for this, and just re-running the install script should fix the issue.

### Booting the disk image in QEMU

To modify the disk image and add content manually create first the working directory with:
```
make -f image/Makefile build-wkdir 
```
Then boot the image with
```
make -f image/Makefile run-<x86/arm> 
```
Finally, for debugging purposes, you can use another terminal login via ssh using port 5555.
```
ssh gem5@localhost -p 5555
```

**NOTE: The username as well as password for the ARM image is `root` and for the x86 image it is `gem5`.

## Gem5 simulation

## Boot benchmark and take snapshot

Before we can start simulating the actual benchmark (1) linux has to be booted, (2) the docker image has to be started and (3) the benchmarks JIT engine -- very common for server applications -- has to be warmed up.
The KVM accelerated core is used to perform all three steps after which a checkpoint is taken.
> Note KVM can only be used if the host ISA is the same as the simulated system.

### On x86
```bash
# Simulate
./<path/to/gem5>/build/X86/gem5.opt gem5-configs/x86-simple.py --kernel wkdir/kernel --disk wkdir/disk.img --mode=setup 
```


### On Arm ISA

```bash
# Start the setup phase with gem5 and take a checkpoint
./<path/to/gem5>/build/ARM/gem5.opt gem5-configs/arm-simple.py --kernel wkdir/kernel --disk wkdir/disk.img --mode=setup
```
This will take 5-10 minutes. The progress can be inspected via the `m5term` terminal or the redirected `board.terminal` log in the output directory.


## Simulation

Once the setup step has been performed and the checkpoint is taken simulations can be performed by invoking the same script with the `--mode=eval` parameter.

### On Arm
```bash
# Simulate
./<path/to/gem5>/build/ARM/gem5.opt gem5-configs/arm-simple.py --kernel wkdir/kernel --disk wkdir/disk.img --mode=eval
```
