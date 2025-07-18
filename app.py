import streamlit as st
import pandas as pd
from PIL import Image
import base64
from io import BytesIO
import re
import random
import os

# === Configuración de la página ===

st.set_page_config(page_title="Mundo Peces Agua Fría", page_icon="imagenes/mundopeces_icon.ico")

#  === Inyección de estilos adaptativos  === 
st.markdown("""
    <style>
    /* === MODO OSCURO === */
    @media (prefers-color-scheme: dark) {
        body, .stApp {
            background-color: #1e2a33 !important;
            color: #ecf0f1 !important;
        }

        section[data-testid="stSidebar"] {
            background-color: #2c3e50 !important;
            color: #ecf0f1 !important;
        }

        .stSidebar .css-1cypcdb,
        .stSidebar .css-1v3fvcr,
        .stSidebar .css-qbe2hs {
            color: #ecf0f1 !important;
        }

        .stRadio > label,
        .stSelectbox label,
        .stTextInput label {
            color: #ecf0f1 !important;
        }

        .css-1offfwp {
            color: #ecf0f1 !important;
        }

        .css-1cpxqw2, .css-1d391kg {
            background-color: #34495e !important;
            color: #ffffff !important;
        }

        .titulo-principal {
            color: #5dade2 !important;
            font-weight: bold;
        }

        .subtitulo-principal {
            color: #a9cce3 !important;
        }

        h2, h3 {
            color: #ecf0f1 !important;
        }

        .stButton>button:hover {
            background-color: #5dade2 !important;
            color: black !important;
        }

        a {
            color: #5dade2 !important;
        }
    }

    /* === MODO CLARO === */
    @media (prefers-color-scheme: light) {
        body, .stApp {
            background-color: #ecf0f1 !important;
            color: #1e2a33 !important;
        }

        section[data-testid="stSidebar"] {
            background-color: #dce6f1 !important;
            color: #1e2a33 !important;
        }

        .stSidebar .css-1cypcdb,
        .stSidebar .css-1v3fvcr,
        .stSidebar .css-qbe2hs {
            color: #1e2a33 !important;
        }

        .stRadio > label,
        .stSelectbox label,
        .stTextInput label {
            color: #1e2a33 !important;
        }

        .css-1offfwp {
            color: #1e2a33 !important;
        }

        .css-1cpxqw2, .css-1d391kg {
            background-color: #ffffff !important;
            color: #1e2a33 !important;
        }

        .titulo-principal {
            color: #2c3e50 !important;
            font-weight: bold;
        }

        .subtitulo-principal {
            color: #34495e !important;
        }

        h2, h3 {
            color: #1e2a33 !important;
        }

        .stButton>button:hover {
            background-color: #2c3e50 !important;
            color: white !important;
        }

        a {
            color: #2c3e50 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)


# === Encabezado ===

# Convertir imagen a base64
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Cargar y convertir imagen
logo = Image.open("imagenes/icon.png").convert("RGBA")
logo_base64 = image_to_base64(logo)

# Encabezado
col1, col2 = st.columns([1, 5])  # mantener buen ancho para el logo

with col1:
    st.markdown(
        f"""
        <div style='display: flex; align-items: center; justify-content: flex-start; margin-top: 30px;'>
            <img src='data:image/png;base64,{logo_base64}' width='90'>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(f"""
        <div id='encabezado-app' style='padding-top: 10px; line-height: 1.2; margin-top: 20px;'>
            <div class='titulo-principal'>Mundo Peces Agua Fría</div>
            <div class='subtitulo-principal'>Guía de crianza y cuidados de peces de agua fría</div>
        </div>

        <style>
        @media (prefers-color-scheme: dark) {{
            .titulo-principal {{
                font-size: 42px;
                font-weight: bold;
                color: #e53935 !important;
            }}
            .subtitulo-principal {{
                font-size: 28px;
                color: #cccccc !important;
            }}
        }}
        @media (prefers-color-scheme: light) {{
            .titulo-principal {{
                font-size: 42px;
                font-weight: bold;
                color: #e53935 !important;
            }}
            .subtitulo-principal {{
                font-size: 28px;
                color: gray !important;
            }}
        }}
        </style>
    """, unsafe_allow_html=True)

# Línea separadora
st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# === Cargar datos ===
fichas = pd.read_excel("data/base.xlsx", sheet_name="ficha")
recursos = pd.read_excel("data/base.xlsx", sheet_name="recurso")

# === Sidebar ===
st.sidebar.title("Opciones")

# === Paso 1: Aplicar filtro por palabra clave ===
palabra_clave = st.session_state.get("palabra_clave_input", "").strip().lower()

fichas_filtradas = fichas.copy()
if palabra_clave:
    def peces_con_palabra(df, col_pez="pez"):
        df = df.copy()
        df = df.fillna("").astype(str)
        df["texto_total"] = df.drop(columns=[col_pez]).agg(" ".join, axis=1).str.lower()
        # Coincidencia también en el nombre del pez
        coincidencias_nombre = df[df[col_pez].str.lower().str.contains(palabra_clave)][col_pez]
        coincidencias_texto = df[df["texto_total"].str.contains(palabra_clave)][col_pez]
        return set(coincidencias_nombre) | set(coincidencias_texto)
    
    def peces_con_palabra_en_fichas(df, col_pez="pez"):
        df = df.copy()
        df = df.fillna("").astype(str)
        texto_filas = df.drop(columns=[col_pez]).agg(" ".join, axis=1).str.lower()

        # Coincidencia en columnas (nombres de columna)
        columnas_con_match = [col for col in df.columns if palabra_clave in col.lower()]

        desde_texto = df[texto_filas.str.contains(palabra_clave)][col_pez]
        desde_nombre = df[df[col_pez].str.lower().str.contains(palabra_clave)][col_pez]

        if columnas_con_match:
            cols_numericas = df[columnas_con_match].apply(pd.to_numeric, errors='coerce').fillna(0)
            desde_columnas = df[cols_numericas.sum(axis=1) > 0][col_pez]
        else:
            desde_columnas = pd.Series([], dtype=str)

        return set(desde_texto) | set(desde_nombre) | set(desde_columnas)

    # Unimos los resultados de todas las fuentes
    peces_validos = sorted(set(
        peces_con_palabra(fichas) |
        peces_con_palabra_en_fichas(recursos)
    ))

    # Filtrar
    fichas_filtradas = fichas[fichas["pez"].isin(peces_validos)]
    recursos_filtrados = recursos[recursos["pez"].isin(peces_validos)]

else:
    recursos_filtrados = recursos

# === Paso 2: Obtener opciones disponibles actualizadas ===
especies_disponibles = (
    fichas_filtradas["Especie"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

# === Paso 3: Obtener selección actual o default ===
especie_actual = st.session_state.get("especie_sel", "Todos")

# === Paso 4: Selector de especie ===
# Armamos el selector dinámicamente
opciones_especie = ["Todos"] + sorted(especies_disponibles)

especie_sel = st.sidebar.selectbox(
    "Filtra por especie",
    opciones_especie,
    index=opciones_especie.index(especie_actual)
    if especie_actual in opciones_especie else 0,
    key="especie_sel"
)

# === Paso 5: Aplicar filtro por especie ===
if especie_sel != "Todos":
    fichas_final = fichas_filtradas[fichas_filtradas["Especie"] == especie_sel]
else:
    fichas_final = fichas_filtradas.copy()

# === Paso 6: Mostrar campo de búsqueda por palabra clave ===
palabra_clave_input = st.sidebar.text_input(
    "Buscar por palabra clave",
    value=st.session_state.get("palabra_clave_input", ""),
    key="palabra_clave_input",
    placeholder="Ej: omnívoros, arvejas, alimento vivo",
    help="Escribe una palabra y presiona Enter para buscar"
)

# === Paso 7: Selector de peces dependiente ===
peces = sorted(fichas_final["pez"].dropna().unique())

if peces:
    pez_sel = st.sidebar.selectbox(
        "Selecciona una variedad",
        peces,
        index=peces.index(
            st.session_state.pez_sel
        ) if "pez_sel" in st.session_state and st.session_state.pez_sel in peces else peces.index(random.choice(peces)),
        key="pez_sel"
    )
else:
    if "pez_sel" in st.session_state:
        del st.session_state["pez_sel"]
    st.sidebar.warning("No hay peces para esa búsqueda, inténtalo otra vez.")
    st.stop()

# === Cálculo  ===

# Escoger unidad de medida  
unidad_opciones = {
    "Litros (L)": "L",
    "Metros Cúbicos (m³)": "m3"
}

unidad_label = st.sidebar.radio(
    "Unidad de medida", 
    list(unidad_opciones.keys()),
    key="unidad_label"
)
unidad = unidad_opciones[unidad_label]

# Factor de conversión: convertir a litros
factor_conversion = 1 if unidad == "L" else 1000

# Input: número de peces
cantidad = st.sidebar.number_input(
    "Número de peces", 
    min_value=1, 
    key="cantidad"
)

volumen_deseado = None
litros = None

# === Verificar selección válida de pez antes de continuar ===
if pez_sel:
    ficha_seleccionada = fichas_final[fichas_final["pez"] == pez_sel]
    
    if not ficha_seleccionada.empty:
        fila_ficha = ficha_seleccionada.iloc[0]
    else:
        st.warning("No se encontró información para el pez seleccionado.")
        st.stop()
else:
    st.info("Selecciona un pez para ver los detalles.")
    st.stop()

# === Obtener datos de la ficha seleccionada ===
campos = fila_ficha.drop([col for col in [
    "Especie",
    "Temperatura Mínima",
    "Temperatura Máxima",
    "Tamaño Corporal Máximo"
] if col in fila_ficha.index])

datos = fila_ficha.drop([col for col in [
    "Tamaño Mínimo Acuario"
] if col in fila_ficha.index])

# === Botón de limpiar filtros ===
CAMPOS_RESET = ["especie_sel", "pez_sel", "unidad_label", "cantidad", "palabra_clave_input"]

if st.sidebar.button("Limpiar selección"):
    for clave in CAMPOS_RESET:
        st.session_state.pop(clave, None)
    st.session_state["cantidad"] = 1  # <--- Establece cantidad en 1 explícitamente
    st.rerun()

# === Cantidad de variedades de peces ===
st.sidebar.markdown("---")  # línea separadora

total_peces = fichas["pez"].nunique()

st.sidebar.markdown(f"""
<div style='text-align: justify; font-style: italic; font-size: 13px;'>
    <p><b>Mundo Peces Agua Fría</b> es una aplicación interactiva enfocada en peces de agua fría creada por aficionados de la acuariofilia, que buscan compartir tips de crianza y cuidados.</p>
    <p>Actualmente incluye <b>{total_peces}</b> variedades de peces.</p>
    <p>Contenido por Scarlet Silva Faúndez y xxx (Santiago de Chile, 2025).</p>
    <p style="margin-top:10px;">
        <a href="mailto:sscarletandrea@gmail.com" target="_blank" style="text-decoration: none;">
            <img src="https://img.icons8.com/color/24/000000/gmail-new.png" style="vertical-align: middle;"/> sscarletandrea@gmail.com
        </a><br>
        <a href="mailto:xxx@gmail.com" target="_blank" style="text-decoration: none;">
            <img src="https://img.icons8.com/color/24/000000/gmail-new.png" style="vertical-align: middle;"/> xxx@gmail.com
        </a><br>
    <p>Aplicación desarrollada por Carlos Andrés González Miranda (Santiago de Chile, 2025).</p>
    <p style="margin-top:10px;">
        <a href="mailto:cargomida@gmail.com" target="_blank" style="text-decoration: none;">
            <img src="https://img.icons8.com/color/24/000000/gmail-new.png" style="vertical-align: middle;"/> cargomida@gmail.com
        </a><br>
    <p>Redes sociales:</p>
        <a href="https://www.instagram.com/mundopeces_aguafria" target="_blank" style="text-decoration: none;">
            <img src="https://img.icons8.com/fluency/24/000000/instagram-new.png" style="vertical-align: middle;"/> @mundopeces_aguafria
        </a>
    </p>
</div>
""", unsafe_allow_html=True)

# === Visualización central ===

st.markdown(f"<h3 style='font-size: 48px; color: #2c3e50; font-weight: bold;'>{pez_sel}</h3>", unsafe_allow_html=True)

# Mostrar imagen si existe
image_path = f"imagenes/{pez_sel}.jpg"
if os.path.exists(image_path):
    st.image(image_path, width=400)
else:
    st.info("Imagen no disponible para este pez.") 

# === Calcular tamaño mínimo del acuario ajustado a la cantidad de peces y unidad ===
tamaño_base_litros = fila_ficha["Tamaño Mínimo Acuario"]
tamaño_total_litros = tamaño_base_litros * cantidad
tamaño_convertido = tamaño_total_litros / factor_conversion
unidad_display = "litros" if unidad == "L" else "m³"
tamaño_formateado = (
    f"{tamaño_convertido:.2f}".replace(".", ",") if unidad == "m3"
    else f"{int(tamaño_convertido)}"
)

# === Ficha HTML con datos principales ===
ficha_html = f"""
<style>
.ficha-bloque {{
    border-radius: 10px;
    padding: 20px;
    margin-top: 20px;
    border: 1px solid;
}}

@media (prefers-color-scheme: dark) {{
    .ficha-bloque {{
        background-color: #2c3e50;
        border-color: #5dade2;
        color: #ecf0f1;
    }}
}}

@media (prefers-color-scheme: light) {{
    .ficha-bloque {{
        background-color: #f9f9f9;
        border-color: #ddd;
        color: #1e2a33;
    }}
}}
</style>

<div class="ficha-bloque">
    <p><strong>🌍 Especie:</strong> {fila_ficha['Especie']}</p>
    <p><strong>🌡️ Temperatura mínima:</strong> {fila_ficha['Temperatura Mínima']} °C</p>
    <p><strong>🌡️ Temperatura máxima:</strong> {fila_ficha['Temperatura Máxima']} °C</p>
    <p><strong>📏 Tamaño corporal máximo:</strong> {fila_ficha['Tamaño Corporal Máximo']} cm</p>
    <p><strong>🏠 Tamaño mínimo del acuario o estanque:</strong> {tamaño_formateado} {unidad_display}</p>
</div>
"""
st.markdown(ficha_html, unsafe_allow_html=True)

# === Sección recursos asociados ===
recurso_fila = recursos[recursos["pez"] == pez_sel]
if not recurso_fila.empty:
    fila = recurso_fila.iloc[0]

    # === Información sobre la variedad ===
    campos_variedad = {
        "Descripción": "Descripción",
        "Origen": "Origen",
        "Alimentación": "Alimentación",
        "Dimorfismo sexual": "Dimorfismo sexual",
        "Reprodución": "Reproducción",
        "Acidez y dureza del dgua": "Acidez y Dureza del Agua",
        "Enriquecimiento ambiental": "Ambiente",
        "Filtración": "Filtracion"
    }

    hay_variedad = any(
        pd.notna(fila.get(campo)) and str(fila.get(campo)).strip() != ""
        for campo in campos_variedad.values()
    )

    if hay_variedad:
        st.markdown("---")
        st.markdown(
            "<h2 style='color: #e65100; font-size: 36px; font-weight: bold;'>Información sobre la variedad</h2>",
            unsafe_allow_html=True
        )

        def mostrar_bloque(titulo, campo):
            valor = fila.get(campo)
            if pd.notna(valor) and str(valor).strip().lower() not in ["", "none", "nan"]:
                contenido = str(valor).strip()
                st.markdown(f"### {titulo}")
                st.markdown(
                    f"<div style='font-size: 15px; text-align: justify;'>{contenido}</div>",
                    unsafe_allow_html=True
                )

        for titulo, campo in campos_variedad.items():
            mostrar_bloque(titulo, campo)

    # === Recursos adicionales ===
    hay_recursos = any([
        pd.notna(fila.get("Datos Curiosos")) and str(fila.get("Datos Curiosos")).strip() != "",
        pd.notna(fila.get("texto_enlace_1")) and pd.notna(fila.get("url_1")),
        pd.notna(fila.get("texto_enlace_2")) and pd.notna(fila.get("url_2")),
    ])

    if hay_recursos:
        st.markdown("---")
        st.markdown(
            "<h2 style='color: #2c3e50; font-size: 36px; font-weight: bold;'>Recursos adicionales</h2>",
            unsafe_allow_html=True
        )

        # Bloque de datos curiosos
        if pd.notna(fila.get("Datos Curiosos")) and str(fila.get("Datos Curiosos")).strip() != "":
            st.markdown("### Datos curiosos")
            st.markdown(
                f"<div style='font-size: 15px; text-align: justify;'>{fila['Datos Curiosos'].strip()}</div>",
                unsafe_allow_html=True
            )

        # Enlace 1
        if pd.notna(fila.get("texto_enlace_1")) and pd.notna(fila.get("url_1")):
            st.markdown("### Video recomendado")
            st.markdown(
                f'<a href="{fila["url_1"]}" target="_blank"> {fila["texto_enlace_1"]}</a>',
                unsafe_allow_html=True
            )

        # Enlace 2
        if pd.notna(fila.get("texto_enlace_2")) and pd.notna(fila.get("url_2")):
            st.markdown("### Mira también lo siguiente")
            st.markdown(
                f'<a href="{fila["url_2"]}" target="_blank"> {fila["texto_enlace_2"]}</a>',
                unsafe_allow_html=True
            )
