# Análisis de Costos y Comparativa de Despliegue: Local vs. API Mistral vs. Nube GPU (AWS)

## 1. Introducción y Detalles de Costos de Tokens

El despliegue de Modelos de Lenguaje de Gran Escala (LLMs), como la familia **Ministral 3** (3B y 8B) desarrollada por Mistral AI, plantea diversas alternativas de arquitectura de infraestructura. Cada arquitectura presenta estructuras de costo radicalmente distintas:

1. **API de Mistral (La Plateforme):** Pago por consumo (*Pay-as-you-go*) basado en volumen de tokens procesados (entrada y salida) o ejecución por lotes (*batch*).
2. **Instancia GPU en la Nube (AWS EC2 - g5.xlarge):** Pago por infraestructura alquilada bajo demanda por hora ($1.006/hora), independientemente del nivel de tráfico.
3. **Despliegue Local (Ollama / Docker):** Costo marginal derivado únicamente del consumo de energía eléctrica del hardware personal ya adquirido.

---

## 2. Precios Oficiales y Fuentes de Consulta

A continuación se resumen las tarifas oficiales tomadas como referencia para los cálculos de costos de inferencia y hosting:

### A. Tarifas API Oficial de Mistral AI (La Plateforme)
* **Ministral 3 8B:** 
  * Tokens de Entrada: **$0.15** por millón de tokens ($0.15 / 1M tokens).
  * Tokens de Salida: **$0.15** por millón de tokens ($0.15 / 1M tokens).
  * Ventana de contexto: 256K.
* **Ministral 3 3B:** 
  * Tokens de Entrada y Salida: **$0.10** por millón de tokens ($0.10 / 1M tokens).
* **Tarifa Batch (Procesamiento por Lotes):** 
  * **$0.075** por millón de tokens (50% de descuento sobre la tarifa estándar).

### B. Instancia GPU en la Nube (AWS EC2 g5.xlarge)
* **Especificaciones:** 1 GPU NVIDIA A10G (22 GiB VRAM), 4 vCPU, 16 GiB RAM.
* **Costo Bajo Demanda (us-east-1):** **$1.006** por hora.
* **Costo Mensual Estimado (24/7 = 730 horas):** $1.006 \times 730 \approx \mathbf{\$734.38/mes}$.

---

## 3. Cálculo del Caso Concreto

### Caso de Estudio
* **Volumen diario:** 1 000 consultas por día.
* **Tamaño promedio por consulta:** 500 tokens (combinación de entrada y salida).
* **Periodo:** 30 días.
* **Total de tokens mensuales:** $1\,000 \times 500 \times 30 = \mathbf{15\,000\,000 \text{ tokens/mes (15 M)}}$.

---

### Cálculos Detallados por Opción

#### Opción A: API de Mistral AI (Ministral 3 8B - Tiempo Real)
$$\text{Costo Mensual} = 15 \text{ M tokens} \times \frac{\$0.15}{1 \text{ M tokens}} = \mathbf{\$2.25 \text{ / mes}}$$

#### Opción B: API de Mistral AI (Ministral 3 8B - Tarifa Batch)
$$\text{Costo Mensual} = 15 \text{ M tokens} \times \frac{\$0.075}{1 \text{ M tokens}} = \mathbf{\$1.13 \text{ / mes}}$$

#### Opción C: AWS EC2 g5.xlarge (Servidor Encendido 24/7)
$$\text{Costo Mensual} = 730 \text{ horas} \times \$1.006 \text{ / hora} = \mathbf{\$734.38 \text{ / mes}}$$

#### Opción D: AWS EC2 g5.xlarge (Encendido Bajo Demanda según Horas de Inferencia)
Tomando como referencia el rendimiento obtenido en la evaluación del repositorio (Fase 4, con promedios conservadores de $30 \text{ tokens/s}$):
* **Segundos por consulta:** $\frac{500 \text{ tokens}}{30 \text{ tokens/s}} \approx 16.67 \text{ segundos/consulta}$.
* **Horas mensuales de cómputo activo:**
  $$\frac{1\,000 \text{ consultas/día} \times 16.67 \text{ s/consulta} \times 30 \text{ días}}{3\,600 \text{ s/hora}} \approx 138.9 \text{ horas/mes}$$
* **Costo mensual aproximado:**
  $$138.9 \text{ horas} \times \$1.006 \text{ / hora} \approx \mathbf{\$139.73 \text{ / mes}}$$

*(Nota: Mantener la GPU encendida solo durante la inferencia requeriría una arquitectura *serverless* o de auto-escalado con retraso de arranque / "cold start", poco viable para aplicaciones con requerimiento de respuesta inmediata).*

#### Opción E: Despliegue Local (Ollama en Laptop/PC Personal)
$$\text{Costo} = \text{Potencia (kW)} \times \text{Horas de uso} \times \text{Tarifa eléctrica (\$/kWh)}$$
* **Consumo de laptop personal bajo carga de inferencia:** $\approx 45 \text{ W} = 0.045 \text{ kW}$.
* **Tiempo estimado de procesamiento activo (a 30 tokens/s):** $\approx 138.9 \text{ horas/mes}$.
* **Tarifa promedio de electricidad en Costa Rica (ICE/CNFL residencial):** $\approx \$0.15 \text{ / kWh}$.
* **Costo eléctrico mensual aproximado:**
  $$0.045 \text{ kW} \times 138.9 \text{ h} \times \$0.15 \text{ / kWh} \approx \mathbf{\$0.94 \text{ / mes}}$$

*(Aclaración: No incluye el costo de adquisición del equipo ni su desgaste por cómputo intenso).*

---

### Resumen Financiero del Caso Concreto

| Opción de Despliegue | Cálculo / Fórmula | Costo Mensual Estimado |
| :--- | :--- | :--- |
| **API Mistral (Ministral 3 8B)** | $15 \text{ M tokens} \times \$0.15 / \text{M}$ | **~$2.25 USD** |
| **API Mistral (Batch)** | $15 \text{ M tokens} \times \$0.075 / \text{M}$ | **~$1.13 USD** |
| **AWS g5.xlarge (24/7)** | $730 \text{ h} \times \$1.006 / \text{h}$ | **~$734.38 USD** |
| **AWS g5.xlarge (Solo uso activo)** | $138.9 \text{ h} \times \$1.006 / \text{h}$ | **~$139.73 USD** |
| **Local (Ollama)** | $0.045 \text{ kW} \times 138.9 \text{ h} \times \$0.15 / \text{kWh}$ | **~$0.94 USD** (Excluye hardware) |

---

## 4. Tabla Comparativa de Criterios Técnicos y Operativos

A partir de las métricas obtenidas durante la Fase 4 del proyecto (archivos `analyze.py`, `docker_3runs.json`, `nativo_3runs.json`, `grafico_ttft.png` y `grafico_tps.png`), se consolida la siguiente tabla comparativa:

| Criterio | Local (Ollama / Docker) | API Mistral (La Plateforme) | GPU en AWS (EC2 g5.xlarge) |
| :--- | :--- | :--- | :--- |
| **Latencia (TTFT y TPS)** | TTFT y TPS limitados por hardware local (medidos mediante `src/analyze.py`). Sin latencia de red. | Baja latencia de procesamiento; suma la latencia de red desde Costa Rica a los servidores de Mistral AI. | Altísima velocidad de generación por la GPU A10G; suma latencia de red hacia AWS `us-east-1`. |
| **Escalabilidad** | Baja. Una petición concurrente a la vez; saturación según límites del equipo personal. | Muy Alta. Manejada íntegramente por el proveedor según límites de cuotas de API. | Alta. Regulada mediante políticas de auto-escalado e instancias adicionales configuradas por el usuario. |
| **Mantenimiento** | Totalmente manual: actualizaciones del entorno, controladores, Ollama/Docker y mitigación de fallos. | Ninguno. El mantenimiento, alta disponibilidad e infraestructura corren por cuenta de Mistral AI. | Alto. Gestión completa del SO (Linux), drivers NVIDIA, parches de seguridad, monitoreo y contenedor. |
| **Costo (Caso 15M Tokens)** | Consumo eléctrico marginal (~$0.94 USD/mes). Hardware previamente adquirido. | **~$2.25 USD/mes** (Extremadamente económico para volúmenes bajos/medios). | **~$734.38 USD/mes** (24/7) o ~$139.73 USD/mes (bajo uso activo). |
| **Privacidad de Datos** | **Absoluta.** Los datos no salen de la máquina local ni se comparten con terceros. | Media/Baja. Los prompts se envían a servidores de un tercero; requiere verificar las políticas de privacidad. | Alta/Controlada. Los datos permanecen dentro de la VPC propia en la infraestructura del proveedor cloud. |
| **Dependencia de Internet**| **Ninguna.** Una vez descargado el peso `.gguf`, funciona 100% offline. | **Obligatoria.** Requiere conexión continua y estable a Internet. | **Obligatoria.** Requiere conexión continua y estable a Internet. |
| **Facilidad de Uso** | Media. Requiere instalación de Ollama/Docker y ejecución de scripts propios (`inference.py`). | **Alta.** Basta con generar una clave API (`API_KEY`) y consumir los endpoints. | Baja. Exige aprovisionar VPCs, grupos de seguridad, llaves SSH y entornos CUDA/Docker. |

---

## 5. Ventajas y Desventajas por Arquitectura

### 1. Inferencia Local (Ollama / Docker)
* **Ventajas:**
  * **Privacidad Total:** Ideal para datos confidenciales, legales o médicos.
  * **Costo Operativo Nulo:** Sin costo recurrente de licencias o infraestructura.
  * **Autonomía:** Funciona sin acceso a Internet.
* **Desventajas:**
  * **Rendimiento Limitado:** Depende del hardware disponible (CPU/RAM/VRAM).
  * **Nula Escalabilidad Concurrente:** Un solo usuario o petición puede saturar los recursos.

### 2. API de Mistral AI (La Plateforme)
* **Ventajas:**
  * **Costo Eficiente a Bajo Volumen:** Pagos mínimos por consumo real (apenas $2.25 por 15M de tokens).
  * **Cero Mantenimiento:** Inicia inmediatamente sin administración de servidores.
  * **Escalabilidad Elástica:** Soporta múltiples solicitudes concurrentes sin degradar la experiencia.
* **Desventajas:**
  * **Riesgo de Privacidad:** Envío de información sensible a servidores externos.
  * **Dependencia Externa:** Vulnerable a interrupciones en la conexión a Internet o caídas de la API.

### 3. GPU dedicada en la Nube (AWS EC2 g5.xlarge)
* **Ventajas:**
  * **Control Total:** Posibilidad de ajustar el entorno, usar modelos personalizados o fine-tuning propio.
  * **Alto Rendimiento:** Procesamiento veloz sostenido mediante GPU dedicada A10G.
  * **Aislamiento de Red:** Control de seguridad mediante VPN/VPC privada.
* **Desventajas:**
  * **Costo Elevado e Ineficiente a Bajo Volumen:** Gastos fijos muy altos ($734/mes) independientemente de la demanda.
  * **Carga de Mantenimiento:** Exige soporte técnico para mantenimiento de sistema y drivers.

---

## 6. Recomendación Final y Conclusiones

### Recomendación por Escenario
1. **Opción Local (Ollama/Docker):** Recomendada para **entornos de desarrollo, pruebas conceptuales, aprendizaje**, o cuando la **privacidad y confidencialidad estricta de los datos** impidan el envío de información a servidores de terceros, así como en aplicaciones que requieran funcionar offline.
2. **API de Mistral AI:** Es la **opción recomendada para el caso de estudio propuesto (1 000 consultas diarias de 500 tokens)**. Con un gasto mensual estimado de **$2.25 USD**, ofrece la mejor relación costo-beneficio, eliminando la sobrecarga operativa de administración de servidores y garantizando escalabilidad inmediata.
3. **GPU dedicada en AWS:** Recomendada únicamente para **escenarios empresariales de muy alto volumen** (millones de consultas diarias), o cuando se requieran arquitecturas personalizadas con fine-tuning estricto sobre infraestructura propia donde el costo fijo de $734 USD/mes quede totalmente amortizado por el nivel de tráfico.

### Conclusión
Para el volumen del caso (15 millones de tokens al mes), **la API oficial de Mistral representa la solución más económica, eficiente y simple**. Mantener una GPU en la nube resulta económicamente inviable para este flujo de trabajo ($734 vs $2.25). Por su parte, la opción **Local** destaca como la mejor alternativa para preservar el control absoluto sobre la privacidad de los datos sin asumir costos recurrentes.

---

## 7. Referencias (APA 7)

* BenchLM. (2026). *Mistral API Pricing Comparison*. BenchLM AI. https://benchlm.ai/mistral/api-pricing
* Developer's Digest. (2026). *Ministral 3 8B: Benchmarks and API Costs*. https://www.developersdigest.tech/models/ministral-3-8b
* Holori. (2026). *AWS EC2 g5.xlarge On-Demand Pricing - us-east-1*. Holori Calculator. https://calculator.holori.com/aws/ec2/g5.xlarge?region=us-east-1
* Mistral AI. (2026, 27 de octubre). *Models and Platform Pricing*. Docs Mistral AI. https://docs.mistral.ai/platform/pricing