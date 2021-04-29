# Demo

Steps for reproducing the demo. Please follow the steps on the actual drone, simulator is of not much help here.

This assumes that you have updated the firmware on the drone to a version later than 1.2 and you have ssh access onto the drone. The wiki at <https://github.com/intel-aero/meta-intel-aero/wiki> contains detailed instructions on it and also the linked video lectures are of great help.

## Buliding the orignial PX4 firmware

- From <http://dev.px4.io/en/setup/getting_started.html>, follow the steps at <http://dev.px4.io/en/setup/dev_env.html> for your operating system to install the required dependencies for your platform.
- As per <http://dev.px4.io/en/setup/building_px4.html>, clone the firmware from <https://github.com/PX4/Firmware>. The demo was done at the commit `e2973028ab`, so if something fails, try this commit. Building for the simulator now can be good check of the dev setup.
- Build the firmware for Intel RTF by executing `make aerofc-v1_default`.
- Test the vanilla build is working fine by flashing it onto the FC of the drone. You can follow <https://docs.px4.io/en/flight_controller/intel_aero.html#flashing-px4-software> or the follow steps for flashing.
	- Copy the file `.px4` file in the build directory onto the drone though `scp`. For my setup it was `scp build/nuttx_aerofc-v1_default/aerofc-v1_default.px4 root@192.168.7.2:~/`.
	- SSH onto the drone and run `aerofc-update.sh aerofc-v1_default.px4`.
	- If the flash is successful, the lights beneath the rotors blink in a periodic fashion.
- Run `./Tools/mavlink_shell.py tcp:192.168.7.2:5760` from your system to get the shell on the FC and check that it booted correctly. Ref: <https://dev.px4.io/en/debug/system_console.html>

## Building the modified PX4 firmware

- Next fetch the `bft-boeing-drone` project.
- Execute `deps.sh` in `patchkit` folder to install the dependencies.
- Install Radare2 (<https://github.com/radare/radare2>) and r2pipe (<https://github.com/radare/radare2-r2pipe/tree/master/python>).
- Set the `PATH` `env` variable such that [patchkit/arm-none-eabi-g++](patchkit/arm-none-eabi-g++) is in the `PATH`.
- Edit the above file to fix the path of the original `arm-none-eabi-g++` compiler (which is installed as part of setting up the tool chain, can also be found using the `which` command), `stack_patch` script (present in the same folder) and `file_list` filter file (present in the same folder).
- Edit the `file_list` to select only those obj files that needs to be patched. Each line denote the obj file that is passed as output to the compiler. The included `file_list` selects the drivers to be patched.
- Run `make clean && make aerofc-v1_default` in the cloned PX4 firmware directory.
- Flash the firmware and verify that it is booting correctly as described above.
