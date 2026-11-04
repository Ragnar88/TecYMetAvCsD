# Propuesta comercial: modelos predictivos de WTI y Brent

14 diapositivas · Audiencia: responsables de compras y finanzas · Duración sugerida: 12–15 minutos

**Idea central:** el cambio entre períodos exige revisar los supuestos de compra. Holt amortiguado y ARIMA aportan estimaciones contrastables para un piloto que mida su valor económico.

**Base documental:** precios spot del CSV EIA del proyecto hasta el 14/10/2026 y resultados guardados en los notebooks. Marzo de 2026 se excluye por diseño. Los períodos tienen distinta duración y la comparación no establece causalidad. El piloto, el uso conjunto y los ejemplos económicos son propuestas, no resultados de despliegue.

## Bloque 1. Agitación y contexto

### 1. El presupuesto enfrenta un mercado que cambió

**Guion del presentador**

“Quiero empezar por una decisión concreta: cuánto comprar la próxima semana y con qué presupuesto. Cuando el mercado cambia, una referencia que antes resultaba razonable puede dejar de representar el riesgo. Nuestro trabajo parte de esa tensión: entender qué cambió y convertir esa evidencia en una mejor preparación de la compra.”

**Contenido visual y puntos clave**

Subtítulo: Decisiones semanales de compra de petróleo con evidencia
Visual: portada minimalista, sin mencionar aún los modelos.

### 2. Los dos períodos exigen supuestos distintos

**Guion del presentador**

“Separé el análisis en dos períodos porque promediar toda la historia oculta diferencias relevantes. El primero va de enero de 2024 a febrero de 2026. El segundo empieza en abril de 2026 y, en nuestra copia, llega al 14 de octubre. Marzo queda excluido. Los precios medios subieron alrededor de 30% en WTI y 36% en Brent. Es una comparación histórica, sin atribución causal.”

**Contenido visual y puntos clave**

Mostrar línea temporal con Período 1 y Período 2 separados por marzo excluido. Tabla de precio promedio, USD/barril: WTI P1 70,37, P2 91,68, variación +30,3%; Brent P1 74,34, P2 101,39, variación +36,4%. Pie: comparación descriptiva, períodos de distinta duración; fuente CSV EIA del proyecto, corte 14/10/2026.

### 3. La volatilidad aumentó más del doble

**Guion del presentador**

“La diferencia más importante aparece en los movimientos entre cotizaciones. La volatilidad de WTI se multiplicó por 2,13 y la de Brent por 2,48. Para compras, esto significa que un margen de presupuesto razonable en el primer período merece una revisión en el segundo. El precio promedio ayuda a dimensionar el costo. La volatilidad ayuda a dimensionar la incertidumbre.”

**Contenido visual y puntos clave**

Gráfico de columnas con desvío estándar muestral de retornos entre cotizaciones consecutivas, en puntos porcentuales, no anualizado: WTI P1 1,91 y P2 4,07; Brent P1 1,83 y P2 4,55. Destacar multiplicadores WTI 2,13 veces, Brent 2,48 veces. Aclarar: cada retorno puede abarcar más de un día calendario.

### 4. La brecha entre Brent y WTI también se amplió

**Guion del presentador**

“También encontré un cambio en la relación entre ambas referencias. La diferencia promedio pasó de 3,94 a 10,13 dólares por barril. Por eso analizar cada crudo por separado aporta valor a quien tiene contratos indexados a referencias distintas. El presupuesto puede desviarse tanto por el movimiento general del mercado como por la evolución de esa brecha.”

**Contenido visual y puntos clave**

Comparación del spread promedio Brent menos WTI en fechas comunes: P1 3,94 USD/barril, P2 10,13 USD/barril, diferencia +6,19 USD/barril, 2,57 veces. Pie: 529 fechas comunes en P1 y 135 en P2.

### 5. Un desvío pequeño por barril pesa en el presupuesto

**Guion del presentador**

“Para llevarlo al negocio, tomo un ejemplo hipotético. En una operación de cien mil barriles, un desvío de cinco dólares por barril cambia el presupuesto en quinientos mil dólares. Ese monto muestra la exposición. La oportunidad comercial consiste en evaluar cuánto puede mejorar la decisión cuando incorporamos una estimación y una lectura explícita de su incertidumbre.”

**Contenido visual y puntos clave**

Gran ecuación: 100.000 barriles × USD 5/barril = USD 500.000 de desvío presupuestario.
Dos puntos breves: Mayor exposición exige revisar supuestos; el costo depende del volumen y del precio efectivo.
Pie VISIBLE: Ejemplo hipotético de sensibilidad. No representa ahorro generado por los modelos.

## Bloque 2. Storytelling y solución

### 6. Dos modelos para preparar la decisión semanal

**Guion del presentador**

“Para trabajar sobre esa necesidad desarrollamos dos enfoques complementarios. Holt amortiguado resume el nivel y la tendencia reciente. ARIMA analiza la relación temporal entre los precios. Cada uno genera estimaciones para WTI y Brent. Los propongo como apoyo a una conversación comercial concreta: qué escenario usar para preparar la semana y qué tan sensible es la decisión.”

**Contenido visual y puntos clave**

Introducir los protagonistas: Holt amortiguado, lectura del nivel y la tendencia reciente; ARIMA, lectura de la dependencia entre cotizaciones. Ambos: estimaciones independientes para WTI y Brent, cinco cotizaciones objetivo de lunes a viernes, con incertidumbre. Indicar horizonte puede extenderse si último dato está atrasado.

### 7. Holt sigue la tendencia reciente con prudencia

**Guion del presentador**

“Uso Holt para actualizar la lectura del precio a partir de las cotizaciones recientes. Su tendencia amortiguada reduce gradualmente el peso de esa tendencia a medida que avanzamos. Así obtenemos una referencia interpretable para la semana. Su utilidad debe comprobarse contra una alternativa sencilla: mantener el último precio conocido.”

**Contenido visual y puntos clave**

Mostrar tres conceptos explicativos breves: actualización del nivel, tendencia reciente, amortiguación al avanzar el horizonte. Salida: precio estimado por fecha y bandas aproximadas. Sin métricas de precisión inventadas ni curvas ficticias.

### 8. ARIMA aporta una segunda lectura temporal

**Guion del presentador**

“ARIMA aporta otra manera de leer la misma historia. El ajuste evalúa cómo se relacionan las cotizaciones y sus cambios a lo largo del tiempo. En ocasiones selecciona una estructura cuyo pronóstico coincide con el último precio. Ese resultado también informa la decisión: la evidencia disponible puede justificar una referencia sencilla.”

**Contenido visual y puntos clave**

Mostrar: patrones de dependencia entre cotizaciones; selección dentro de cada entrenamiento; estimación e intervalos condicionales. Nota: algunos ajustes pueden coincidir con repetir el último precio.

### 9. El uso conjunto permite contrastar escenarios

**Guion del presentador**

“Mi propuesta es usar ambos enfoques sobre el mismo corte y el mismo horizonte. Si entregan lecturas próximas, podemos discutir ese escenario. Si difieren, revisamos el supuesto antes de comprometer el presupuesto. Todavía no evaluamos una combinación automática. La transformación que proponemos es una decisión documentada con estimaciones contrastables y resultados que luego podemos medir.”

**Contenido visual y puntos clave**

Rotular VISIBLE: Propuesta de uso comercial, sin combinación automática validada.
Mostrar en una única composición: misma fecha de corte, estimación Holt, estimación ARIMA, revisión de diferencias, decisión del responsable de compras. Tres salidas: precios por fecha; rangos de cada modelo; comparación con referencia.

### 10. ARIMA redujo 32,1% el error en una semana de Brent

**Guion del presentador**

“Esta es nuestra evidencia comercial más concreta. Reservamos la semana del 5 al 9 de octubre y entrenamos solo con información hasta el día 2. En Brent, ARIMA redujo el error absoluto promedio de 8,078 a 5,485 dólares por barril, una mejora de 32,1% frente al último precio. En WTI empató con la referencia. Presento este resultado como una señal para validar en más semanas, sin extrapolarlo como una ventaja permanente.”

**Contenido visual y puntos clave**

Tabla MAE, USD/barril, semana reservada 05–09/10/2026, corte entrenamiento 02/10/2026:
WTI: último precio 1,498; Holt 1,54; ARIMA 1,498.
Brent: último precio 8,078; Holt 8,03; ARIMA 5,485.
Destacar para Brent: reducción absoluta 2,593 USD/barril frente a último precio. Reducción relativa 32,1%.
Pie VISIBLE: Una semana histórica, cinco cotizaciones por crudo. Resultado de ARIMA, no de la combinación. No garantiza desempeño futuro.

### 11. La incertidumbre también entra en el presupuesto

**Guion del presentador**

“Un precio central por sí solo deja fuera una parte de la decisión. Por eso también mostramos la incertidumbre. En este ejemplo histórico, el intervalo de ARIMA se amplía al avanzar en la semana. Las bandas dependen de los supuestos del modelo y no anticipan un shock nuevo. Antes de utilizar una salida también verificamos la fecha del último dato disponible.”

**Contenido visual y puntos clave**

Mostrar ejemplo HISTÓRICO ARIMA Brent, corte 02/10/2026:
Fecha 05/10/2026, pronóstico 134,61, intervalo condicional 95% 125,06 a 144,15.
Fecha 09/10/2026, pronóstico 131,28, intervalo condicional 95% 111,29 a 151,27.
Banda o tabla nativa editable con esas dos fechas, sin rellenar trayectorias inexistentes.
Texto breve: El rango se amplía con el horizonte. La frescura del dato debe verificarse.
Pie: Intervalos condicionados al modelo, sin cobertura empírica garantizada. Holt utiliza bandas aproximadas por simulación. Fuente del proyecto hasta 14/10/2026.

### 12. El ROI se mide sobre compras reales

**Guion del presentador**

“Voy a medir el valor con el resultado de la compra y con los costos completos. Como hipótesis de sensibilidad, una mejora efectiva de cincuenta centavos por barril sobre cien mil barriles representaría cincuenta mil dólares de beneficio bruto. El piloto debe demostrar si esa mejora existe y qué parte puede atribuirse al uso del producto. Recién entonces calculamos el ROI.”

**Contenido visual y puntos clave**

Fórmula: ROI = (beneficio incremental atribuible − costo total) / costo total.
Ejemplo VISIBLE como hipótesis, NO resultado: 100.000 barriles × USD 0,50/barril de mejora efectiva = USD 50.000 de beneficio bruto potencial.
Costo total: piloto, operación e integración, a definir. Texto: precisión predictiva y ahorro efectivo son métricas distintas.

### 13. Un piloto de ocho semanas permite medir el aporte

**Guion del presentador**

“Propongo un piloto inicial de ocho semanas con una decisión de compra definida. Ya contamos con los modelos desarrollados en notebooks. Acordaremos el formato del informe, usaremos datos actualizados y congelaremos cada pronóstico antes de conocer el resultado. Mediremos precisión, efecto económico y esfuerzo operativo frente al proceso actual. Si la evidencia resulta insuficiente, extendemos la evaluación antes de escalar.”

**Contenido visual y puntos clave**

Rotular VISIBLE: Propuesta de implementación.
Mostrar secuencia simple sin prometer funcionalidad existente: acordar una decisión y volumen; emitir informes con ambos modelos en cortes y horizontes idénticos; registrar decisiones antes del resultado; medir frente a política actual y último precio.
Criterios: MAE y RMSE comparables; beneficio neto atribuible; tiempo operativo.
Nota: modelos desarrollados en notebooks. Formato de entrega e integración a acordar. Ocho semanas es propuesta inicial y se extiende si evidencia insuficiente.

### 14. La próxima compra puede tener evidencia medible

**Guion del presentador**

“El cambio entre períodos ya nos muestra por qué conviene revisar los supuestos de compra. Tenemos dos modelos y una evidencia inicial que merece una prueba comercial. Propongo que elijamos una operación concreta y acordemos el criterio de éxito. Al cierre del piloto, podrán decidir la continuidad con resultados comparables y un valor económico medido en su propia operación.”

**Contenido visual y puntos clave**

Cierre mínimo: Una operación definida; un volumen conocido; un criterio de éxito acordado.
CTA destacado: Acordar el alcance del piloto
Subtexto: Decidir la continuidad con resultados comparables

## Fuentes y alcance de las métricas

- `data/eia_precios_crudo_diarios_2024-01_a_2026-10.csv`: comparación de períodos, precios medios, volatilidad de retornos y spread.
- `notebooks/serie_tiempo.ipynb`: Holt amortiguado, validación histórica y bandas aproximadas.
- `notebooks/arima_periodo_2_wti_brent.ipynb`: ARIMA y prueba semanal del 05–09/10/2026, con corte de entrenamiento 02/10/2026.

El 32,1 % corresponde a la reducción del MAE de ARIMA frente al último precio en Brent en esa única semana: (8,078 − 5,485) / 8,078. No mide ahorro ni desempeño conjunto. Las validaciones generales guardadas de Holt y ARIMA tienen horizontes distintos y no deben usarse para un ranking directo. La reconstrucción aleatoria de precios ocultos no demuestra precisión de pronóstico futuro. Las salidas futuras guardadas tampoco comparten semana objetivo y no se presentan como cotizaciones actuales.

