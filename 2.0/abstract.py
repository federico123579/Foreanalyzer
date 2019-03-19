# =======  Algorithm Abstract module AAM  =======
# Contains all ABS for algorithm building
# ===============================================

from abc import ABCMeta, abstractmethod

class Algorithm(metaclass=ABCMeta):
    """class for algorithm"""

    def __init__(self):
        # algo properties
