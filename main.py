import glutils
import argparse


"""
Main function to be used in real-world as oppposed to benchmarking. Triggers initiation of Green Lantern.
"""
def main(config):
    if glutils.get_cpu_compatibility():
        glutils.start(config)
    else:
        print("Incompatible CPU. Please note that Green Lantern works only with AMD and Intel CPUs.")


"""
Initiates benchmarking, Green Lantern starts but uses randomised carbon-intensity data instead of real data.
"""
def benchmark(config):
    if glutils.get_cpu_compatibility():
        glutils.start_benchmark(config)
    else:
        print("Incompatible CPU. Please note that Green Lantern works only with AMD and Intel CPUs.")


"""
Parse command-line arguments. Main starts Green Lantern for real-world use, benchmark starts
Green Lantern with mock data.
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['main', 'benchmark'])
    args = parser.parse_args()

    try:
        config = glutils.get_config("./config.toml")['config']

        if config is not None:
            if args.command == 'main':
                main(config)
            elif args.command == 'benchmark':
                benchmark(config)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("Please ensure that you have a valid configuration file in the local directory.")
        print(e)
        exit()
