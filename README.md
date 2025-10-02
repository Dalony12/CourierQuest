# 📌 Proyecto#1: CourierQuest
**Curso:** EIF207 - Estructuras de Datos (2025-II)  
**Universidad Nacional - Escuela de Informática**

## 📖 Descripción
CourierQuest es un proyecto académico desarrollado en Python, utilizando una librería especializada en desarrollo de videojuegos (Pygame). El juego simula la experiencia de un repartidor urbano que debe aceptar y completar pedidos dentro de una ciudad dinámica y cambiante.

La persistencia de datos se realiza mediante **archivos JSON, Binario**.

---

## 🎯 Objetivos
- Implementar	y	justificar	el	uso	de	estructuras	de	datos	lineales
- Practicar	el	manejo	de	archivos	en	múltiples	formatos (JSON,	texto,	binario)
- Aplicar	algoritmos	de	ordenamiento en	escenarios	reales
- Desarrollar	un	videojuego	con	Python	y	Arcade/Pygame/cocos2d
- Integrar	un	API	real y	gestionar	caché	para	trabajar	en	modo	offline
- Diseñar	un	bucle	de	juego	consistente	con	 reglas	cuantificables	 (clima,	 reputación,	
resistencia)

---

## 🧱 Estructuras de Datos Utilizada

**Matrices**
  - En backend/clima.py: Se implementa una matriz de transición de Markov representada mediante un diccionario (matriz_markov). Cada clave corresponde a un estado climático y su valor es una tupla que asocia los estados de destino con las probabilidades de transición respectivas. Este enfoque permite modelar de manera probabilística la dinámica del clima en el entorno del juego.

  - En backend/mapa.py: El escenario se representa a través de una matriz bidimensional, la cual se estructura como una lista de listas (self.tiles_raw) que contiene los tiles del mapa. Asimismo, se   utiliza self.celdas, otra matriz bidimensional compuesta por objetos de tipo Celda, lo que permite añadir propiedades específicas a cada unidad espacial del entorno.

**Vectores**

Las listas de Python cumplen el rol de vectores en distintas partes del programa. Entre sus aplicaciones se destacan:
  - active_paquetes (core/game_loop.py), que almacena los paquetes activos en el juego.
  - pedido_queue (core/game_loop.py), que simula una cola de pedidos en proceso.
  - Listas de partículas tales como rain_particles y snow_particles, utilizadas en la representación de fenómenos climáticos.

**Colas**

Las colas se utilizan para gestionar procesos en orden secuencial bajo la política FIFO (First In, First Out):
  - En core/game_loop.py, la lista pedido_queue se manipula como cola, añadiendo elementos con append() y retirándolos mediante pop(0).
  - En frontend/hud.py, se implementa el algoritmo de BFS (Breadth-First Search) mediante collections.deque en el método find_path(), para la búsqueda de caminos en el minimapa.
  - En backend/mapa.py, collections.deque también es utilizado en el método _crear_celdas() para la agrupación de edificios mediante BFS, así como en find_path() para la búsqueda de trayectorias en el mapa.

---

## 🔃 Algoritmos de Ordenamient

**Merge Sort**
- Implementación: Localizada en core/sorting.py bajo la función merge_sort(arr, key_func). Este algoritmo recursivo divide un arreglo en mitades, las ordena de manera independiente y posteriormente realiza un proceso de fusión ordenada, además, se utilizó en persistencia/puntajes.py bajo la función merge_sort_puntajes(lista). Del mismo modo ordena los resultados del mayor al menor, permitiendo ver los mejores resultados.

- Aplicación: En core/game_loop.py, se utiliza para ordenar la lista active_paquetes de acuerdo con el tiempo límite de entrega y el código del paquete:
merge_sort(game.active_paquetes, lambda p: (p.tiempo_limite, p.codigo))

**Heap Sort**
- Implementación: Definida en core/sorting.py mediante la función heap_sort(arr, key_func). Se apoya en la librería heapq para construir un min-heap a partir de una función de clave y posteriormente extraer los elementos en orden.

- Aplicación: En core/game_loop.py, se emplea para ordenar los paquetes activos de acuerdo con la prioridad (en orden descendente) y el código asociado:
heap_sort(game.active_paquetes, lambda p: (-(p.priority or 0), p.codigo))


## 👥 Autores

- Javier Garita Granados - [@JavierGarita](https://github.com/Dalony12)
- Josue Peñaranda Alvarado - [@JosuePenaranda](https://github.com/JosuePenaranda)
