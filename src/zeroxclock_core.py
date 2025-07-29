import os
import sys
import datetime
import shutil
from time import sleep

from src.zerox_numbers import zerox_numbers_lines
from src.utils import *


class ZeroXClock:
    def __init__(self, shutdown_time=None, show_seconds=False):
        self.shutdown_time = shutdown_time
        self.show_seconds = show_seconds
        self.start_time = None
        self.blink = False

    def start(self):
        terminal_size = self.get_terminal_size()
        current_time = self.get_current_time()
        self.clear_screen()
        self.print_clock(current_time, terminal_size, blink=False)
        colon_positions = self.calculate_colon_positions(current_time, terminal_size)
        hide_cursor()
        sys.stdout.flush()

        if self.shutdown_time is not None:
            self.start_time = datetime.datetime.now()
            self.print_remaining_time(terminal_size)

        try:
            while True:
                sleep(1)
                self.blink = not self.blink

                new_terminal_size = self.get_terminal_size()
                new_time = self.get_current_time()

                if new_terminal_size != terminal_size:
                    terminal_size = new_terminal_size
                    self.clear_screen()
                    self.print_clock(new_time, terminal_size, blink=self.blink)
                    colon_positions = self.calculate_colon_positions(new_time, terminal_size)

                elif new_time != current_time:
                    current_time = new_time
                    self.clear_screen()
                    self.print_clock(current_time, terminal_size, blink=self.blink)
                    colon_positions = self.calculate_colon_positions(current_time, terminal_size)

                else:
                    self.update_colon(colon_positions, self.blink)

                if self.shutdown_time is not None:
                    if self.print_remaining_time(terminal_size) <= 0:
                        if os.name == 'nt':  # Windows
                            os.system("shutdown /s /f /t 0")
                        else:  # Linux/Unix
                            os.system("shutdown -h now")
                        sys.exit(0)

        except KeyboardInterrupt:
            ZeroXClock.clear_screen()
            if self.shutdown_time is not None:
                print("\nНа всякий случай отменю возможное выключение")
                if os.name == 'nt':
                    os.system("shutdown /a")
                else:
                    os.system("shutdown -c")
            print('\033[?25h', end='')
            sys.stdout.flush()
            ZeroXClock.clear_screen()
            sys.exit(0)

    def print_remaining_time(self, terminal_size) -> int:
        """Show remaining time until PC shutdown under clock"""
        elapsed_time = (datetime.datetime.now() - self.start_time).total_seconds()
        remaining_time = max(0, self.shutdown_time - elapsed_time)
        days, rem = divmod(int(remaining_time), 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        remaining_time_str = f"Shutdown "
        if days > 0:
            remaining_time_str += f"in {days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            remaining_time_str += f"in {hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            remaining_time_str += f"in {minutes}m {seconds}s"
        elif seconds > 0:
            remaining_time_str += f"in {seconds}s"
        else:
            remaining_time_str += f"NOW!"

        y_space = (terminal_size[1] - 5) // 2 + 7  # 5 — высота часов
        x_space = (terminal_size[0] - len(remaining_time_str)) // 2 + 1

        print(f'\033[{y_space};{x_space}H\033[2K{remaining_time_str}', end='')
        sys.stdout.flush()

        return remaining_time

    def calculate_colon_positions(self, current_time, terminal_size):
        clock_height = 5
        y_space = (terminal_size[1] - clock_height) // 2
        colon_index = current_time.index(':')
        positions = []
        for height in [1, 3]:  # Строки, где двоеточие имеет "██"
            line_parts = [zerox_numbers_lines[number][height] for number in current_time]
            total_width = sum(len(part) for part in line_parts) + 2 * (len(current_time) - 1)
            x_space = (terminal_size[0] - total_width) // 2
            column = x_space + sum(len(line_parts[i]) for i in range(colon_index)) + 2 * colon_index + 1
            row = y_space + height + 1
            positions.append((row, column))
        return positions

    def update_colon(self, positions, blink):
        for row, column in positions:
            print(f'\033[{row};{column}H', end='')
            if not blink:
                print('██', end='')
            else:
                print('  ', end='')
        print('\033[999;999H', end='')  # Переместить курсор в конец экрана
        sys.stdout.flush()

    @staticmethod
    def print_clock(current_time: str, terminal_size: tuple[int, int] = (0, 0),
                    blink: bool = False, clock_height: int = 5, centered: bool = True) -> None:
        output = str()
        if blink:
            current_time = current_time.replace(':', '*')
        if centered:
            y_space = (terminal_size[1] - clock_height) // 2
            print('\n' * y_space, end='')
        for height in range(clock_height):
            if centered:
                x_space = ((terminal_size[0] -
                            sum([len(zerox_numbers_lines[number][0]) for number in current_time]) -
                            (2 * (len(current_time) - 1))) // 2)
                output += ' ' * x_space
            for number in current_time:
                output += zerox_numbers_lines[number][height]
                output += '  '
            output += '\n'
        print(output)

    @staticmethod
    def get_current_time(include_seconds: bool = False) -> str:
        try:
            if not include_seconds:
                return datetime.datetime.now().strftime("%H:%M")
            return datetime.datetime.now().strftime("%H:%M:%S")
        except Exception as e:
            print(f'Unknown error!\n{e}')
            sys.exit(1)

    @staticmethod
    def get_terminal_size():
        try:
            terminal_size = shutil.get_terminal_size((0, 0))
            return terminal_size.columns, terminal_size.lines
        except Exception as e:
            print(f'Unknown error!\n{e}')
            sys.exit(1)

    @staticmethod
    def clear_screen():
        try:
            # print('\033[2J\033[H', end='')
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception as e:
            print(f'Unknown error!\n{e}')
            sys.exit(1)
