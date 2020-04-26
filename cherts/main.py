#!/usr/bin/env python3

import kxg
import cherts

def main():
    kxg.quickstart.main(
            cherts.World,
            cherts.Referee,
            cherts.Gui,
            cherts.GuiActor,
            cherts.AiActor,
    )

