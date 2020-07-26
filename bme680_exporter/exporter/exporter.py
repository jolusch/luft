import logging
from prometheus_client import Counter, Gauge

_LOG_MESSAGE_FORMAT = "   ".join(["temp: {temp:.2f} C",
                                  "humidity: {humidity:.2f}%",
                                  "pressure: {pressure:.2f} hPa",
                                  "gas: {gas:.2f} Ohms"])
_METRICS = {
    # Gauges
    'humidity': ('bme680_humidity_percent', "Current BME680 humidity"),
    'pressure': ('bme680_pressure_pa', "Current BME680 atmospheric pressure"),
    'temp': ('bme680_temperature_celsius', "Current BME680 temperature"),
    'gas': ('bme680_gas_resistance', "Current BME680 temperature"),

    # Counters
    'io_reads': ('bme680_io_reads_total', "Total number of BME680 I/O reads"),
    'io_errors': ('bme680_io_errors_total', "Total number of BME680 I/O errors")
}

logger = logging.getLogger(__name__)


def _gauge(metric, labels=None):
    """Initialize and return a Gauge object"""
    if labels is None:
        labels = {}
    label_keys = list(labels.keys())
    label_values = [labels[k] for k in label_keys]
    gauge = Gauge(*metric, label_keys)
    if len(label_values):
        gauge = gauge.labels(*label_values)
    return gauge


def _counter(metric, labels=None):
    """Initialize and return a Counter object"""
    if labels is None:
        labels = {}
    label_keys = list(labels.keys())
    label_values = [labels[k] for k in label_keys]
    counter = Counter(*metric, label_keys)
    if len(label_values):
        counter = counter.labels(*label_values)
    return counter


class BME680Exporter(object):
    """Collects and exports metrics for a single BME680 sensor"""
    def __init__(self, bme680, labels=None, metrics=_METRICS, log_format=_LOG_MESSAGE_FORMAT):
        self.bme680 = bme680
        self.temp = None
        self.humidity = None
        self.pressure = None
        self.gas = None
        self.log_format = log_format
        self.humidity_gauge = _gauge(metrics['humidity'], labels)
        self.pressure_gauge = _gauge(metrics['pressure'], labels)
        self.temp_gauge = _gauge(metrics['temp'], labels)
        self.gas_gauge = _gauge(metrics['gas'], labels)
        self.ioread_counter = _counter(metrics['io_reads'], labels)
        self.ioerror_counter = _counter(metrics['io_errors'], labels)

    def measure(self):
        """Read BME680 measurements"""
        self.ioread_counter.inc()
        try:
            self.temp = self.bme680.data.temperature
            self.humidity = self.bme680.data.humidity
            self.pressure = self.bme680.data.pressure
            self.gas = self.bme680.data.gas_resistance
        except IOError:
            logger.error('IOError when reading BME680 measurements')
            self.ioerror_counter.inc()
        logger.info(self.log_format.format(temp=self.temp,
                                           humidity=self.humidity,
                                           pressure=(self.pressure / 100),
                                           gas=self.gas))

    def export(self):
        """Export BME680 metrics to Prometheus"""
        self.humidity_gauge.set(self.humidity)
        self.pressure_gauge.set(self.pressure)
        self.temp_gauge.set(self.temp)
        self.gas_gauge.set(self.gas)
