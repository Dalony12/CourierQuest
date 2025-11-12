# TODO: Solucionar problemas de entrada a edificios y wall-following en RepartidorIA

## Problemas identificados
- El repartidor IA no identifica correctamente las puertas ("D") para entrar a edificios cuando el objetivo está dentro ("B" o "3").
- Se queda pegado en wall_following alrededor de obstáculos sin poder entrar al edificio.
- Wall-following puede entrar en loops en esquinas.

## Estrategia de solución
1. **Modificar cálculo de rutas para objetivos en edificios**: Siempre calcular ruta a la puerta primero si el objetivo está en edificio, luego al objetivo interno.
2. **Mejorar wall_following**: Priorizar puertas adyacentes y forzar giros en esquinas para evitar loops.
3. **Asegurar entrada a edificios**: Permitir movimiento a "B" desde "D" sin restricciones adicionales.
4. **Fallback robusto**: Si wall_following falla, usar Dijkstra a la puerta.

## Tareas Pendientes
- [ ] Modificar `calcular_ruta_optima` para incluir ruta a puerta si objetivos en edificio.
- [ ] Actualizar `mover_hacia_objetivo` para priorizar ruta a puerta antes de objetivo interno.
- [ ] Mejorar `mover_wall_following` para detectar y priorizar puertas adyacentes.
- [ ] Ajustar lógica de giros en esquinas en wall_following para evitar loops.
- [ ] Probar en juego: verificar que IA entre a edificios por puertas y no se pegue en wall-following.
- [ ] Ajustar si surgen nuevos problemas.

## Notas
- Usar `find_door_for_building` para localizar puertas.
- Reconstruir grafo cuando cambie `allow_enter_building`.
- Limitar wall-following a 30 pasos, luego fallback a Dijkstra a puerta.
