# Especificación de Proyecto: Juego Educativo de Matemáticas (Pygame)

## 1. Resumen del Proyecto
Desarrollar una aplicación de escritorio interactiva en Python usando `pygame` para que un niño practique operaciones matemáticas fundamentales. La aplicación no es solo un generador de preguntas, sino un sistema adaptativo que rastrea el tiempo de respuesta y la precisión para identificar áreas de mejora y ajustar la dificultad.

**Público Objetivo:** Niño en etapa escolar (práctica de sumas/restas de 2 dígitos y tablas de multiplicar/dividir del 1 al 10).
**Stack Tecnológico:** Python 3.x, `pygame` (interfaz y lógica del juego), `sqlite3` o `json` (almacenamiento de datos locales).

---

## 2. Requisitos Funcionales

### A. Tipos de Operaciones
1.  **Sumas y Restas:** Exclusivamente con números de 1 y 2 dígitos (ej. 15 + 8, 42 - 19).
2.  **Multiplicaciones:** Basadas estrictamente en las tablas del 1 al 10 (ej. 7 * 8).
3.  **Divisiones:** Inversas exactas de las tablas de multiplicar del 1 al 10. 
    *   *Regla de implementación para divisiones:* Generar $A \in [1,10]$ y $B \in [1,10]$. Calcular $C = A * B$. La pregunta a mostrar debe ser $C \div A = ?$ para garantizar un resultado entero exacto ($B$).

### B. Progresión y Dificultad Dinámica
El sistema debe tener 3 niveles de dificultad que afectan la generación de números:
*   **Nivel 1:** Sumas/Restas sin llevar/prestar (ej. 45 + 12). Multiplicaciones/Divisiones de las tablas del 1 al 5.
*   **Nivel 2:** Sumas/Restas llevando en unidades. Multiplicaciones/Divisiones de las tablas del 6 al 8.
*   **Nivel 3:** Sumas/Restas complejas de 2 dígitos. Tablas del 9 y 10. Operaciones mezcladas.

### C. Sistema de Tracking y Refuerzo (Spaced Repetition)
Se debe registrar cada intento del usuario.
*   **Datos a guardar por pregunta:** Tipo de operación, string de la pregunta, respuesta correcta, respuesta del usuario, booleano de acierto/fallo, y **tiempo de respuesta en milisegundos**.
*   **Lógica de Refuerzo:** El generador de preguntas debe leer el historial. Si el usuario falla consistentemente en una operación específica (ej. $7 * 8$) o tarda mucho (ej. > 5 segundos), el sistema debe aumentar la probabilidad (ej. 30%) de que esa operación vuelva a aparecer en la sesión actual o futura para reforzar el aprendizaje.

### D. Interfaz Gráfica (Pygame)
*   **HUD (Arriba):** Nivel actual, puntuación/estrellas, y una barra de progreso de la sesión actual.
*   **Pizarra (Centro):** Texto grande y legible mostrando la operación (ej. "45 + 27 = ?").
*   **Input (Abajo):** Captura de teclado. El usuario debe poder escribir números y borrar con `Backspace`. Se evalúa al presionar `Enter`.
*   **Feedback Inmediato:** 
    *   *Acierto:* Sonido de éxito, color verde intermitente, suma puntos.
    *   *Fallo:* Sonido de error, efecto visual de "temblor" (shake) en la pantalla, muestra la respuesta correcta en rojo por 2 segundos antes de continuar.

---

## 3. Arquitectura del Código Requerida

El código debe estar estructurado usando Programación Orientada a Objetos (POO) y seguir el patrón de **Máquina de Estados**.

*   `DatabaseManager`: Clase encargada de leer/escribir en SQLite/JSON y calcular promedios de tiempo y tasas de error.
*   `QuestionGenerator`: Clase que genera las preguntas basándose en el nivel actual y consultando al `DatabaseManager` para aplicar la lógica de refuerzo.
*   `GameStateManager`: Administra las transiciones entre `MenuState` (inicio), `PlayState` (bucle principal de juego), y `SummaryState` (estadísticas al final de una ronda).
*   `UIElement`: Clases base para renderizar texto, botones y la caja de input numérico.

---

## 4. Instrucciones de Implementación para el Agente IA

Actúa como un Desarrollador Python Senior. Por favor, implementa este proyecto en fases. Detente y pide mi aprobación al final de cada fase antes de continuar.

*   **Fase 1: Motor Lógico y Base de Datos.** Crea el `DatabaseManager` y el `QuestionGenerator`. Escribe tests simples (usando `print` o `unittest`) para demostrar que las preguntas se generan correctamente según el nivel, que las divisiones son exactas, y que el historial afecta la generación futura.
*   **Fase 2: Motor Gráfico Base.** Crea la estructura básica de `pygame` con la Máquina de Estados, el bucle principal a 60 FPS, y un sistema robusto para la captura de texto (Input Box) numérico.
*   **Fase 3: Integración y Pulido.** Conecta el motor lógico con el gráfico. Añade animaciones de feedback (verde para éxito, rojo/shake para error) y sonidos generados proceduralmente (o placeholders para archivos `.wav`). Crea la pantalla de estadísticas finales.

Empieza ahora con la **Fase 1**, generando el código para el modelo de datos y la generación matemática.