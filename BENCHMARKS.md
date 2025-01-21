# Benchmarks


The repository comprises several benchmarks from different benchmark suites. It is not the aim to build new benchmarks but run existing suites on gem5.
We support workloads from Googles [Fleetbench](https://github.com/google/fleetbench) and Meta's [DCPerf]()



## Own benchmarks

The following own benchmarks are shipped with this repo

Benchmark   | Description | Orchestration | x86 support | Arm support
----------- | ----- | --- | --- | ---
Nodeapp     | Small shopping website implemented in NodeJS. Nginx as HTTP server. | Docker | ✓ | ✕ |
Mediawiki   | Mediawiki page. Witten in PHP. FPM as content server. Nginx as HTTP server, MariaDB as database | Docker | ✓ | ✕ |


## Fleetbench (Google)

Detailed description on the benchmarks refer to the [fleetbench repo](https://github.com/google/fleetbench)

Benchmark   | Version | x86 support | Arm support
----------- | ----- | --- | ---
Proto       | v1.0.0 |  ✓ | ✕ |
Swissmap    | v1.0.0 |
Libc        | v1.0.0 |
TCMalloc    | v1.0.0 |
Compression | v1.0.0 |
Hashing     | v1.0.0 |
STL-Cord    | v1.0.0 |