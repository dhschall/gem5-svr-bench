

# Java benchmarks

This directory instructs on how to run Java benchmarks from three popular benchmark suites: [DaCapo](https://github.com/dacapobench/dacapobench) and [Renaissance](https://github.com/renaissance-benchmarks/renaissance) and [Benchbase](https://github.com/cmu-db/benchbase).
Refer to their respective GitHub repositories for more information about the benchmarks and their workloads.

> [!NOTE]
> Be aware that the DaCapo benchmark suites `jar` file is quite large (6GB) and unzipped it takes up 21GB of space. You need to have enough space on your disk to run the benchmarks. See the [disk image README](./../../image/README.md#disk-image-size) for more details on how to create a disk image with enough space.


## Benchmark status

### Versions

- DaCapo: 23.8-chopin-RC1
- Renaissance: 0.16.0
- Java: openjdk-11-jdk

### Benchmark support

We have tested the following benchmarks from the DaCapo and Renaissance benchmark suites:

Benchmark | Suite | X86 | ARM
--- | --- | --- | ---
cassandra | DaCapo | ? | ✅
h2 | DaCapo | ? | ✅
h2o | DaCapo | ? | ✅
kafka | DaCapo | ? | ✅
luindex | DaCapo | ? | ✅
lusearch | DaCapo | ? | ✅
spring | DaCapo | ? | ✅
tomcat | DaCapo | ? | ✅

<!-- avrora | DaCapo | ? | ✅
batik | DaCapo | ? | ✅
biojava | DaCapo | ? | ✅ 
fop | DaCapo | ? | ✅
graphchi | DaCapo | ? | ✅ -->
<!-- jme | DaCapo | ? | ✅
jython | DaCapo | ? | ✅ -->

<!-- pmd | DaCapo | ? | ✅ -->
<!-- sunflow | DaCapo | ? | ✅ -->
<!-- tradebeans | DaCapo | ? | ✅
tradesoap | DaCapo | ? | ✅
xalan | DaCapo | ? | ✅
zxing | DaCapo | ? | ✅ -->

Benchmark | Suite | X86 | ARM
--- | --- | --- | ---
finagle-chirper | Renaissance | ? | ✅
finagle-http | Renaissance | ? | ✅


## Benchbase Java benchmarks
Benchbase is another benchmark suite of Java applications. Note it will require a Java 21 JDK to build the benchmarks.

To build the benchmark jar files, follow the instructions in the [Benchbase README](https://github.com/cmu-db/benchbase?tab=readme-ov-file#quickstart)

The build process will create a tar file `benchbase-mariadb.tgz` in the `benchbase/target` directory. Copy this tar file to the home directory of the gem5 server and extract it.

Before running the benchmarks you need to edit the config files for each benchmark to update the `user` and `password` fields for the database connection.
Also you need to add the <warmup>64</warmup> to the `workload` section of the config file.

Benchmark | Suite | X86 | ARM
--- | --- | --- | ---
TPCC | Benchbase | ? | ✅
TPCH | Benchbase | ? | ✅
TATP | Benchbase | ? | ✅
Wikipedia | Benchbase | ? | ✅
Resourcestresser | Benchbase | ? | ✅
Twitter | Benchbase | ? | ✅
Epinions | Benchbase | ? | ✅
YCSB | Benchbase | ? | ✅
Seats | Benchbase | ? | ✅
Auctionmark | Benchbase | ? | ✅
CHBenchmark | Benchbase | ? | ✅
Voter | Benchbase | ? | ✅
Sibench | Benchbase | ? | ✅
Noop | Benchbase | ? | ✅
Smallbank | Benchbase | ? | ✅
Hyadapt | Benchbase | ? | ✅
OTMetrics | Benchbase | ? | ✅
Templated | Benchbase | ? | ✅