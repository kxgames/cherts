#!/usr/bin/env python3

import kxg
import cherts

def main():
    print("start main")
    kxg.quickstart.main(
            cherts.DummyWorld,
            cherts.DummyReferee,
            cherts.Gui,
            cherts.GuiActor,
            cherts.AiActor,
    )
    print("end main")

if __name__ == '__main__':
    main()

