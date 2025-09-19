# Benchmarks


The repository comprises several benchmarks from different benchmark suites. The primary goal is not to build new benchmarks but instead use existing once and provide scripts and hacks to run them on gem5.
The repo contains only two own benchmarks (Mediawiki and Nodeapp).
In addition, we support workloads from various open-source Java benchmarks and Googles [Fleetbench](https://github.com/google/fleetbench).
We are continuously working on adding more benchmarks and are happy to receive contributions.



## Simpoints

The repo contains also helper configs and scripts to create simpoints for benchmarks to increase representativeness while reducing simulation time.
See the [simpoint readme](../simpoints/README.md) for more details.


## Own benchmarks

The following own benchmarks are shipped with this repo

Benchmark   | Description | Orchestration | x86 support | Arm support
----------- | ----- | --- | --- | ---
Nodeapp     | Small shopping website implemented in NodeJS. Nginx as HTTP server. | Docker | ✓ | ✓ |
Mediawiki   | Mediawiki page. Witten in PHP. FPM as content server. Nginx as HTTP server, MariaDB as database | Docker | ✓ | ✓ |


## Fleetbench (Google)

Detailed description on the benchmarks refer to the [fleetbench repo](https://github.com/google/fleetbench)

Benchmark   | Version | x86 support | Arm support
----------- | ----- | --- | ---
Proto       | v1.0.0 |  ✓ | ✓ |
Swissmap    | v1.0.0 |  ✓ | ✓ |
Libc        | v1.0.0 |  ✓ | ✓ |
TCMalloc    | v1.0.0 |  ✓ | ✓ |
Compression | v1.0.0 |  ✓ | ✓ |
Hashing     | v1.0.0 |  ✓ | ✓ |
STL-Cord    | v1.0.0 |  ✓ | ✓ |


## Java workloads

The [java-apps](./java-apps/README.md) directory contains instructions and scripts how to install an run Java benchmarks from three popular benchmark suites: [DaCapo](https://github.com/dacapobench/dacapobench) and [Renaissance](https://github.com/renaissance-benchmarks/renaissance) and [Benchbase](https://github.com/cmu-db/benchbase).
The benchmarks have been tested with Arm but not yet with x86. They might work on x86 as well but might require some additional hacks.

Suite | Number of benchmarks | x86 support | Arm support
----------- | ----- | --- | ---
DaCapo      | 8 |  ? | ✓ |
Renaissance | 2 |  ? | ✓ |
Benchbase   | 18 |  ? | ✓ |
