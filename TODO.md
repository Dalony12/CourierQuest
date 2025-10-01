# TODO for Sound Effects Implementation

- [x] Set volume to 0.1 for all sound effects in game_loop.py
- [x] Add bicycle_playing flag to track if bicycle sound is playing
- [x] Modify bicycle sound logic: loop when moving and not inside building, stop otherwise
- [x] Test the changes in the game
- [ ] Implement wind sound: activate when weather is adverse (clouds, rain_light, rain, storm, fog, heat, cold, wind), vary volume, stop when not
- [ ] Implement walk sound: loop when moving inside building (on B tiles), stop otherwise
- [ ] Implement victory sound: play once when player wins
- [ ] Implement cansado sound: loop while resistencia < 30
