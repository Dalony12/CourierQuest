# TODO: Optimizar RepartidorIA para rutas por puertas y wall-following

## Tareas Pendientes
- [ ] Modificar `construir_grafo` para restringir aristas a 'B' solo desde 'D' o 'B'
- [ ] Mejorar `mover_wall_following` para evitar loops en esquinas (limitar pasos, forzar giros)
- [ ] Modificar `mover_hacia_objetivo` para calcular ruta a puerta primero para objetivos internos
- [ ] Asegurar salida completa a calle ('0') después de puerta
- [ ] Probar en juego: ruta pasa por 'D', entra a 'B', llega a '3', sale a '0', wall-following no loops
- [ ] Ajustar si problemas en esquinas o rutas

## Notas
- Tipos: '0'=calle, 'B'=edificio interior, 'D'=puerta, '3'=destino interno
- Reconstruir grafo cuando cambie allow_enter_building
- Limitar wall-following a 30 pasos, luego resetear
