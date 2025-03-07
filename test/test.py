# *************************************
# author: leonard.yu@teledyne.com
# *************************************
import sys
import os
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(currentdir)
sys.path.append(parentdir)

import asyncio
from xoa_cqtm.cqtm import XenaCableQualification

async def main():
    stop_event = asyncio.Event()
    try:
        test = XenaCableQualification("test_config.yml")
        await test.run()
    except KeyboardInterrupt:
        stop_event.set()

if __name__ == "__main__":
    asyncio.run(main())