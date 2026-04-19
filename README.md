# Generador de Etiquetas en PDF con Flask

Aplicación web desarrollada con **Python y Flask** para la generación automática de **etiquetas en formato PDF**, ideal para productos, envíos o identificación de artículos.

El sistema permite generar etiquetas de forma rápida y estructurada, listas para imprimir.

---

## Descripción

Este proyecto permite crear etiquetas en PDF a partir de datos definidos por el usuario, automatizando un proceso que normalmente se realiza de forma manual.

Está pensado para negocios que necesitan generar etiquetas de manera frecuente, como:

- tiendas
- almacenes
- logística
- productos alimenticios
- envíos

---

## Características principales

- Generación de etiquetas en formato PDF
- Diseño listo para impresión
- Generación dinámica desde datos ingresados
- Interfaz web sencilla
- Descarga directa del PDF
- Posibilidad de generar múltiples etiquetas

---

## Tecnologías utilizadas

- **Python**
- **Flask**
- **ReportLab / FPDF** (según lo que estés usando)
- **HTML / CSS**
- **Bootstrap** (si lo estás usando)

---

## Funcionamiento

1. El usuario introduce los datos necesarios (nombre, código, descripción, etc.)
2. El sistema procesa la información
3. Se genera un archivo PDF con las etiquetas
4. El usuario puede descargar e imprimir el documento

---

## Estructura del proyecto

```bash
/etiquetas-pdf
│
├── app.py
├── requirements.txt
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   └── img/
│
└── utils/
    └── generar_pdf.py
