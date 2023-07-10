import toml
import cpuinfo
import requests
import ipinfo
import time
import random
from cpufreq import cpuFreq

supported_cpus = ["AMD", "INTEL"]

# To be initialised based on what's supported by system
cpu_governors = {}
current_governor = 0

# Keeps track of governor initiation
gl_init = False


"""
Get type of CPU of system.
"""
def get_cpu_brand():
    return cpuinfo.get_cpu_info()['brand_raw']


"""
Check if CPU is supported by Green Lantern, return true if so, false if not.
"""
def get_cpu_compatibility():
    brand_raw = get_cpu_brand()

    for cpu in supported_cpus:
        if cpu.upper() in brand_raw.upper():
            return True

    return False


"""
Open the configuration file stored in path.
"""
def get_config(path):
    with open(path, 'r') as f:
        return toml.load(f)


"""
Get the national or regional carbon-intensity based on which options set in the config.
"""
def get_CI(postcode, config):
    if postcode is None:
        return get_national_CI()
    elif len(config['location']) > 0:
        return get_regional_CI(postcode)


"""
Get random carbon-intensity forecast, used for benchmarking purposes.
"""
def get_mock_CI():
    return random.randint(50, 350)


"""
Get regional carbon-intensity forecast for the postcode location passed into the function.
Return JSON response.
"""
def get_regional_CI(postcode):
    headers = {
        'Accept': 'application/json'
    }

    try:
        return requests.get(f'https://api.carbonintensity.org.uk/regional/postcode/{postcode}', params={},
                            headers=headers).json()
    except:
        print("Unable to connect to Carbon Intensity API. Please check that you have a working internet connection.")


"""
Get national carbon-intensity forecast for the UK.
"""
def get_national_CI():
    headers = {
        'Accept': 'application/json'
    }

    try:
        return requests.get('https://api.carbonintensity.org.uk/intensity', params={}, headers=headers).json()
    except:
        print("Unable to connect to Carbon Intensity API. Please check that you have a working internet connection.")


"""
Get public IP address of server running Green Lantern in order to get a rough estimate of location.
"""
def get_public_ip():
    return requests.get('https://api.ipify.org').content.decode('utf8')


"""
Get postcode based on public IP address using the IPInfo API.
"""
def get_postcode(ip):
    access_token = 'be7b47304d7cee'
    handler = ipinfo.getHandler(access_token)
    details = handler.getDetails(ip)
    return details.postal


""""
Get location of computer/server, get from configuration if provided, get from public IP if not.
"""
def get_location(config):
    if len(config['location']) == 0 or config['location'] is None:
        print("Identifying location...")

        try:
            location = get_postcode(get_public_ip())

            if len(location) > 0 and location is not None:
                print("Identified location: " + location)
                return location
        except KeyboardInterrupt:
            exit()
        except:
            print(
                "Unable to determine location. Please ensure that you have a valid internet connection or input your "
                "postcode into the location item within the config.")
    else:
        return config['location']


"""
Get governor's weight based on governor name.
"""
def get_governor_weight(governor):
    match governor:
        case "powersave":
            return 1
        case "conservative":
            return 2
        case "ondemand":
            return 3
        case "performance":
            return 4


"""
Get governor name based on governor weight.
"""
def get_governor_name(weight):
    match weight:
        case 1:
            return "powersave"
        case 2:
            return "conservative"
        case 3:
            return "ondemand"
        case 4:
            return "performance"


"""
Sort unsorted dictionary.
"""
def sort_dict(unsorted_dict):
    return dict(sorted(unsorted_dict.items()))


"""
Get governor currently in use by CPU.
"""
def get_current_governor(governors_dict):
    tmp_gov = next(iter(governors_dict.values()))

    for weight, gov in governors_dict.items():
        if gov != tmp_gov:
            return None

    return get_governor_weight(tmp_gov)


"""
Get governors supported by CPU and store in global dictionary.
"""
def init_governors():
    global cpu_governors
    global current_governor

    cpu = cpuFreq()
    tmp_cpu_governors = {}

    for gov in cpu.available_governors:
        if get_governor_weight(gov) is not None:
            tmp_cpu_governors[get_governor_weight(gov)] = gov

    cpu_governors = sort_dict(tmp_cpu_governors)
    current_governor = get_current_governor(cpu.get_governors())


"""
Scale up to governor with +1 weight to boost CPU frequency.
"""
def upscale_governor():
    if gl_init is False or current_governor == 0:
        init_governors()

    cpu = cpuFreq()

    try:
        cpu.set_governors(cpu_governors[current_governor + 1])
        print("Carbon intensity within acceptable limit, increasing CPU performance...")
    except:
        print("Failed to increase CPU performance. Please check that you are running with sudo privileges.")


"""
Scale down to governor with -1 weight to decrease CPU frequency.
"""
def downscale_governor():
    if gl_init is False or current_governor == 0:
        init_governors()

    cpu = cpuFreq()

    try:
        cpu.set_governors(cpu_governors[current_governor - 1])
        print("Carbon intensity outside of acceptable limit, decreasing CPU performance...")
    except:
        print("Failed to decrease CPU performance. Please check that you are running with sudo privileges.")


"""
Set governor based on arbitrary weight.
"""
def set_governor(governor_weight):
    global current_governor

    if gl_init is False or current_governor == 0:
        init_governors()

    cpu = cpuFreq()

    try:
        # cpu.set_governors(cpu_governors[governor_weight])
        current_governor = governor_weight
    except:
        print("Failed to set specified governor. Please check that you are running with sudo privileges.")


"""
Determine which CPU governor to be used at various carbon-intensity forecast thresholds.
"""
def determine_governor(config, forecast):
    ci_limit = int(config['carbon_intensity_limit'])

    if forecast <= (0.25 * ci_limit):
        # Less than or equal to 25%
        print("CI forecast less than or equal to 25% of specified limit...")
        return get_governor_weight("performance")
    elif forecast <= (0.5 * ci_limit):
        # Less than or equal to 50%
        print("CI forecast less than or equal to 50% of specified limit...")
        return get_governor_weight("ondemand")
    elif forecast <= (0.75 * ci_limit):
        # Less than or equal to 75%
        print("CI forecast less than or equal to 75% of specified limit...")
        return get_governor_weight("conservative")
    elif forecast <= ci_limit:
        # Greater than forecast
        print("CI forecast within 25% or equal to specified limit...")
        return get_governor_weight("powersave")
    elif forecast > ci_limit:
        print("CI forecast exceeds specified limit...")
        return get_governor_weight("powersave")


"""
Start Green Lantern background process. Location and carbon-intensity forecast are obtained according
to the poll interval set in the config and governor adjusted accordingly.
"""
def start(config):
    location = get_location(config)

    while True:
        ci_request = get_CI(location, config)
        ci_forecast = ci_request['data'][0]['data'][0]['intensity']['forecast']
        gov = determine_governor(config, ci_forecast)

        print("Carbon intensity forecast: " + str(ci_forecast))

        try:
            set_governor(gov)
            print("CPU governor: " + get_governor_name(gov))
            print("===================")

        except:
            print("Unable to adjust CPU governor. Please ensure you are using a compatible CPU.")

        time.sleep(config['poll_interval'])


"""
Start Green Lantern background process. Mock data used in place of real-world data.
Governor adjusted accordingly at interval set by user in the config.
"""
def start_benchmark(config):
    while True:
        ci_forecast = get_mock_CI()
        gov = determine_governor(config, ci_forecast)

        print("Carbon intensity forecast: " + str(ci_forecast))

        try:
            set_governor(gov)
            print("CPU governor: " + get_governor_name(gov))
            print("===================")

        except:
            print("Unable to adjust CPU governor. Please ensure you are using a compatible CPU.")

        time.sleep(10)
