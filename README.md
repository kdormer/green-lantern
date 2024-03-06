# Green Lantern: A Novel Technique for Carbon-Aware DVFS
This is the repo for Green Lantern, a novel approach to Dynamic Voltage and Frequency Scaling (DVFS) that I developed for my dissertation, achieving a first-class grade. Green Lantern is the first software of its kind to integrate regional carbon-awareness into a DVFS technique, allowing the compute performance of a CPU to be upscaled or downscaled relative to the carbon-intensity of the electricity that it is consuming.

## Methodology
Green Lantern's energy-saving efficacy was evaluated using [jouleit](https://github.com/powerapi-ng/jouleit), a script developed by [PowerAPI]() for measuring power consumption using Intel's "Running Average Power Limit" (RAPL) technology. For a memory-bound real-world workload, [*libquantum*](http://www.libquantum.de/) was used to run quantum mechanics simulations, specifically using [Shor's algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm) to find all the prime factors of a large integer. As for a CPU-bound workload, finite-element analysis was performed using [*calculix*](http://www.calculix.de/). Measurements taken during these benchmarks were total power consumed in joules (J) and time taken to complete the benchmark in seconds.

Baseline results were established by running each benchmark three times and taking the mean. Then the benchmarks were put to the test on an AMD six-core CPU and an Intel dual-core CPU. With the mean results of these benchmarks obtained, the results were evaluated against the null hypothesis using an Independent Samples T Test, resulting in the null hypothesis being rejected and the results being deemed statistically significant.

## Results
In testing, Green Lantern achieved up to a 23% decrease in energy-usage, accompanied by up to a 16% decrease in performance. Depending on the workload, it was found that Green Lantern outperformed other contemporary solutions. Green Lantern, and DVFS techniques in general, are only generally applicable to CPU-bound workloads. If the workload is particularly memory-bound, dynamically upscaling or downscaling the frequency and voltage of a CPU has little effect on overall power-usage.

## Setup

### Dependencies
The following dependencies are required. They can be obtained using `pip`.
- toml
- cpuinfo
- requests
- ipinfo
- time
- random
- cpufreq

### Configuration
Green Lantern is configured using a toml file named `config.toml`. An example configuration can be found below:
```toml
[config]
# regional/national
mode = "regional"

# if regional mode is applied, a UK post-code should be provided
location = "SW1A"

# regional/national limit in gCO2/kWh that GL should scale around
carbon_intensity_limit = "350"

# number of seconds between polling the Carbon Intensity API and up/down-scaling accordingly
poll_interval = 10

# ipinfo access token - if regional mode is applied and no post-code is provided, the ipinfo API will be automatically determine general location using the host's public IP address
access_token = ""
```

### Usage
After providing a configuration file for the program in the project's directory, simply run it as follows:
```
./main.py main
```

Alternatively, mock carbon-intensity data can be used for benchmarking purposes:
```
./main.py benchmark
```
