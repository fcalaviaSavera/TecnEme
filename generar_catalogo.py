from pathlib import Path
from pypdf import PdfReader
from collections import defaultdict
import re

# ======================================
# CARPETAS ORIGEN
# ======================================

carpetas = [
    Path(r"U:\CATALOGO TECNICO\CATALOGO TECNICO"),
    Path(r"U:\CATALOGO TECNICO\Fichas NO distribuidas")
]

# ======================================
# CARPETA DESTINO
# ======================================

docs = Path("docs/fichas")
docs.mkdir(parents=True, exist_ok=True)

indice = []
familias = defaultdict(list)

# ======================================
# FUNCIONES
# ======================================

def obtener_estado(pdf):

    ruta = str(pdf)

    if "Obsoletas" in ruta:
        return "Obsoleta"

    if "Fichas NO distribuidas" in ruta:
        return "No distribuida"

    return "Distribuida"


def obtener_edicion(nombre):

    m = re.search(
        r"Ed[\s\._-]*(\d+)",
        nombre,
        re.IGNORECASE
    )

    if m:
        return m.group(1)

    return "No identificada"


def obtener_referencia(nombre):

    patrones = [
        r"CAB-[A-Z0-9_/-]+",
        r"CEP-[A-Z0-9_/-]+",
        r"CHM-[A-Z0-9_/-]+",
        r"CHP-[A-Z0-9_/-]+",
        r"CEM-[A-Z0-9_/-]+",
        r"CAH-[A-Z0-9_/-]+",
        r"PAC-[A-Z0-9_/-]+",
        r"PCS-[A-Z0-9_/-]+",
        r"CC-[A-Z0-9_/-]+",
        r"BAG-[A-Z0-9_/-]+",
        r"PFSCM-[A-Z0-9_/-]+",
        r"PSP-[A-Z0-9_/-]+",
        r"BPRA-[A-Z0-9_/-]+",
        r"BT[0-9]+",
        r"TMH",
        r"TMF",
        r"S1P",
        r"S2P",
        r"SPH",
        r"SEN-P",
        r"SEN-M",
        r"QMC[0-9A-Z_/-]+",
        r"Q0_Q1X"
    ]

    for patron in patrones:

        m = re.search(
            patron,
            nombre,
            re.IGNORECASE
        )

        if m:
            return m.group(0).upper()

    return "No identificada"


def obtener_familia(referencia):

    if referencia == "No identificada":
        return "OTROS"

    if "-" in referencia:
        return referencia.split("-")[0]

    return referencia


# ======================================
# GENERAR FICHAS
# ======================================

for carpeta in carpetas:

    print(f"Leyendo: {carpeta}")

    for pdf in carpeta.rglob("*.pdf"):

        try:

            reader = PdfReader(str(pdf))

            texto = ""

            for pagina in reader.pages:

                try:
                    texto += pagina.extract_text() or ""
                    texto += "\n"
                except:
                    pass

            nombre = pdf.stem

            nombre_md = re.sub(
                r"[^\w\- ]",
                "",
                nombre
            )

            nombre_md = (
                nombre_md
                .replace(" ", "_")
                + ".md"
            )

            referencia = obtener_referencia(nombre)
            familia = obtener_familia(referencia)
            edicion = obtener_edicion(nombre)
            estado = obtener_estado(pdf)

            with open(
                docs / nombre_md,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(f"# {nombre}\n\n")

                f.write("## Datos de la ficha\n\n")

                f.write(
                    f"- **Referencia:** {referencia}\n"
                )

                f.write(
                    f"- **Familia:** {familia}\n"
                )

                f.write(
                    f"- **Edición:** {edicion}\n"
                )

                f.write(
                    f"- **Estado:** {estado}\n\n"
                )

                f.write(
                    f"**Archivo:** `{pdf}`\n\n"
                )

                f.write(
                    "## Extracto técnico\n\n"
                )

                f.write("```\n")
                f.write(texto[:50000])
                f.write("\n```\n")

            familias[familia].append(
                (nombre, nombre_md)
            )

            indice.append(
                (nombre, nombre_md)
            )

            print(
                f"OK: {familia} -> {nombre}"
            )

        except Exception as e:

            print(
                f"ERROR: {pdf}"
            )

            print(e)

# ======================================
# GENERAR CATÁLOGO
# ======================================

with open(
    "docs/catalogo.md",
    "w",
    encoding="utf-8"
) as f:

    f.write("# Catálogo técnico\n\n")

    f.write(
        f"Total de fichas: **{len(indice)}**\n\n"
    )

    for familia in sorted(familias.keys()):

        f.write(
            f"## {familia}\n\n"
        )

        f.write(
            f"Total: {len(familias[familia])} fichas\n\n"
        )

        for nombre, archivo in sorted(
            familias[familia]
        ):

            f.write(
                f"- [{nombre}](fichas/{archivo})\n"
            )

        f.write("\n")

print()
print(
    f"✅ Catálogo generado ({len(indice)} fichas)"
)