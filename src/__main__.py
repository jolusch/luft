import argparse
import bme680
from exporter import exporter as exp
import json
import logging
import prometheus_client
from time import sleep


logger = logging.getLogger('bme680_exporter')


def init_arg_parser():
    """Initialize, configure, and return an instance of ArgumentParser"""
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action='store_true',
                   help="increase output verbosity")
    p.add_argument("-p", "--port", type=int, default=9500,
                   help="exporter port (default: 9500)")
    p.add_argument("-l", "--labels", type=json.loads,
                   help="JSON object of Prometheus labels to apply")
    p.add_argument("-i", "--interval",
                   type=int, default=bme680.FILTER_SIZE_3,
                   help="measurement sample interval (default: {})"
                        .format(bme680.FILTER_SIZE_3))

    return p


def configure_logger(args):
    """Configure the module logger"""
    f = logging.Formatter("%(asctime)s - %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(f)
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger.setLevel(log_level)
    logger.addHandler(ch)


def main():
    """Run the exporter"""
    parser = init_arg_parser()
    args = parser.parse_args()

    configure_logger(args)
    logger.info("Initializing BME680 at 0x{a:02x} filter: {f} oversampling(h: {h}, p: {p}, t: {t})"
                .format(a=bme680.I2C_ADDR_PRIMARY,
                        f=bme680.FILTER_SIZE_3,
                        h=bme680.OS_2X,
                        p=bme680.OS_4X,
                        t=bme680.OS_8X))

    sensor = bme680.BME680()
    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_pressure_oversample(bme680.OS_4X)
    sensor.set_temperature_oversample(bme680.OS_8X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sensor.set_temp_offset(6)

    for name in dir(sensor.calibration_data):
        if not name.startswith('_'):
            value = getattr(sensor.calibration_data, name)

            if isinstance(value, int):
                logger.info("calibration data: {}: {}".format(name, value))

    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)

    logger.info("initializing exporter with labels {}".format(args.labels))
    exporter = exp.BME680Exporter(labels=args.labels)

    logger.info("starting exporter on port {}".format(args.port))
    prometheus_client.start_http_server(args.port)

    logger.info("starting sampling with {:.1f}s interval".format(args.interval))

    while True:
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            exporter.export(sensor.data.temperature, sensor.data.humidity, sensor.data.pressure, sensor.data.gas_resistance)

        sleep(args.interval)


if __name__ == "__main__":
    main()
