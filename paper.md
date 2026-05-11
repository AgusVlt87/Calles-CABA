---
title: "Nomenclatura urbana y geografía electoral: los nombres de calle como marcadores de territorio político en la Ciudad Autónoma de Buenos Aires (2011–2025)"
author: "Agustín Viullet"
date: "Mayo de 2026"
lang: es
abstract: |
  Este artículo examina la relación entre la presencia de calles con nombres de figuras políticas partidarias y el comportamiento electoral de los 167 circuitos de la Ciudad Autónoma de Buenos Aires entre 2011 y 2025. A partir de un callejero de 31.961 segmentos viales, se identificaron 6.863 tramos asociados a 217 figuras políticas mediante dos métodos complementarios: consulta directa de la propiedad *named after* (P138) de Wikidata y *matching* textual supervisado. Los datos electorales comprenden diez elecciones —presidenciales, legislativas nacionales y de jefe de gobierno—. La hipótesis de que la densidad continua de calles partidarias predice el voto no es sostenida por los datos: ni el porcentaje de metros lineales (*ρ* de Spearman entre −0,32 y 0,14, todos ns) ni la densidad por kilómetro cuadrado muestran relación estadísticamente significativa con el porcentaje de votos, una vez controlados el nivel socioeconómico y la educación por radio censal. Sin embargo, la presencia *binaria* de calles peronistas discrimina de manera robusta: los 23 circuitos con al menos un segmento asignado al PJ obtienen en promedio 5,7 puntos porcentuales más de voto peronista que los 144 circuitos sin calles de esa adscripción (Mann-Whitney, *p* = 0,003; *d* de Cohen = 0,83), efecto que se reproduce sin excepción en las diez elecciones del período. El análisis de autocorrelación espacial (I de Moran) confirma que la distribución de nombres políticos es geográficamente concentrada y no aleatoria. Se argumenta que los topónimos políticos operan como *marcadores de territorio histórico* antes que como agentes de influencia sobre el votante individual: reflejan el dominio que un partido ejerció sobre un área de la ciudad en el pasado y cuyo sedimento electoral persiste en el presente.
keywords: []
---

\newpage

---

## 1. Introducción

Las ciudades inscriben su historia política en el espacio público. Los nombres de las calles —a diferencia de los monumentos, los murales o los discursos— están presentes en cada dirección postal, en cada conversación cotidiana, en cada mapa impreso o digital. Constituyen, en ese sentido, lo que Azaryahu (1996) denominó "monumentos cotidianos": artefactos simbólicos de muy bajo costo de mantenimiento y muy alta exposición repetida.

La pregunta que orienta este trabajo es si esa exposición tiene consecuencias electorales medibles. Específicamente: ¿los circuitos electorales de la Ciudad Autónoma de Buenos Aires (CABA) en los que predominan nombres de calles asociados a un partido político muestran mayor adhesión electoral a ese partido? La hipótesis es teóricamente plausible desde al menos dos perspectivas. Desde la psicología política, la exposición repetida a estímulos simbólicos puede reforzar identidades preexistentes y aumentar la disponibilidad cognitiva de un referente político (*mere exposure effect*, Zajonc, 1968). Desde la geografía electoral, la literatura ha documentado cómo el espacio construido actúa como repositorio de identidades colectivas que se transmiten intergeneracionalmente (Johnston *et al.*, 2000; Agnew, 2002).

CABA ofrece condiciones favorables para una prueba empírica de esta hipótesis. Cuenta con un callejero oficial georeferenciado, 167 circuitos electorales con resultados desagregados para una serie histórica de diez elecciones (2011-2025), y un acervo de nombres políticos que abarca desde los unitarios del siglo XIX hasta el peronismo contemporáneo. Adicionalmente, la disponibilidad de la base de datos Wikidata —que codifica explícitamente la propiedad *named after* (P138) para miles de entidades callejeras— permite resolver el problema de identificación con un grado de certeza superior al *text matching* convencional.

Los resultados obligan a matizar la hipótesis original. La versión continua —más metros de calles del partido implica más votos— no es sostenida para ningún partido ni indicador de densidad. La versión binaria —la mera presencia de calles del partido— sí discrimina de manera estadísticamente significativa y temporalmente estable para el caso del Partido Justicialista (PJ). Esta asimetría entre densidad y presencia constituye el hallazgo central del artículo y sugiere que los nombres de calle no *causan* el voto, sino que son un *proxy* de la identidad territorial histórica de un partido en determinada zona de la ciudad.

El artículo se organiza como sigue. La sección 2 revisa los antecedentes teóricos relevantes. La sección 3 describe los datos y la estrategia metodológica. La sección 4 presenta los resultados en cuatro subsecciones. La sección 5 discute las implicaciones sustantivas y las limitaciones del trabajo. La sección 6 concluye.

---

## 2. Marco teórico y antecedentes

### 2.1 Toponimia política y construcción simbólica del espacio

La literatura sobre topónimos políticos ha documentado extensamente el uso de la nomenclatura urbana como herramienta de legitimación y disputa simbólica. Azaryahu (1996, 2011) mostró que los cambios de nombre de calles en Berlín antes y después de la Segunda Guerra Mundial, y en Israel tras la independencia, siguieron lógicas de borramiento de memorias adversarias y consolidación de narrativas nacionales. Light (2004) realizó un análisis análogo para Bucarest entre 1990 y 1997, mostrando cómo la transición poscomunista se expresó en oleadas de renombramiento orientadas a reemplazar el panteón socialista con figuras de la historia nacional rumana. Rose-Redwood *et al.* (2010) sintetizaron este campo en la noción de *geografías de inscripción toponímica*, que entiende el proceso de nombrar lugares como un ejercicio de poder que construye y naturaliza determinadas versiones del pasado y el presente.

En América Latina, la bibliografía sobre este fenómeno es más escasa pero creciente. Para Argentina, Jelin (2002) y Lorenz (2006) han abordado los nombres como parte de las políticas de memoria en contextos postdictatoriales. Para Buenos Aires en particular, se conoce el proceso de renombramiento durante el primer peronismo (1946-1955), cuando decenas de calles, avenidas y plazas recibieron nombres de figuras del movimiento —incluida la renominación de la entonces Avenida Alvear como Avenida del Libertador en 1952— pero no existe, hasta donde se conoce, un estudio cuantitativo que vincule esa distribución con comportamientos electorales contemporáneos.

### 2.2 Geografía electoral y persistencia territorial

La geografía electoral de Buenos Aires ha sido caracterizada por una fractura norte-sur consolidada. Las comunas del norte (Palermo, Recoleta, Belgrano, Núñez) han votado consistentemente por partidos de centroderecha —la UCR y luego el PRO— mientras que las comunas del sur (La Boca, Barracas, Villa Lugano, Mataderos, Villa del Parque) han mostrado mayor adhesión peronista (Calvo y Escolar, 2005; Maronese *et al.*, 2007). Esta estructura ha demostrado notable estabilidad a lo largo de décadas y es robusta a los cambios en la oferta partidaria.

La explicación canónica de esta persistencia apela a la segregación socioespacial: las comunas del sur concentran mayor proporción de trabajadores manuales, hogares con NBI más elevado y menores niveles educativos, variables que en Argentina están históricamente asociadas al voto peronista (Lupu y Stokes, 2009; Vommaro y Morresi, 2014). Sin embargo, la persistencia territorial del voto supera lo que se explicaría exclusivamente por las características socioeconómicas contemporáneas, lo que sugiere la existencia de identidades político-territoriales con cierta autonomía respecto a las condiciones materiales actuales.

En este marco, los nombres de calle podrían operar como uno de los mecanismos de reproducción de esa identidad: no como causa primera, sino como componente del entorno simbólico que cotidianamente recuerda a los residentes de ciertos barrios a qué tradición política pertenecen.

### 2.3 Hipótesis

Del marco teórico precedente se derivan tres hipótesis que este trabajo somete a prueba empírica:

**H1 (densidad continua):** A mayor porcentaje de metros lineales de calles con nombres de figuras de un partido en un circuito, mayor porcentaje de votos obtendrá ese partido en ese circuito.

**H2 (presencia binaria):** Los circuitos que poseen al menos una calle con nombre de figuras de un partido obtienen mayor porcentaje de votos para ese partido que los circuitos que no poseen ninguna.

**H3 (persistencia temporal):** Los efectos detectados, de existir, son estables a lo largo de la serie electoral (2011-2025) y no responden a coyunturas específicas.

---

## 3. Datos y metodología

### 3.1 Callejero y proceso de identificación

El callejero oficial de la CABA, provisto por el Gobierno de la Ciudad, contiene 31.961 segmentos viales georeferenciados con geometría en formato WKT (EPSG:4326). Para identificar calles con nombres de figuras políticas se empleó un procedimiento en dos etapas.

**Etapa 1 — Wikidata P138 (fuente primaria).** Se consultó la API SPARQL de Wikidata buscando entidades geográficas ubicadas en CABA (P131 = Q1486, con cobertura transitiva a barrios y comunas) que posean la propiedad *named after* (P138) apuntando a una persona (P31 = Q5). Esta consulta devolvió 603 resultados, correspondientes a 582 entidades callejeras únicas. Mediante normalización de nombres (eliminación de abreviaturas de tipo de vía, conversión a mayúsculas sin tildes, inversión del formato "Apellido, Nombre") se estableció correspondencia con 5.406 segmentos del callejero oficial.

La ventaja principal de este método es que elimina la ambigüedad inherente al *matching* textual: la base de datos certifica explícitamente la identidad de la persona que da nombre a cada calle, con independencia de si el nombre de la calle es el apellido solo, el nombre completo o una abreviatura.

**Etapa 2 — *Matching* textual supervisado (fuente complementaria).** Para los segmentos no cubiertos por P138, se construyó un catálogo de figuras políticas argentinas descargado también desde Wikidata (presidentes, legisladores, gobernadores, políticos del siglo XX/XXI con partido registrado). Se aplicó búsqueda de *substring* exacto sobre el nombre normalizado del callejero contra las variantes de nombre de cada figura. Solo se aceptaron *matches* con nombre completo de al menos dos *tokens*, sin *fuzzy matching*. Este proceso identificó 1.457 segmentos adicionales.

En total, 6.863 segmentos —el 21,5% del callejero— fueron asignados a alguna figura política. De ellos, el 78,8% procede de la fuente Wikidata P138 (mayor confianza) y el 21,2% del *matching* textual.

### 3.2 Clasificación partidaria

Las figuras identificadas se clasificaron en seis categorías:

| Partido | Descripción | Segmentos | Circuitos |
|:---|:---|---:|---:|
| UCR | Unión Cívica Radical y partidos afiliados | 942 | 92 |
| Liberalismo | Partidos liberal-conservadores históricos y modernos¹ | 1.173 | 95 |
| PJ | Peronismo en todas sus expresiones (1946–presente) | 209 | 23 |
| PS | Partido Socialista (todas sus fracciones) | 236 | 29 |
| PRO | Propuesta Republicana y coaliciones | 1 | 1 |
| Prócer | Figuras previas a la organización partidaria (nacidos antes de 1850) | 1.087 | — |

> ¹ La categoría "Liberalismo" incluye el Partido Unitario (siglo XIX), el Partido Autonomista Nacional, el Partido Demócrata y sus descendientes, y los partidos liberal-libertarios contemporáneos. La inclusión del Partido Unitario en esta categoría responde a su posición histórica como facción centralista-liberal, cuya línea ideológica es la antecesora intelectual del liberalismo porteño moderno. Los próceres se excluyen del análisis correlacional por tratarse de figuras anteriores al sistema de partidos.

Para el análisis correlacional, UCR y PRO se agrupan en "Centroderecha" dado que desde 2015 la UCR no presenta candidatos presidenciales propios en CABA.

### 3.3 Datos electorales y controles

Los resultados electorales provienen de la Dirección Nacional Electoral (DINE) y el GCBA, y cubren diez elecciones entre 2011 y 2025:

- **Presidenciales:** 2011, 2015, 2019, 2023
- **Legislativas (diputados nacionales):** 2013, 2017, 2021, 2025
- **Jefe de Gobierno de CABA:** 2019, 2023

Los controles socioeconómicos se obtuvieron del Censo Nacional de Población 2022 (INDEC) a nivel de radio censal (3.555 radios en CABA). Mediante *spatial join* por centroide, cada radio se asignó al circuito electoral correspondiente; los controles se agregaron a nivel circuito como promedio ponderado por población. Las variables utilizadas son la tasa de hogares con Necesidades Básicas Insatisfechas (*tasa_NBI*) y un índice educativo ponderado (*índice_edu*) construido a partir de la distribución del máximo nivel de instrucción alcanzado (escala 0-10).

### 3.4 Vinculación espacial calles–circuitos

La asignación de cada segmento vial a un circuito electoral se realizó mediante *spatial join* por centroide, reproyectando las geometrías al sistema POSGAR 2007 Faja 3 (EPSG:22185) para el cálculo correcto del centroide. Este método evita los duplicados que generaría una unión por intersección cuando un segmento cruza la frontera entre dos circuitos.

### 3.5 Variables y modelos estadísticos

**Variables independientes (calles):**

- *pct_metros*: porcentaje de metros lineales atribuidos al partido sobre el total de metros políticos del circuito (excluidos próceres y figuras sin partido conocido).
- *metros_por_km²*: densidad absoluta de metros del partido por kilómetro cuadrado del circuito.
- *presencia_binaria*: indicador dicotómico (0/1) de si el circuito contiene al menos un segmento del partido.

**Variable dependiente (votos):**

- *pct_votos*: porcentaje de votos positivos obtenido por el partido en cada elección. Para los análisis de promedio se utiliza la media aritmética sobre todas las elecciones disponibles para ese tipo.

Los análisis empleados son: (1) correlación de Spearman bivariada; (2) correlación parcial de Spearman controlando por *tasa_NBI* e *índice_edu* (biblioteca *pingouin*); (3) prueba de Mann-Whitney de dos colas para comparación de grupos; (4) *I* de Moran global (con 999 permutaciones) y LISA (*Local Moran's I*) para la detección de autocorrelación espacial (bibliotecas *libpysal* y *esda*).

Todos los análisis se realizaron en Python 3.12. El umbral de significancia es α = 0,05 (bilateral).

---

## 4. Resultados

### 4.1 Geografía descriptiva de la nomenclatura política

La Figura 1 presenta el partido con mayor presencia en metros lineales por circuito electoral.² El patrón territorial es pronunciado: el Liberalismo histórico domina la nomenclatura en las comunas centrales y norteñas (1, 4, 5, 7, 8, 9, 14), la UCR aparece distribuida con relativa uniformidad en toda la ciudad, el PS se concentra en el centro-norte, y el PJ queda circunscrito casi exclusivamente al sur (comunas 4, 7, 8 y 9).

> ² Los circuitos con solo calles de próceres, sin partido, o sin ninguna calle política, aparecen en gris.

En términos de figuras individuales, las cinco con mayor presencia en kilómetros lineales son Bernardino Rivadavia (170 segmentos), Juan B. Justo (144), José de San Martín (124), Juan Bautista Alberdi (113) y Eva Perón (100). La distribución es marcadamente asimétrica: unas pocas figuras concentran una proporción desproporcionada del metraje total (*véase* Figura 5).

Dentro de la categoría Liberalismo, el desglose por era revela dos geografías distintas. Las figuras del siglo XIX (Partido Unitario, PAN, Partido Liberal; *n* = 956 segmentos) se distribuyen en las comunas del centro-norte, con mayor concentración en las comunas 4, 7, 9 y 14. Las figuras del siglo XX y XXI (Partido Federal, UCR disidente, partidos liberal-conservadores modernos; *n* = 146 segmentos) se concentran en cambio en las comunas 14 y 15 (Villa del Parque, Paternal, Villa Crespo).

### 4.2 Autocorrelación espacial

La distribución de nombres políticos en CABA no es geográficamente aleatoria. La Tabla 1 reporta el estadístico *I* de Moran global para el indicador *pct_metros* de cada partido.

**Tabla 1.** *I* de Moran global para la distribución de calles políticas por circuito electoral (999 permutaciones).

| Partido electoral | *N* circuitos | *I* de Moran | E[*I*] | *p*-valor | Interpretación |
|:---|---:|---:|---:|---:|:---|
| Centroderecha | 93 | 0,239 | −0,011 | 0,004 | Clustering positivo |
| Liberalismo | 95 | 0,160 | −0,011 | 0,013 | Clustering positivo |
| PJ | 23 | 0,324 | −0,046 | 0,025 | Clustering positivo |
| PS | 29 | 0,036 | −0,036 | 0,342 | No significativo |

Los valores positivos y significativos para Centroderecha, Liberalismo y PJ indican que los circuitos con mayor concentración de calles de cada partido tienden a estar rodeados de otros circuitos con concentración igualmente elevada. Este patrón refleja decisiones histórico-políticas de nomenclatura concentradas geográficamente, no el producto de una asignación aleatoria de nombres.

El análisis LISA (*Local Moran's I*) para Centroderecha identifica 9 circuitos *High-High* (conglomerados calientes en la zona norte) y 7 circuitos *Low-Low* (conglomerados fríos en el sur). Para el PJ, el análisis evidencia 2 circuitos *Low-Low* y 2 *High-Low*, consistentes con la concentración de nombres peronistas en un área geográfica compacta del sur (*véase* Figura 4).

### 4.3 Densidad continua y voto: ausencia de correlación

La hipótesis H1 no es sostenida por los datos. La Tabla 2 reporta los coeficientes de correlación de Spearman entre *pct_metros* y el porcentaje de votos promedio (columna bivariada) y parcial, controlando *tasa_NBI* e *índice_edu* (columna parcial).

**Tabla 2.** Correlación de Spearman entre *pct_metros* y porcentaje de votos, por tipo de elección y partido.

| Partido | *N* | ρ bivariado | *p* | ρ parcial | *p* |
|:---|---:|---:|:---|---:|:---|
| Centroderecha | 93 | 0,143 | 0,171 | 0,059 | 0,580 |
| Liberalismo | 95 | −0,135 | 0,193 | −0,155 | 0,139 |
| PJ | 23 | −0,275 | 0,205 | −0,014 | 0,952 |
| PS | 29 | −0,317 | 0,094 | −0,070 | 0,728 |

Ningún coeficiente alcanza el umbral de significancia estadística. El indicador alternativo *metros_por_km²* presenta un comportamiento similar, con una única excepción: para el PS, la correlación es significativa pero en dirección negativa (*ρ* = −0,39, *p* = 0,036), indicando que mayor densidad de calles socialistas se asocia con *menor* voto socialista. Este resultado, discutido en la sección 5.3, es consistente con la interpretación histórica de la distribución del PS en la ciudad.

La Figura 6 sintetiza visualmente los resultados de las tres especificaciones (pct_metros, metros_por_km², presencia binaria) para los cuatro partidos, evidenciando que la señal estadística solo emerge en la especificación binaria.

### 4.4 Presencia binaria y voto: el hallazgo central

La hipótesis H2 se confirma para el PJ con notable solidez. La Tabla 3 compara el voto promedio al PJ entre circuitos con y sin calles peronistas.

**Tabla 3.** Comparación del voto al PJ (promedio 2011-2025) entre circuitos con y sin presencia de calles peronistas (universo: 167 circuitos electorales de CABA).

| Grupo | *N* | Media | DE |
|:---|---:|---:|---:|
| Con calles PJ | 23 | 38,0% | 6,8 pp |
| Sin calles PJ | 144 | 32,2% | 6,8 pp |
| **Diferencia** | | **+5,7 pp** | |

Prueba de Mann-Whitney: *U* = 977, *p* = 0,003; *d* de Cohen = 0,83 (IC 95%: +2,1; +9,3 pp).³

> ³ El intervalo de confianza se obtuvo mediante bootstrap con 10.000 remuestras.

Para PS y Liberalismo se detectan diferencias menores pero estadísticamente significativas (*p* = 0,017 y *p* = 0,041, respectivamente). Para UCR/Centroderecha, el efecto no alcanza significancia (*p* = 0,309). Las razones de estas asimetrías se examinan en la sección 5.

La Figura 2 combina un mapa coroplético del voto peronista promedio con la delimitación de los 23 circuitos que poseen calles PJ y un gráfico de violín que exhibe la distribución completa de votos en ambos grupos.

### 4.5 Consistencia temporal (H3)

La diferencia detectada en la sección 4.4 no es atribuible a ninguna coyuntura electoral particular. La Tabla 4 reporta el resultado de la prueba de Mann-Whitney para cada uno de los diez eventos electorales disponibles.

**Tabla 4.** Diferencia en el porcentaje de votos al PJ entre circuitos con y sin calles peronistas, por elección.

| Año | Tipo | CON calles (%) | SIN calles (%) | Δ (pp) | *p* |
|---:|:---|---:|---:|---:|:---|
| 2011 | Presidencial | 62,9 | 57,3 | +5,6 | 0,002 |
| 2013 | Legislativa | 26,7 | 21,2 | +5,5 | 0,001 |
| 2015 | Presidencial | 47,9 | 39,1 | +8,8 | 0,001 |
| 2017 | Legislativa | 5,5 | 4,8 | +0,7 | 0,001 |
| 2019 | Jefe de Gobierno | 47,7 | 39,7 | +8,0 | 0,004 |
| 2019 | Presidencial | 49,2 | 41,4 | +7,8 | 0,005 |
| 2021 | Legislativa | 29,8 | 24,6 | +5,2 | 0,003 |
| 2023 | Jefe de Gobierno | 36,7 | 31,5 | +5,2 | 0,004 |
| 2023 | Presidencial | 39,8 | 34,8 | +5,0 | 0,008 |
| 2025 | Legislativa | 33,6 | 28,2 | +5,4 | 0,003 |
| **Promedio** | | **38,6** | **32,2** | **+5,7** | |

La diferencia es significativa en las **diez de diez** elecciones, incluyendo 2017 —la elección menos favorable para el PJ en este período—, aunque con una diferencia absoluta notablemente menor (+0,7 pp) en ese caso. El promedio de la diferencia es de 5,7 pp, con variación entre +0,7 pp (mínimo, legislativas 2017) y +8,8 pp (máximo, presidenciales 2015).

La Figura 3 presenta la serie temporal completa: dos curvas con bandas de error estándar para los grupos "con calles PJ" y "sin calles PJ", y un panel inferior de barras que cuantifica la diferencia en cada elección. La estabilidad del efecto a lo largo de un período que cubre contextos electorales tan heterogéneos —desde la hegemónica victoria kirchnerista de 2011 hasta la derrota presidencial de 2023— sugiere que el mecanismo subyacente es estructural y no coyuntural.

---

## 5. Discusión

### 5.1 Por qué la densidad no predice el voto

El resultado nulo de H1 admite al menos tres interpretaciones complementarias que merecen consideración antes de concluir que no existe relación alguna entre nomenclatura y comportamiento electoral.

En primer lugar, el indicador *pct_metros* mide **composición relativa**, no magnitud absoluta. Un circuito donde la única calle política es peronista tiene *pct_metros* = 100%; un circuito con veinte calles políticas de las cuales doce son peronistas tiene *pct_metros* = 60%. Ambas situaciones difieren radicalmente en términos de la "densidad simbólica" que experimenta el residente, pero el indicador los aproxima. La densidad absoluta (*metros_por_km²*) corrige parcialmente este problema, pero tampoco resulta predictiva.

En segundo lugar, la evidencia muestra que **dentro** de los 23 circuitos con calles PJ, el coeficiente de Spearman entre *pct_metros* y voto PJ es negativo aunque no significativo (*ρ* = −0,28, *p* = 0,21). Los circuitos con proporción más alta de calles peronistas —incluyendo algunos con *pct_metros* = 100%— no son los que obtienen mayores porcentajes de voto PJ; de hecho, tienden a ser inferiores a los circuitos con *pct_metros* intermedio (40-60%). Una hipótesis explicativa es que el PJ concentró nombres en territorios **periféricos o en disputa** donde necesitaba afirmar simbólicamente su presencia, mientras que sus fortalezas electorales más densas —Soldati, Lugano, Mataderos— tienen, en términos relativos, menor proporción de calles peronistas porque albergan también más calles con nombres no partidarios (de próceres, números, accidentes geográficos, etc.).

En tercer lugar, para el caso del Liberalismo la varianza del voto es tan reducida que la correlación no podría resultar significativa con ningún tamaño de muestra razonable: el desvío estándar del porcentaje de votos al Liberalismo en los circuitos de CABA es de apenas 2,26 pp (rango: 17,5%-27,2%). Los votantes liberales están distribuidos de manera casi uniforme en la ciudad, lo que torna imposible detectar variación electoral asociada a la variación geográfica de los topónimos.

### 5.2 La UCR y los costos de la omnipresencia

El partido con mayor cobertura en el callejero —la UCR, presente en 92 de los 167 circuitos— es el único para el que la presencia binaria no predice el voto (*p* = 0,309). La paradoja es solo aparente. Precisamente porque la UCR gobernó CABA durante períodos prolongados del siglo XX y distribuyó nombres en toda la geografía porteña —incluyendo barrios del sur históricamente peronistas—, la variable *presencia_UCR* carece de poder discriminante entre las distintas identidades político-territoriales de la ciudad. La ubicuidad destruye la capacidad clasificatoria del marcador.

Este resultado tiene implicaciones para la teoría del marcador territorial: el poder predictivo de los topónimos políticos depende de que la nomenclatura haya sido **focalizada** geográficamente. Un partido que concentra nombres en sus zonas de dominio histórico conserva la señal; uno que los distribuyó de manera más universalista la pierde.

### 5.3 El PS y el sedimento histórico

La correlación negativa entre densidad de calles socialistas y voto PS (*ρ* = −0,39) se vuelve inteligible en perspectiva histórica. El socialismo porteño tuvo su apogeo en las primeras décadas del siglo XX, cuando dominaba los barrios de trabajadores calificados y profesionales del centro-norte (comunas 5, 6, 14, 15). Ese espacio social fue luego disputado y parcialmente capturado por el peronismo en la segunda mitad del siglo XX y por el radicalismo y el PRO desde los años ochenta en adelante. Las calles socialistas —Juan B. Justo, Alfredo Palacios, Mario Bravo— quedaron como sedimento histórico en zonas que evolucionaron electoralmente hacia el centroderecha.

Lejos de refutar la teoría del marcador territorial, este resultado la confirma en una dirección temporal: los nombres fueron puestos donde el partido era fuerte. El problema es que el tiempo erosionó la coincidencia entre geografía de los nombres y geografía del voto. Las calles no se actualizaron; el electorado, sí.

### 5.4 El PJ y la persistencia territorial

El resultado más robusto del artículo —diferencia de 5,7 pp en las diez de diez elecciones— es consistente con la tesis del territorio político histórico. La geografía electoral del PJ en CABA es una de las más estables del sistema político argentino. El sur de la ciudad —La Boca, Barracas, Nueva Pompeya, Villa Lugano, Soldati, Mataderos— concentra históricamente el voto peronista y fue también el espacio donde el primer peronismo (1946-1955) concentró su acción simbólica en materia de nomenclatura. Los circuitos con calles peronistas no votan más al PJ *porque* las calles los influyen; votan más al PJ *y* tienen calles peronistas porque ambos son manifestaciones del mismo territorio histórico.

Esta interpretación —los topónimos como *proxy* de territorio antes que como causa del voto— tiene implicaciones para el diseño de futuros estudios. Un experimento natural que analizara cambios exógenos de nombres de calle (como los producidos por las ordenanzas de la dictadura 1976-1983 o las restituciones posteriores) en áreas de adhesión partidaria conocida permitiría separar el efecto causal del efecto de selección.

### 5.5 Limitaciones

**Fecha de denominación.** La limitación más importante de este trabajo es la ausencia de datos sobre cuándo fue asignado cada nombre. La información existe en los archivos de la Dirección General de Nomenclatura de la Ciudad, pero no está disponible en formato estructurado y abierto. Con ese dato sería posible testear si los nombres asignados durante gobiernos específicos predicen mejor el voto en las elecciones contemporáneas a su asignación que el voto actual.

**Causalidad.** El diseño observacional no permite distinguir entre los tres mecanismos teóricos propuestos (reflejo, refuerzo, señalización). Los resultados son compatibles con el mecanismo de *reflejo histórico* y no permiten confirmar ni descartar los mecanismos de *refuerzo identitario* o *señalización de dominio*.

**Cobertura del matching.** El 78,5% de los segmentos viales no fue asignado a ninguna figura política. Una cobertura mayor podría modificar los resultados, aunque es poco probable que lo haga de manera sustancial dado que las calles sin nombre político están distribuidas de manera relativamente uniforme en la ciudad.

**N reducido para el PJ.** Con solo 23 circuitos, el análisis PJ es estadísticamente potente gracias al tamaño del efecto, pero la pequeñez de la muestra invita a la cautela en la generalización.

---

## 6. Conclusiones

Este artículo partió de la hipótesis de que la densidad de calles con nombres de figuras de un partido político predice la adhesión electoral a ese partido en los circuitos de CABA. Esa hipótesis, en su formulación continua, fue rechazada para todos los partidos y todos los indicadores de densidad.

Sin embargo, la reformulación binaria de la hipótesis —¿tiene el circuito alguna calle del partido, sí o no?— produce un resultado robusto y temporalmente estable para el caso del PJ: los 23 circuitos con calles peronistas votan sistemáticamente más al PJ que los 144 circuitos sin ellas, con una diferencia promedio de 5,7 pp que se mantiene significativa en las diez elecciones del período 2011-2025 (Mann-Whitney, *p* < 0,01 en todos los casos; *d* de Cohen = 0,83).

La interpretación más parsimoniosa de este resultado es que los nombres de calle funcionan como **marcadores de territorio político histórico**: registran el dominio que un partido ejerció sobre una zona de la ciudad en el pasado y son, al mismo tiempo, indicadores de una identidad colectiva territorial que persiste en el presente electoral. No son causa del voto; son co-síntoma del mismo fenómeno subyacente.

Para la UCR, la distribución geográfica excesivamente amplia de su nomenclatura diluyó la señal territorial. Para el PS, el desfase temporal entre la geografía de sus nombres y la geografía de su voto actual ilustra cómo el sedimento simbólico puede sobrevivir a la reconfiguración del electorado. Para el Liberalismo, la baja varianza espacial del voto hace indetectable cualquier efecto.

El resultado del PJ, por su magnitud, consistencia y replicabilidad a lo largo de quince años de competencia electoral, constituye una contribución empírica al estudio de la relación entre espacio construido e identidad política en ciudades latinoamericanas. La agenda pendiente incluye la obtención de los años de denominación de cada calle para testear la hipótesis temporal, la extensión del análisis a otras ciudades argentinas con mayor presencia de calles peronistas, y el diseño de estrategias de identificación causal que permitan separar el efecto de reflejo del efecto de refuerzo.

---

## Referencias

Agnew, J. (2002). *Place and politics in modern Italy*. University of Chicago Press.

Azaryahu, M. (1996). The power of commemorative street names. *Environment and Planning D: Society and Space*, *14*(3), 311–330. https://doi.org/10.1068/d140311

Azaryahu, M. (2011). The politics of commemorative street renaming: After Reunification Berlin. *Journal of Historical Geography*, *37*(4), 483–492. https://doi.org/10.1016/j.jhg.2011.08.001

Calvo, E., y Escolar, M. (2005). *La nueva política de partidos en la Argentina: crisis política, realineamientos partidarios y reforma electoral*. Prometeo Libros.

Jelin, E. (2002). *Los trabajos de la memoria*. Siglo XXI Editores.

Johnston, R., Pattie, C., Dorling, D., y Rossiter, D. (2000). *From votes to seats: The operation of the UK electoral system since 1945*. Manchester University Press.

Light, D. (2004). Street names in Bucharest, 1990–1997: Exploring the modern historical geographies of post-socialist change. *Journal of Historical Geography*, *30*(1), 154–172. https://doi.org/10.1016/S0305-7488(02)00102-8

Lorenz, F. (2006). El presente en el pasado: El peronismo en la memoria argentina. *Iberoamericana*, *6*(22), 105–118.

Lupu, N., y Stokes, S. (2009). The social bases of political parties in Argentina, 1912–2003. *Latin American Research Review*, *44*(1), 58–87. https://doi.org/10.1353/lar.0.0066

Maronese, L., Muzzio, H., y Yujnovsky, O. (2007). *Buenos Aires, ciudad y política: Una mirada histórica*. Ediciones del Gobierno de la Ciudad de Buenos Aires.

Rose-Redwood, R., Alderman, D., y Azaryahu, M. (2010). Geographies of toponymic inscription: New directions in critical place-name studies. *Progress in Human Geography*, *34*(4), 453–470. https://doi.org/10.1177/0309132509351042

Vommaro, G., y Morresi, S. (2014). *"Hagamos equipo": PRO y la construcción de la nueva derecha en Argentina*. Ediciones UNGS.

Zajonc, R. B. (1968). Attitudinal effects of mere exposure. *Journal of Personality and Social Psychology*, *9*(2), 1–27. https://doi.org/10.1037/h0025848

---

## Apéndice A. Notas metodológicas sobre el pipeline computacional

El análisis se realizó íntegramente en Python 3.12 sobre Windows 10 (64 bits). Los scripts se ejecutan en el siguiente orden:

1. **`wiki.py`** — Descarga figuras políticas desde Wikidata mediante consultas SPARQL (presidentes, políticos del siglo XX/XXI, próceres pre-1850). Genera `figuras_con_partido.csv` y `figuras_proceres.csv`.

2. **`wikidata_calles.py`** — Consulta la propiedad P138 para entidades ubicadas en CABA; normaliza nombres y cruza con el callejero por *exact match* y *substring bidireccional*. Genera `callejero_wikidata_match.csv`.

3. **`ner.py`** — Realiza el *matching* textual sobre los segmentos no cubiertos por P138; integra ambas fuentes con prioridad para P138. Genera `callejero_matched.csv` y `callejero_no_match.csv`.

4. **`normalizar_electoral.py`** — Unifica diez archivos electorales en un CSV normalizado con variable `partido_electoral` (Opción B: UCR y PRO → "Centroderecha").

5. **`spatial_join.py`** — *Spatial join* calles → circuitos por centroide (EPSG:22185); agrega controles censales por *spatial join* de radios censales. Genera `data/tabla_analisis.csv`.

6. **`analisis_moran.py`** — Correlaciones de Spearman (bivariada y parcial), prueba de Mann-Whitney, *I* de Moran global, LISA, scatter plots. Genera `output_capa4/`.

7. **`visualizaciones_paper.py`** — Figuras del paper. Genera `output_paper/`.

Todos los datos de entrada son de acceso público: callejero oficial GCBA, resultados electorales DINE, microdatos del Censo 2022 (INDEC), Wikidata (licencia CC0).
