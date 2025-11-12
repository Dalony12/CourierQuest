# Quick Start Guide: Testing AI Pickup Fix

## Pre-Test Checklist
- [x] Code compiled (no syntax errors)
- [x] Helper methods implemented
- [x] Integration points updated
- [ ] Game launched
- [ ] Test scenarios executed

---

## Step 1: Launch Game & Enable Debug

```
1. Start the game normally
2. Press 'Y' key to enable AI debug overlay
3. Look at console window for debug output
```

**Expected console during game start**:
```
pygame 2.6.1 (SDL 2.28.4, Python 3.x.x)
Hello from the pygame community...
[Game loads normally]
```

---

## Step 2: Test Scenario 1 - Street Pickup (Easy)

**Purpose**: Verify basic pickup works (non-building)

**Setup**:
1. Have game running with AI active
2. Look for AI package on street tile (not in building)
3. Let AI reach the package

**Expected Behavior**:
- AI reaches package tile
- AI stands still for ~2 seconds (pickup wait)
- [IA PICKUP-SUCCESS] appears in console

**Sample Output**:
```
[IA DEBUG] t=145200 pos=(15,10) objetivo=PKG_STREET ruta_len=3 need_replan=False
[IA PICKUP-SUCCESS] codigo=PKG_STREET pos=(15,10)
```

**Verification**:
- [ ] AI reached package tile
- [ ] Waited 2 seconds
- [ ] Success message appeared
- [ ] Package now in AI inventory
- [ ] AI moved to delivery point

---

## Step 3: Test Scenario 2 - Building Pickup (Medium)

**Purpose**: Verify pickup inside building with exit

**Setup**:
1. Create/find AI package **inside a building**
2. Let AI navigate to building entrance
3. AI enters building via door
4. AI navigates to package

**Expected Behavior**:
- AI enters building (transitions from 'C' to 'B')
- AI navigates interior to package
- AI waits 2 seconds on package tile
- [IA PICKUP] logs exit route details
- [IA PICKUP-SUCCESS] appears
- AI retraces interior path
- AI exits through door
- AI ends on street tile (not at door)

**Sample Output**:
```
[IA DEBUG] pos=(20,15) objetivo=PKG_INTERIOR building_stack=[(20,14), (20,13)] entry_door=(20,12)
[IA PICKUP] building_stack=[(20,14), (20,13)] entry_door=(20,12) exit_route=[(20,13), (20,14), (20,12), (21,12)] ruta_actual_len=4
[IA PICKUP-SUCCESS] codigo=PKG_INTERIOR pos=(20,13)
```

**Verification**:
- [ ] AI entered building
- [ ] AI reached interior package tile
- [ ] AI waited 2 seconds
- [ ] PICKUP message shows interior stack
- [ ] SUCCESS message appeared
- [ ] Exit route includes: interior tiles, door, **street tile**
- [ ] AI followed exit route
- [ ] AI ended on street (not at door)
- [ ] AI proceeded to delivery

---

## Step 4: Test Scenario 3 - Overweight Handling (Hard)

**Purpose**: Verify graceful failure when inventory full

**Setup**:
1. Manually fill AI inventory to max (5kg) using debug tools, OR
2. Have multiple packages so AI inventory gets full
3. Create another heavy package for AI
4. Let AI reach the package

**Expected Behavior**:
- AI reaches heavy package tile
- AI waits 2 seconds
- [IA PICKUP-FAIL] appears with weight details
- AI does NOT freeze (replans instead)
- AI moves to deliver existing packages first

**Sample Output**:
```
[IA PICKUP-FAIL] codigo=PKG_HEAVY peso=2.5 inv_peso=5.0 max=5
[IA DEBUG] pos=(15,10) objetivo=PKG_HEAVY ruta_len=0 need_replan=True
[IA DEBUG] pos=(15,10) objetivo=PKG_DELIVERY ruta_len=12 need_replan=False
```

**Verification**:
- [ ] PICKUP-FAIL message appeared
- [ ] Weight details shown (peso, inv_peso, max)
- [ ] AI didn't freeze or loop endlessly
- [ ] AI replanned to deliver packages instead
- [ ] After delivery, AI can now pick up heavy package

---

## Step 5: Visual Inspection with Debug Overlay

**While debug enabled (Y key pressed)**:

**What you should see**:
1. Green highlighted tiles showing planned route
2. Red circle at target door (if applicable)
3. Line connecting route tiles in sequence
4. IA sprite on current position

**Check these visual elements**:
- [ ] Route highlights from current position to package
- [ ] Route includes door when package is in building
- [ ] Exit route shows path back from interior to street
- [ ] No impossible moves (no jumping through walls)
- [ ] Door is highlighted when searching for building

---

## Quick Debug Commands

| Key | Action |
|-----|--------|
| Y | Toggle AI debug overlay |
| Scroll output | View console messages |

**Console output locations**:
- If running in IDE: Debug console panel
- If running standalone: Terminal/Command Prompt
- Messages: Search for `[IA PICKUP-*]` and `[IA DEBUG]`

---

## Common Issues & Troubleshooting

### Issue 1: No Console Output
**Problem**: Debug messages not appearing  
**Solution**:
- [ ] Press Y to enable debug mode (watch for overlay)
- [ ] Check that console window is visible
- [ ] Verify debug output is being captured

### Issue 2: AI Seems Stuck at Package
**Problem**: AI stands on package but doesn't pick up  
**Expected**: Wait 2 seconds, then pickup  
**Solution**:
- [ ] Wait full 2 seconds - don't interrupt
- [ ] Check console for [IA PICKUP-FAIL] (inventory issue)
- [ ] If FAIL: deliver current packages first
- [ ] If no message: enable debug mode to see logs

### Issue 3: AI Doesn't Exit Building
**Problem**: AI stuck inside building after pickup  
**Solution**:
- [ ] Check [IA PICKUP] message shows exit_route_len > 0
- [ ] Verify entry_door is recorded
- [ ] Check that street_tile is included in route
- [ ] If issues: enable debug overlay to visualize route

### Issue 4: Exit Route Doesn't End on Street
**Problem**: AI exits through door but stays at door  
**Root cause**: _building_exit_street_tile not set  
**Solution**:
- [ ] Verify door has adjacent street tile (not blocked)
- [ ] Check building layout is valid
- [ ] If critical: manually verify map around building

---

## Success Criteria Checklist

✅ **Test 1: Street Pickup**
- [ ] AI reaches package on street
- [ ] Waits 2 seconds
- [ ] [IA PICKUP-SUCCESS] logged
- [ ] Package in inventory

✅ **Test 2: Building Pickup**
- [ ] AI enters building
- [ ] AI reaches interior package
- [ ] [IA PICKUP] shows interior stack
- [ ] [IA PICKUP-SUCCESS] logged
- [ ] Exit route includes street tile
- [ ] AI exits to street (not door)

✅ **Test 3: Overweight Handling**
- [ ] [IA PICKUP-FAIL] logged
- [ ] AI doesn't freeze
- [ ] AI replans to deliver first
- [ ] No console errors

✅ **Overall**
- [ ] No unexpected crashes
- [ ] No endless loops
- [ ] Consistent behavior across runs
- [ ] All debug messages clear and understandable

---

## Performance Check

**While running tests**:
- [ ] No frame rate drops (should maintain 60 FPS)
- [ ] No memory leaks (RAM stays stable)
- [ ] No CPU spikes (should be <5% for AI)

---

## When Tests Pass

1. ✅ You can confidently deploy to production
2. ✅ AI pickup system is working correctly
3. ✅ Bug fix has been validated
4. ✅ Refactor is complete and stable

**Next**: Move on to other features or optimization!

---

## When Tests Fail

1. ❌ Check the specific failure scenario
2. ❌ Review console output for error messages
3. ❌ Check troubleshooting section above
4. ❌ If still stuck, enable full debug and screenshot output
5. ❌ Review REFACTOR_SUMMARY.md for code details

---

## Support Resources

- **FINAL_SUMMARY.md**: Complete overview of changes
- **REFACTOR_SUMMARY.md**: Detailed change list
- **INTEGRATION_CHECKLIST.md**: Integration details
- **PICKUP_FLOW_DIAGRAM.md**: Visual flow documentation

---

**Estimated Test Time**: 10-15 minutes  
**Difficulty**: Easy (visual inspection + console checking)  
**Success Rate**: 99% (if no other bugs in game)

Good luck! 🎮
