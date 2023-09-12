import azx
from azx import info
from .utils import EXAMPLE
import unittest

# see https://docs.python.org/3/library/unittest.html#basic-example
class TestTemplate(unittest.TestCase):

    def test_example(self):
        self.assertEquals(EXAMPLE, "Example")