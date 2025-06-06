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

### Build base disk image

To create a fresh base image with docker and all gem5 tools installed use the `build-<x86/arm>.sh` script in the image folder. This step has done only once and the same base disk image can be used for different workloads.

> [!TIP]
> The building process from the base disk image is inherited from [gem5-resources](https://github.com/gem5/gem5-resources). For further details refer to the build [README](./image/README.md) and the gem5-resources [documentation](https://github.com/gem5/gem5-resources/blob/stable/src/ubuntu-generic-diskimages/BUILDING.md).

Use the corresponding script to build the x86 or Arm disk image. 
**Note** that the arm building process assumes you run on an arm machineas and use kvm. See the [README](./image/README.md#disk-image) for details to run without kvm.

```bash
# Build the disk image for x86 Ubuntu 22.04
cd image
sudo ./build-x86.sh 22.04   
cd ..

# Building the disk image for arm Ubuntu 24.04 (22.04 not supported)
cd image
sudo ./build-arm.sh 24.04   
cd ..
```

Depending on the type of machine the building process can take a while (x86 ~10min, arm ~30min). Once completed the new base image will be placed in the `x86-disk-image-22-04 / arm-disk-image-24-04` directory.


### Install the benchmarks on the disks

The base image has only docker installed and all necessary tools. However, the docker images for the benchmarks are not pulled which needs to be done outside of gem5.

Run the install script to automatically install the benchmarks onto the disk image.
```bash

./image/install.sh
```
The script will create a new working directory `wkdir` and copy all files needed for the gem5 simulation needed (disk-image, kernel, http-client) into it.
Afterwards the disk is booted with QEMU and the benchmarks installed onto the disk


### Booting the disk image in QEMU

To modify the disk image and add content manually create first the working directory with:
```
make -f image/Makefile build-wkdir 
```
Then boot the image with
```
make -f image/Makefile run-<x86/arm> 
```
Finally, for debugging purposes, you can use another terminal login via ssh using port 8888.
```
ssh gem5@localhost -p 8888
```



## Gem5 simulation

## Boot benchmark and take snapshot

Before we can start simulating the actual benchmark (1) linux has to be booted, (2) the docker image has to be started and (3) the benchmarks JIT engine -- very common for server applications -- has to be warmed up.
The KVM accelerated core is used to perform all three steps after which a checkpoint is taken.
> Note KVM can only be used if the host ISA is the same as the simulated system.

### Automated setup
To generate all checkpoints, consider the `scripts/setup-all.sh` script:

```bash
# Edit the GEM5 variable at the top to point to a valid GEM5 binary
vim ./scripts/setup-all.sh
# Execute the script
bash ./scripts/setup-all.sh
```

This will take 5-10 minutes. The output can be inspected in the following ways: 
- See the process state with `pueue status` (running / failed ...)
- View the gem5 log (`gem5.log`) or the Linux output (`board.terminal`) in the `results/<arch>/setup/*` output directories


## Simulation

After the checkpoints were taken, the simulation can be executed via the `scripts/run-all.sh` script:

```bash
# Edit the GEM5 variable at the top to point to a valid GEM5 binary
# Adjust the other variables to select benchmarks and the architecture
vim ./scripts/run-all.sh
# Start the simulation, giving it a label to identify the experiment later
bash ./scripts/run-all.sh <SCENARIO_NAME>
```

Similar to the setup process, the output can be observed in the `results/<arch>/<SCENARIO_NAME>/*` folders

