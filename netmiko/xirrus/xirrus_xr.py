from __future__ import unicode_literals
from netmiko.base_connection import BaseConnection
import time

class XirrusXR(BaseConnection):
    """
    Implement methods for interacting with XIRRUS APs.

    Disables 'enable()' and 'check_enable_mode()' methods.
    """

    def session_preparation(self):
        """
        Prepare the session after the connection has been established.

        Enter config mode.
        Disable paging (the '--more--' prompts).
        Exit config mode.
        """

        self.disable_paging(command="no more")
        self.set_base_prompt()

    def check_enable_mode(self, *args, **kwargs):
        """No enable mode on Xirrus APs."""
        pass

    def enable(self, *args, **kwargs):
        """No enable mode on Xirrus APs."""
        pass

    def exit_enable_mode(self, *args, **kwargs):
        """No enable mode on Xirrus APs."""
        pass

    def check_config_mode(self, check_string='', pattern=''):
        """Checks if the device is in configuration mode or now."""
        debug = True
        if debug:
            print("pattern: {}".format(pattern))
        self.write_channel("\n")
        output = self.read_until_pattern(pattern=pattern)
        if debug:
            print("check_config_mode: {}".format(repr(output)))
        return check_string in output
   
    def config_mode(self, config_command='configure', pattern='(config)'):
        """Enter configuration mode."""
        output = ''
        if not self.check_config_mode():
            self.write_channel(self.normalize_cmd(config_command))
            output = self.read_until_pattern(pattern=pattern)
            if not self.check_config_mode():
                raise ValueError("Failed to enter configuration mode.")
        return output

    def exit_config_mode(self, exit_config='end', pattern=''):
        """Exit configuration mode."""
        debug = False
        output = ''
        if debug:
            print(exit_config)
        if self.check_config_mode():
            self.write_channel(self.normalize_cmd(exit_config))
            output = self.read_until_pattern(pattern=pattern)
            if debug:
                print("exit_config_mode: {}".format(output))
            if self.check_config_mode():
                raise ValueError("Failed to exit configuration mode")
        return output

    def set_base_prompt(self, pri_prompt_terminator='#',
                        alt_prompt_terminator='>', delay_factor=1):
        """Sets self.base_prompt"""
        #self.read_until_prompt()
        prompt = self.find_prompt(delay_factor=delay_factor)
        print(prompt)
        if not prompt[-1] in (pri_prompt_terminator, alt_prompt_terminator):
            raise ValueError("AP Prompt not found: {0}".format(prompt))
        # Strip off trailing terminator
        self.base_prompt = prompt[:-1]
        return self.base_prompt

    def disable_paging(self, command="no more", delay_factor=1):
        """Disable paging default to the xirrus method."""
        debug = False
        delay_factor = self.select_delay_factor(delay_factor)
        time.sleep(delay_factor * .1)
        self.clear_buffer()
        config = self.normalize_cmd("configure")
        command = self.normalize_cmd(command)
        exit_config = self.normalize_cmd("end")

        if debug:
            print("In disable_paging")
            print("command: {}", format(command))

        self.read_until_prompt()
        self.write_channel(config)
        output = self.read_until_prompt()
        self.write_channel(command)
        output += self.read_until_prompt()
        self.write_channel(exit_config)
        output += self.read_until_prompt()

        if self.ansi_escape_codes:
            output = self.strip_ansi_escape_codes(output)
        if debug:
            print(output)
            print("Exiting disable_paging")

        return output
