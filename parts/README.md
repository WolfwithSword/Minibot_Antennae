# STLs

- Stalks: tpu_left_stalk.stl, tpu_right_stalk.stl
- Bulbs: abs_left_bulb, abs_right_bulb, abs_clear_left_bulb_light.stl, abs_clear_right_bulb_light.stl
- Headband: headband.stl
- Left Shell: abs_left_backing.stl, abs_left_shell.stl
- Right Shell: abs_right_backing.stl, abs_right_shell.stl
  - Note: The screw alignment for the ESP32 board is *not* perfect, despite using references. As such, when screwing in with M2 screws, may only fit 3 screws and one may be at an angle. Prioritize the front near the USB-C port.
- Misc: abs_top_plugs.stl, abs_side_plugs.stl
  - The plugs are for plugging the holes for where you do *not* use the pogo connector inserts.


# BOM

This is not my best BOM, made in rush

- ESP32 Board DFR0654. [Digikey](https://www.digikey.ca/en/products/detail/dfrobot/DFR0654/13978504),  [dfrobot](https://www.dfrobot.com/product-2195.html)
  - Any other can do, and can probably be swapped for a smaller one with a separate charge shield/circuit for battery. The one linked simply fit the best, had decent processing power and memory, and had the built in battery port and charger on the side instead of the front.
  - Chosen for expandability. If using another board, there are no guarantees as to the code working fully in case lack of processing or memory.
  - This project can use both BLE and WiFi servers, but the config does allow to disable both if you want just default settings.
- LiPo Battery
  - [3.7v 1100mAh, 34.5x51x6.3mm (WxLxH)](https://amzn.to/3zZs4OB).
  - If using the one from the link, you *MAY* need to swap the pwr and gnd leads. Make sure before hooking up to board.
  - For alternatives, size the slot fits is mentioned above. If loose, please pad to make sure it does not come out during use. Capacity can be any, 1100mAh will last between 12-18 hours roughly.
- Screws
  - 4x M2 8-12mm (For ESP32, no heatset inserts, direct to plastic)
  - 2x M3 14mm 
  - 4x M3 12mm (6x if not using headband, possibly will work for all 6 anyways. Then no need for 14mm. I just used all 14mm and cut 4 of em)
- 6x M3 x4mm Heatset inserts
- Resistors
  - 5x 270ohm
- LEDs [Basic kit](https://amzn.to/4fkcopn)
  - 3x Green 5mm (Green plastic shell, so it is still green when off)
  - 2x White or Yellow (your preference) 5mm
- JST-PHR-02 Female and Male connectors (1 pair). [Example](https://amzn.to/46GCu2d)
- Wiring, Heatshrink tubes, pins etc
- Pogo connectors
  - [4Pin Wire MF 20cm](https://s.click.aliexpress.com/e/_DB3E399) To be used externally, trim if necessary
  - [4Pin Straight no-wire](https://s.click.aliexpress.com/e/_DB3E399) To be used internally
- Optional: Acetone
 - If printing in ABS, Acetone can be used to smooth it after some sanding and give a tough, glossy finish. Can vapour smooth it over time or just pour it over once and immediately remove without touching.
- Filament
  - Recommended if you don't want to paint:  [TPU](https://us.polymaker.com/products/polyflex-tpu90?variant=39574341189689&aff=333), [ABS](https://us.polymaker.com/products/polylite-abs?variant=39574342434873&aff=333) 
  - For the Clear pieces in the bulbs, can use any transparent or white filament. ABS/PLA/PETG does not matter.
- Optional: Hot glue (for securing the LEDs and possibly strain relief on some wires)
- Super Glue: (to perma attach the stalks to the shells, hot glue can work too)

# Assembly

## Wiring

See the attached image () for which pins need to go where. All ground wires can be spliced and connected to the same GND pin.

For the LED in the left antenna (where the battery is), connect the ground to the same ground pin on the pogo connector as the battery.

Attach each LED to a 270ohm resistor.

The pogo connectors have support for 4 wires, but only 3 are used. Please make sure they line up properly.

For the PHR connectors, use the male end in the Right shell going to the pogo connector, and the female inside the Left shell going into the pogo connector (if you need to swap battery leads, can do it here or on battery itself), and plug battery into the female end, and male side into the ESP board (tight fit, may need to clip corner).

TODO: Link img

Yes I know the diagram isn't super good, made it in a hurry.

## Building

Use short thin wires, preferably silicone for flexibility inside as it may be a tight fit. Trim the leads on the LEDs and resistors as needed. 

Ensure the ESP32 can be screwed in (preferably route most of the wiring *under* the board) and that the backing can be screwed onto the shell still. It goes in upside down (ESP Chip, Battery port etc, will go facing the round part of the shell).

Insert the LED for each antennae stalk with wires pre-attached through the top of the TPU stalks, then insert the stalks into the shells. They should be a smooth fit, but so superglue them at the base to make sure it is attached tightly.

For inserting the stalks into the bulb ends, it is a *very* tight fit, recommend using tough tweezers to push it in little by little. Once in (with the LED too), pull it out slightly to make sure it is a tight fit at the end. Then insert the light-pieces into the bulb top. You can do this beforehand too and glue from the inside, or try to glue as you insert. If you used clear ABS on ABS bulbs, you can use acetone to bond them, just a light touch of it.

For the shells, if you want them smooth and glossy, sand them then treat them with acetone if printed in ABS.

Super glue the pogo connectors into the slots on the shell you choose - use plugs in the open ones and bond with superglue or acetone if ABS.

To connect the two antennae you will need to make a POGO wire with the reverse ends that will go around the back or top depending on choice. I recommend choosing the back so it provides additional stability with the headband.

The headband is adjustable and relies on the larger screw at the top of the back panels.