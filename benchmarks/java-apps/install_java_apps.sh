#!/bin/bash

set -x


# 1. Install JDK
JDK_NAME=openjdk-11-jdk
apt install -y "${JDK_NAME}" || { echo "Could not install ${JDK_NAME} package"; exit 1;}


# 2. Download the benchmarks jar files
DACAPO_VERSION=23.11-MR2
RENESSANCE_VERSION=0.16.0

# Download the renaissance jar file
wget -O renaissance.jar https://github.com/renaissance-benchmarks/renaissance/releases/download/v$RENESSANCE_VERSION/renaissance-mit-$RENESSANCE_VERSION.jar

# # Download the DaCapo benchmark
wget https://download.dacapobench.org/chopin/dacapo-$DACAPO_VERSION-chopin.zip
unzip dacapo-$DACAPO_VERSION-chopin.zip
rm -rf dacapo-$DACAPO_VERSION-chopin.zip
mv dacapo-$DACAPO_VERSION-chopin.jar dacapo.jar
mv dacapo-$DACAPO_VERSION-chopin dacapo



## Build benchbase

# install MariaDB
sudo apt install mariadb-server
sudo systemctl start mariadb.service


sudo mariadb
GRANT ALL ON *.* TO 'admin'@'localhost' IDENTIFIED BY 'password' WITH GRANT OPTION;
FLUSH PRIVILEGES;
CREATE DATABASE benchbase;

# 1. Install 21 JDK
JDK_NAME=openjdk-21-jdk
apt install -y "${JDK_NAME}" || { echo "Could not install ${JDK_NAME} package"; exit 1;}

# Build
git clone https://github.com/cmu-db/benchbase.git
cd benchbase
git checkout v2023
./mvnw clean package -P mariadb
cd ..


# Extract
mv benchbase/target/benchbase-mariadb.tgz .
tar xvzf benchbase-mariadb.tgz
cd benchbase-mariadb


## Modify the workload configs

# Change the password for root in all config files
# find . -type f -name "*.xml" -exec sed -i 's|<username>.*</username>|<username>root</username>|' {} +
# find . -type f -name "*.xml" -exec sed -i 's|<password>.*</password>|<password>root</password>|' {} +
find . -type f -name "*.xml" -exec sed -i '/<time>.*<\/time>/a \            <warmup>60</warmup>' {} +

## Run workload
