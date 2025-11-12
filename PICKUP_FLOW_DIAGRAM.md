# RepartidorIA Pickup & Exit Flow Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      RepartidorIA (extends Repartidor)         │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ├─ Hard Mode (A* + TSP)
                                  ├─ Medium Mode (Greedy Best-First)
                                  └─ Easy Mode (Random)
                                  
┌─────────────────────────────────────────────────────────────────┐
│                    Main Update Cycle                             │
├─────────────────────────────────────────────────────────────────┤
│  1. actualizar_IA(lista_paquetes, limites)                      │
│  2. mover_hacia_objetivo(limites)                               │
│  3. update_sliding(delta_time)                                  │
│                                                                   │
│  These call:                                                     │
│  - calcular_ruta_optima() [hard mode]                           │
│  - mover_greedy_best_first() [medium mode]                      │
│  - mover_aleatorio() [easy mode]                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pickup Flow (Detailed Sequence)

```
START: IA at position (x, y) ≠ package
       │
       ├─ Move toward package using pathfinding
       │  └─ Hard: A* → Dijkstra → route list
       │  └─ Medium: Greedy best-first scoring
       │  └─ Easy: Random direction
       │
       v
IA reaches package tile (x=p.x, y=p.y)
       │
       ├─ Next game tick calls mover_hacia_objetivo()
       │  └─ Detects: pos_x == target_x AND pos_y == target_y
       │  └─ AND paquete.recogido == False
       │
       v
Call _attempt_pickup() [FIRST TIME]
       │
       ├─ Check: objetivo_actual exists?  → YES
       ├─ Check: _pickup_wait_start set? → NO
       │  │
       │  └─ Record: _pickup_wait_start = pygame.time.get_ticks()
       │  └─ Return: False (still waiting)
       │
       └─ IA stays on tile (no movement)

[TIME PASSES: ~2000 milliseconds]

Next game tick calls _attempt_pickup() [SECOND TIME]
       │
       ├─ Check: objetivo_actual exists?  → YES
       ├─ Check: _pickup_wait_start set? → YES
       ├─ Calculate: elapsed = now - _pickup_wait_start
       │
       ├─ elapsed < pickup_wait_ms (2000)?
       │  └─ YES: Return False (still waiting)
       │
       └─ elapsed >= 2000ms → PROCEED TO PICKUP
              │
              v
         Call: ok = self.recoger_paquete(paquete)
              │
              ├─ Base class checks: inventario.peso_total() + paquete.peso <= pesoMaximo?
              │  │
              │  ├─ YES: inventario.agregar(paquete) → return True
              │  └─ NO:  [skip add] → return False
              │
              v
         IF ok == True:
              │
              ├─ Set: paquete.recogido = True ✓ INVENTORY & RECOGIDO SYNCED
              ├─ Log: "[IA PICKUP-SUCCESS] codigo={paquete.codigo} pos=({pos_x},{pos_y})"
              ├─ Reset: _pickup_wait_start = None
              ├─ Return: True
              │
              └─ PROCEED TO EXIT HANDLING
                     │
                     v
                 Check: Is objetivo in building? (tipo == 'B')
                     │
                     ├─ YES: 
                     │   │
                     │   ├─ Call: exit_route = _build_exit_route_from_stack()
                     │   │   │
                     │   │   └─ Returns: [interior_stack_reversed] + [door] + [street_tile]
                     │   │
                     │   ├─ Set: self.ruta_actual = exit_route
                     │   ├─ Set: self.needs_to_exit = True
                     │   ├─ Set: self._inside_building = False
                     │   ├─ Set: self._popping_building_stack = True
                     │   └─ Log: "[IA PICKUP] ... exit_route length={len(exit_route)}"
                     │
                     └─ NO: 
                         └─ Done! Move to next objective
         
         IF ok == False:
              │
              ├─ paquete.recogido STAYS False ✗ (not set)
              ├─ Log: "[IA PICKUP-FAIL] peso={paquete.peso} inv_peso={inventario.peso_total()} max={pesoMaximo}"
              ├─ Set: _need_replan = True
              ├─ Reset: _pickup_wait_start = None
              ├─ Return: False
              │
              └─ Next tick: replanning triggered
                     └─ IA will find new objective or drop packages

END: Package picked up (recogido=True) and in inventory, OR failed with replan
```

---

## Exit Route Building (Detailed)

```
_build_exit_route_from_stack() Call
       │
       v
Input Data:
  - self._building_path_stack    [list of interior tiles visited]
  - self._building_entry_door    [door tile where entered]
  - self._building_exit_street_tile [street tile outside door]
  - self.pos_x, self.pos_y       [current position]
       │
       v
Step 1: Reverse interior path
       │
       ├─ If _building_path_stack = [(10,5), (10,6), (10,7)]
       └─ Reversed = [(10,7), (10,6), (10,5)]
              │
              v
Step 2: Append entry door
       │
       ├─ If _building_entry_door = (10,4)
       └─ Path now = [(10,7), (10,6), (10,5), (10,4)]
              │
              v
Step 3: Append exit street tile
       │
       ├─ If _building_exit_street_tile = (10,3)
       ├─ Check: not already at end?
       └─ Path now = [(10,7), (10,6), (10,5), (10,4), (10,3)] ✓ ENDS ON STREET
              │
              v
Step 4: Trim current position
       │
       ├─ If current pos = (10,7) and path[0] = (10,7)
       └─ Path now = [(10,6), (10,5), (10,4), (10,3)] ✓ AVOIDS STAYING
              │
              v
Output: Final exit route = [(10,6), (10,5), (10,4), (10,3)]
        └─ Ready to be assigned to self.ruta_actual for exit
```

---

## Building Interior Navigation

```
IA Enters Building via Door
       │
       ├─ Enters update_sliding()
       ├─ Detects: prev_tipo != 'B' AND cur_tipo == 'B'
       │   │
       │   ├─ Initialize: _building_path_stack = [(cur_x, cur_y)]
       │   ├─ Set: _inside_building = True
       │   ├─ Record: _building_entry_door = prev position
       │   │
       │   └─ Find adjacent street tile:
       │       ├─ Search 4-neighbors of door
       │       ├─ First 'C' type (street) and not blocked
       │       └─ Set: _building_exit_street_tile = (street_x, street_y)
       │
       v
IA Moves Deeper into Building
       │
       ├─ Each move: update_sliding() detects prev_tipo == 'B' AND cur_tipo == 'B'
       ├─ Action: _building_path_stack.append((cur_x, cur_y))
       │
       └─ Stack records all interior tiles visited
              │
              ├─ Example stack after 3 steps inside:
              │  [(entry_y, entry_x), (move1_x, move1_y), (move2_x, move2_y)]
              │
              v
IA Reaches Package & Picks Up
       │
       ├─ _attempt_pickup() succeeds
       ├─ _build_exit_route_from_stack() creates path:
       │  └─ Reverse stack + door + street_tile
       │
       v
IA Starts Exit
       │
       ├─ Follows ruta_actual (exit route)
       ├─ Each tile:  interior → interior → door → street ✓
       │
       v
IA Exits Building
       │
       ├─ Reaches street tile outside building
       ├─ All interior data cleared:
       │  ├─ _building_path_stack = []
       │  ├─ _building_entry_door = None
       │  ├─ _building_exit_street_tile = None
       │  └─ _inside_building = False
       │
       └─ Ready for next objective
```

---

## State Machine: Pickup & Exit

```
States:
┌─────────────────────────────────────────┐
│  MOVING_TO_PACKAGE                      │
│  (following route toward objective)     │
└─────────────────────────────────────────┘
                  │
        (reached package tile)
                  │
                  v
┌─────────────────────────────────────────┐
│  WAITING_FOR_PICKUP (2000ms timer)      │
│  (standing on package, waiting)         │
└─────────────────────────────────────────┘
                  │
        (timer elapsed, try pickup)
                  │
        ┌─────────┴─────────┐
        │                   │
    (success)           (fail)
        │                   │
        v                   v
┌──────────────────┐  ┌──────────────────┐
│  EXITING         │  │  REPLANNING      │
│  BUILDING        │  │  (replan=True)   │
│  (if inside)     │  │                  │
└──────────────────┘  └──────────────────┘
        │                   │
        ├─ Reverse stack   │
        ├─ Include door    │
        ├─ End on street   │
        │                   │
        v                   │
┌──────────────────┐        │
│  MOVING_TO_      │        │
│  DELIVERY        │<───────┘
│  or NEXT         │
│  OBJECTIVE       │
└──────────────────┘
```

---

## Key Variables & Lifecycle

### Pickup Wait Variables
```
_pickup_wait_start: int | None
  - Set when _attempt_pickup() first called
  - Used to calculate elapsed time
  - Reset to None after pickup attempt
  - Lifecycle: None → timestamp → None

pickup_wait_ms: int = 2000
  - Configurable wait time (default 2 seconds)
  - Never changes after __init__
  - Used in: _attempt_pickup() comparison
```

### Building Navigation Variables
```
_building_path_stack: list[(x, y)]
  - Records interior tiles visited
  - Growing: each interior tile added
  - Used for: exit route reversal
  - Cleared: when exiting building

_building_entry_door: (x, y) | None
  - Records door used to enter
  - Set once when entering
  - Appended to exit route
  - Cleared when exiting

_building_exit_street_tile: (x, y) | None
  - Records street tile outside door
  - Set when entering (searching neighbors)
  - Appended to exit route
  - Ensures exit ends on street (not door)
  - Cleared when exiting

_inside_building: bool
  - True: currently inside building
  - Used: to control stack recording
  - Set: when entering ('C' → 'B')
  - Reset: when exiting ('B' → 'C')

_popping_building_stack: bool
  - True: currently exiting interior
  - Used: to signal exit route mode
  - Set: when preparing exit
  - Reset: when exit complete
```

---

## Error Handling

```
recoger_paquete() fails
  ├─ Reason 1: Inventory weight limit (most common)
  │  └─ Fix: Drop items or deliver current packages first
  │
  ├─ Reason 2: Package already in inventory
  │  └─ Fix: Check for duplicates
  │
  ├─ Reason 3: Unexpected exception
  │  └─ Fix: Exception caught in try-except block
  │
  └─ Action: _need_replan = True triggers replanning
           └─ IA avoids stuck state

_build_exit_route_from_stack() returns None
  ├─ Reason: No interior stack recorded
  │  └─ Fallback: Use find_door_for_building()
  │
  └─ Action: Less optimal but IA still exits
```

---

## Performance Characteristics

```
Operation                    Complexity    Typical Time
─────────────────────────────────────────────────────
_attempt_pickup()            O(1)          < 1ms
_build_exit_route_from_stack() O(n)        < 5ms (n ≈ interior tiles)
recoger_paquete()            O(1)          < 1ms
Pickup delay (2000ms)        Timer         2000ms (game logic, not CPU)

Total overhead: Negligible for game performance
```

---

## Debug Output Examples

```
# Successful pickup outside building
[IA PICKUP-SUCCESS] codigo=PKG_001 pos=(15,10)

# Successful pickup inside building with exit
[IA PICKUP] pos=(15,10) building_stack=[(15,11), (15,12)] entry_door=(15,13) exit_route=[(15,12), (15,11), (15,13), (16,13)] ruta_actual_len=4
[IA PICKUP-SUCCESS] codigo=PKG_002 pos=(15,10)

# Failed pickup due to inventory
[IA PICKUP-FAIL] codigo=PKG_003 peso=1.5 inv_peso=5.0 max=5

# Route calculation issue
[IA ROUTE-FAIL] pos=(5,5) objetivo=PKG_004 target=(18,18) building_stack=None

# General debug tick
[IA DEBUG] t=123456 pos=(10,5) objetivo=PKG_005 ruta_len=8 need_replan=False active_pkgs=2
```

---

## Summary

**The refactored system ensures:**
1. ✓ Pickup waits 2 seconds (realistic)
2. ✓ Inventory check before recogido flag (no state mismatch)
3. ✓ Exit routes include street tile (IA ends on street, not door)
4. ✓ Failure triggers replan (no stuck states)
5. ✓ Single implementation (100% code reuse)
6. ✓ Clear debug logging (easy troubleshooting)

**Result:** Reliable, debuggable, and maintainable AI pickup system.
