
import unittest

import pigpio

from pisat.handler import PigpioI2CHandler
from pisat.sensor import Bme280
from pisat.tester.sensor import SensorTestor


ADDRESS_BME280 = 0x76


class TestBME280(unittest.TestCase):
    
    def setUp(self) -> None:
        pi = pigpio.pi()
        handler = PigpioI2CHandler(pi, ADDRESS_BME280)
        self.bme280 = Bme280(handler, name="bme280")
        self.testor = SensorTestor(self.bme280)
        
    def test_observe(self):
        self.testor.print_data()
        
    def test_read(self):
        data = self.bme280.read()
        
        self.assertGreater(data.press, 900)
        self.assertLess(data.press, 1100)
        self.assertGreater(data.temp, 0)
        self.assertLess(data.temp, 30)
        
    def test_bench_mark(self):
        result = self.testor.exec_benchmark(show=True)
        print(f"time to read 100 times: {result}")
        
        
if __name__ == "__main__":
    unittest.main()
