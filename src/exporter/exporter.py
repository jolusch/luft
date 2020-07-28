from prometheus_client import Counter, Gauge

_METRICS = {
    # Gauges
    'humidity': ('bme680_humidity_percent', "Current BME680 humidity"),
    'pressure': ('bme680_pressure_pa', "Current BME680 atmospheric pressure"),
    'temp': ('bme680_temperature_celsius', "Current BME680 temperature"),
    'gas': ('bme680_gas_resistance', "Current BME680 temperature"),

    # Counters
    'io_reads': ('bme680_io_reads_total', "Total number of BME680 I/O reads")
}


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
    def __init__(self, labels=None, metrics=_METRICS):
        self.humidity_gauge = _gauge(metrics['humidity'], labels)
        self.pressure_gauge = _gauge(metrics['pressure'], labels)
        self.temp_gauge = _gauge(metrics['temp'], labels)
        self.gas_gauge = _gauge(metrics['gas'], labels)
        self.ioread_counter = _counter(metrics['io_reads'], labels)

    def export(self, temp, humidity, pressure, gas):
        """Export BME680 metrics to Prometheus"""
        self.ioread_counter.inc()
        self.humidity_gauge.set(humidity)
        self.pressure_gauge.set(pressure)
        self.temp_gauge.set(temp)
        self.gas_gauge.set(gas)
