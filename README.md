# 🔢 Contador Mecánico de Unidades (Valor Posicional)

Aplicación de escritorio interactiva para niños diseñada para comprender e interiorizar el sistema decimal y las unidades de valor posicional (**CM, DM, UM, C, D, U**).

Compatible con **Linux** y **macOS**.

---

## 🚀 Cómo ejecutar la aplicación

### En Linux:
```bash
./run.sh
```
*(o `python3 main.py`)*

### En macOS:
Haz doble clic en el archivo **`run_mac.command`** desde el Finder, o ejecuta:
```bash
./run_mac.command
```

---

## 🎨 Características Principales

1. **Diseño fiel al odómetro mecánico 3D**:
   - **Clase de los Miles**: Encabezados en naranja cálido (**CM, DM, UM**).
   - **Clase de las Unidades**: Encabezados en blanco puro (**C, D, U**).
   - **Separador de Miles**: Punto de miles (`.`) y esfera amarilla ubicada entre **UM** y **C** cuando la cifra es $\ge 1.000$.
   - **Flechas interactivas**: Triángulos superiores (▲) e inferiores (▼) en azul petróleo.

2. **Rotación Independiente de Cilindros**:
   - Únicamente rueda el cilindro cuyo dígito cambia. Al alterar las Unidades, las decenas y centenas permanecen estáticas.
   - En acarreos ($9 \to 10$), solo ruedan las columnas involucradas.

3. **Ceros a la Izquierda Ocultos (Desaparición de Spots)**:
   - Para cifras como `3.245`, las columnas **CM** y **DM** desaparecen automáticamente para evitar confusiones (`003245`).
   - En la descomposición aditiva desaparecen los términos con 0: $100.000 + 3.000 + 200 + 40 + 5$.
   - Botón **`+ Columna`** para activar la siguiente unidad superior directamente.
   - Interruptor **`Ceros Izq: Ocultos / Visibles`** para personalizar la visualización.

4. **Voz Humana Natural en Español**:
   - **En Linux**: Motor de voz neural natural en español con sistema de caché local instantáneo.
   - **En macOS**: Detección y uso automático de las voces neurales de Siri en español (Mónica, Paulina, Jorge).
   - Botón **`🔊 Escuchar cómo se lee`** para pronunciar números con entonación fluida y amigable para niños.

5. **Modo Desafíos y Retos Matemáticos**:
   - Retos interactivos con acumulación de estrellas (★): formar números, cambiar dígitos específicos o sumar decenas y centenas.
