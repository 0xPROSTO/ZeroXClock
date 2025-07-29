import sys
import argparse

from src.zeroxclock_core import ZeroXClock
from src.utils import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ZeroXClock')
    parser.add_argument('--shutdown', type=str, nargs='*',
                        help='Time until PC shutdown (e.g., "--shutdown 1h 30m 15s")')
    parser.add_argument('--seconds', '-s', help="Show seconds", action='store_true')
    args = parser.parse_args()

    shutdown_time = None
    if args.shutdown is not None:
        try:
            if not args.shutdown:
                raise ValueError('Time cannot be empty. Use format like "1h 30m 15s".')
            shutdown_time = parse_shutdown_time(' '.join(args.shutdown))
        except ValueError as e:
            print(f'Error: {e}')
            sys.exit(1)

    ZeroXClock = ZeroXClock(shutdown_time=shutdown_time, show_seconds=args.seconds)
    ZeroXClock.start()
