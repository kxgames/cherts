#!/usr/bin/env python3

import kxg

class DummyMap(kxg.Token):

    def __init__(self, shape):
        super().__init__()

        self.boundaries = shape

    def get_boundaries(self):
        return self.boundaries
