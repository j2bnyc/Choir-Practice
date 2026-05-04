Here's a thorough breakdown of the Teenage Engineering Choir (CH-8):
Overview
The Choir is an ensemble of eight computerized wooden dolls, each with its own characteristic vocal range, capable of singing solo or together to perform immersive a cappella concerts. Teenage Engineering It's a reimagining of Teenage Engineering's very first project — the Absolut Vodka Choir, an art installation created in 2007 featuring 22 wooden dolls. Designboom It notably made its cinematic debut in Pixar's film Designboom Elio, where its voices signal the protagonist's first contact with alien life.
Physical Construction
Each doll is handcrafted from beech wood and polished with hard wax oil. Designboom Inside each doll is a removable sound module containing the processor, speaker, BLE transmitter, and battery. Depending on the doll, the sound module is placed either horizontally or vertically inside the wooden body; the vertical ones have an additional beige ring on top. GitHub
The Eight Members
The Choirama GitHub repo documents the full ensemble with precise specs:
DollOriginVoice TypeMusical RangeFrequency RangeHatsheputEgyptMezzo sopranoA3–F5220–698 HzLeilaPalestineSopranoC#4–A5277–880 HzOlgaRussiaContraltoE3–C5162–523 HzBogdanCossackBassE2–C482–262 HzCarloItalyBaritoneG2–D#498–294 HzIvanaNetherlandsAltoF#3–D5175–587 HzMikiJapanTenorB2–G4117–392 HzGieselaGermanyMezzo sopranoB3–G5247–784 Hz
Internal Hardware (Teardown Details)
The sound module can be opened by unscrewing the lid over the speaker. Inside is a tiny circuit board and a battery. GitHub The key components identified in the community teardown:

SoC: Nordic Semiconductor nRF52840, which includes an ARM Cortex-M4F CPU, flash memory, and an integrated 2.4 GHz multiprotocol radio supporting BLE, ANT, and 802.15.4. The specific variant used is N52840-Q1AAD0-2025KR.
Amplifier: Maxim Integrated MAX98390 — a boosted Class-D amplifier with integrated dynamic speaker management.
Power management: Texas Instruments BQ25892 charger IC.
Battery: 3.7V LiPo, 850mAh (3.145Wh), providing up to four hours of continuous performance. With moderate use (about 10 minutes a day), it can last a month on a single charge. Designboom
Charging is via USB-C.

There are also a C4066 analog switch and an unidentified chip marked 6W808 2025QBR on the board, plus circular test/programming pads on the upper side.
How It Works
Interaction is gesture-based thanks to a built-in accelerometer/vibration sensor: tap the doll on its head or on the table to trigger play or pause, tilt left or right to decrease or increase volume. Teenage Engineering A firm smack turns it off entirely.
Inter-doll communication happens via BLE beacons. When more than one member is placed together in any combination, they communicate with each other, recognize the choral members in range, and join in a full choral performance. Teenage Engineering This means you can use any subset of the eight — even a single doll performs a solo.
Pre-loaded repertoire: The dolls come with 16 pre-programmed pieces ranging from baroque to folk. These compositions were created using an algorithm based on counterpoint melody, a technique referring to the independent but complementary relationship between two or more melodic lines played simultaneously. Teenage Engineering
MIDI Over BLE — Where It Gets Interesting
The Choir's MIDI compatibility is where the magic really happens — you can conduct the choir with OP–1 Field, OP–Z, or any MIDI keyboard with Bluetooth connectivity. Teenage Engineering
Connecting: Press and hold the single button on any doll until it sings "Searching for controller." It then connects with any BLE MIDI device in advertising mode. GitHub The pairing PIN is 000000 (six zeros). Connecting one doll pairs the whole ensemble.
MIDI CC controls give you deep voicing control:

CC1 — Vibrato (most noticeable on longer notes)
CC2 — Consonant selection (maps CC values to specific consonant phonemes)
CC3 — Vowel selection (maps CC values to specific vowel phonemes)
CC4 — Reverb duration

This means you can essentially program the choir to sing specific syllables by combining consonant and vowel CC values before triggering a note. The Choirama repo includes full mapping tables for both consonant and vowel CC values.
Important caveat: voicing changes only take effect on the next note — they won't alter a note already playing. GitHub Notes are automatically distributed across whichever dolls are active in the ensemble.
Hacking and Tinkering
USB-C data connection: When plugging the sound module into a computer via USB-C, it mounts a small USB drive containing version.txt (with doll type, serial number, firmware version, and PCBA serial) and a readme.txt with firmware upgrade instructions. GitHub Firmware updates are done by dropping a file onto this virtual USB drive, ejecting, unplugging, then holding the button for 2 seconds while the update installs.
CDC-ACM serial device: The sound module also registers as a CDC-ACM device, which could potentially be used to transfer data between a host computer and the module. Connecting via minicom didn't yield any feedback, so the communication protocol remains unknown. GitHub This is an intriguing avenue for anyone wanting to go deeper.
Operating system: Currently unknown, but likely some Linux variant GitHub given the nRF52840 platform (though it could also be running Zephyr RTOS or a bare-metal Nordic SDK — the community hasn't confirmed).
Firmware: The latest version is 1.1.3 (released December 22, 2022), available from TE's downloads page.
iPad/AUM workflow: The Choirama repo includes a dedicated tutorial for performing music with the Choir using an iPad running AUM (a flexible audio mixer/host), which gives you a full software environment for sequencing, CC automation, and real-time control over the dolls.
Pricing
Choir members are available for $249 individually or $1,992 for the entire set of eight. Colossal
Known Quirks
The choir sometimes reverts back to its built-in repertoire even when connected to a MIDI device GitHub (appears to be a bug — fix is to power cycle and reconnect). Members can also occasionally fall out of sync with each other, sometimes self-correcting after a few seconds, sometimes requiring a restart.

Given your Home Assistant and MIDI interests, Jim, these could be a fun integration target — the BLE MIDI connection means you could theoretically trigger them from an automation or script if you had a BLE MIDI bridge set up. The nRF52840 SoC and that unexplored CDC-ACM serial port are especially tempting from a hacking perspective.