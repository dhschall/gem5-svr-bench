
set -x -e

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
ARCH=$(dpkg --print-architecture)

PACKER_VERSION="1.11.2"

if [ ! -f ./packer ]; then
    wget https://releases.hashicorp.com/packer/${PACKER_VERSION}/packer_${PACKER_VERSION}_linux_${ARCH}.zip;
    unzip packer_${PACKER_VERSION}_linux_${ARCH}.zip;
    rm packer_${PACKER_VERSION}_linux_${ARCH}.zip;
fi



if [ $ARCH == "arm64" ]; then
    make -f $SCRIPTPATH/arm.Makefile build-wkdir
    make -f $SCRIPTPATH/arm.Makefile run-$ARCH 1> qemu.log 2>&1 &
    # Store the configuration file name from the command line argument
config_file=$SCRIPTPATH/packer-scripts/benchmarks_arm.pkr.hcl
else
    make -f $SCRIPTPATH/Makefile build-wkdir
    make -f $SCRIPTPATH/Makefile run-$ARCH 1> qemu.log 2>&1 &
    # Store the configuration file name from the command line argument
    config_file=$SCRIPTPATH/packer-scripts/benchmarks.pkr.hcl   
fi

QEMU_PID=$!
echo "QEMU PID: $QEMU_PID"





# Wait for the QEMU process to finish
sleep 1s


# Check if the specified configuration file exists
if [ -f "$config_file" ]; then
    # Install the needed plugins
    ./packer init "$config_file"
    # Build the image
    ./packer build "$config_file" 1> packer.log 2>&1
else
    echo "Error: Configuration file '$config_file' not found."
    exit 1
fi


# Wait for the QEMU process to finish
wait $QEMU_PID
# sleep 2s