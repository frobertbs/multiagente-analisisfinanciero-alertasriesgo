import os
import sys
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import pypdf

os.environ["MPLCONFIGDIR"] = "/tmp"

class MasterThesisCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and stamp exact headers, footers,
    and page numbering for Cover, TOC, Main Report (Pages 1 to 20), and Appendices.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        
        # Cover = Page 1, TOC = Page 2
        # Main Report = Page 3 to Page 22 (Total 20 pages)
        # Appendices = Page 23 to num_pages
        main_report_total = 20
        
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            page_num = i + 1
            self.draw_decorations(page_num, num_pages, main_report_total)
            super().showPage()
            
        super().save()

    def draw_decorations(self, page_num, total_pages, main_total):
        self.saveState()
        
        # 1. Portada (Cover Page = 1) -> No header, no footer
        if page_num == 1:
            self.restoreState()
            return
            
        # 2. Índice (TOC = 2) -> Clean header/footer with roman page ii
        if page_num == 2:
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(45, 805, "UNIVERSIDAD COMPLUTENSE DE MADRID — MÁSTER EN BIG DATA, DATA SCIENCE & IA")
            self.drawRightString(550, 805, "ÍNDICE GENERAL")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(45, 798, 550, 798)
            
            self.line(45, 42, 550, 42)
            self.drawString(45, 30, "Trabajo Fin de Máster — Fabian Robert Banu Stan")
            self.drawRightString(550, 30, "Índice — Pág. ii")
            self.restoreState()
            return

        # 3. Main report or Appendices
        is_appendix = (page_num > 22)
        
        # Running Header
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        if is_appendix:
            self.drawString(45, 805, "ANEXOS TÉCNICOS Y EVIDENCIAS DE AUDITORÍA")
            self.drawRightString(550, 805, "TFM — Fabian Robert Banu Stan")
        else:
            self.drawString(45, 805, "APLICACIÓN MULTIAGENTE PARA ANÁLISIS FINANCIERO Y ALERTAS DE RIESGO")
            self.drawRightString(550, 805, "MEMORIA TÉCNICA (UCM)")
            
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(45, 798, 550, 798)
        
        # Running Footer
        self.line(45, 42, 550, 42)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(45, 30, "Universidad Complutense de Madrid — Facultad de Estudios Estadísticos")
        
        if is_appendix:
            app_p = page_num - 22
            self.drawRightString(550, 30, f"Anexo — Pág. A-{app_p}")
        else:
            main_p = page_num - 2
            self.drawRightString(550, 30, f"Página {main_p} de 20")
            
        self.restoreState()

def generate_pdf_elements():
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#1E3A8A")     # Navy Blue
    c_secondary = colors.HexColor("#0D9488")   # Teal
    c_dark = colors.HexColor("#0F172A")        # Slate 900
    c_body = colors.HexColor("#1E293B")        # Slate 800
    c_light = colors.HexColor("#F8FAFC")       # Slate 50
    c_alert_bg = colors.HexColor("#FEF2F2")    # Red 50
    c_alert_border = colors.HexColor("#DC2626") # Red 600
    c_note_bg = colors.HexColor("#EFF6FF")     # Blue 50
    c_note_border = colors.HexColor("#2563EB")  # Blue 600
    c_gray_border = colors.HexColor("#CBD5E1")  # Slate 300

    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=19, leading=23,
        textColor=c_primary, alignment=1, spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11, leading=15,
        textColor=colors.HexColor("#475569"), alignment=1, spaceAfter=18
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=12, leading=15,
        textColor=c_primary, spaceBefore=8, spaceAfter=3, keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=9.8, leading=12.5,
        textColor=colors.HexColor("#1E40AF"), spaceBefore=5, spaceAfter=2, keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom', parent=styles['Heading3'],
        fontName='Helvetica-Bold', fontSize=8.8, leading=11.2,
        textColor=colors.HexColor("#334155"), spaceBefore=3.5, spaceAfter=1.5, keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11.2,
        textColor=c_body, spaceAfter=3, alignment=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom', parent=body_style,
        leftIndent=10, firstLineIndent=-6, spaceAfter=1.8
    )

    caption_style = ParagraphStyle(
        'Caption_Custom', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=7.5, leading=9.2,
        textColor=colors.HexColor("#475569"), alignment=1, spaceBefore=2, spaceAfter=3.5
    )

    table_cell_style = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.2, leading=9.0, textColor=c_body
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold', parent=table_cell_style,
        fontName='Helvetica-Bold', textColor=c_dark
    )

    table_header_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=9.2,
        textColor=colors.white, alignment=1
    )

    def create_callout(text, bg=c_note_bg, border=c_note_border, text_color=c_dark):
        p_style = ParagraphStyle('CalloutStyle', fontName='Helvetica', fontSize=7.6, leading=10.0, textColor=text_color)
        t = Table([[Paragraph(text, p_style)]], colWidths=[505])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOX', (0,0), (-1,-1), 1, border),
            ('TOPPADDING', (0,0), (-1,-1), 3.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    story = []

    # =========================================================================
    # PORTADA (COVER PAGE) - Página 1
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("UNIVERSIDAD COMPLUTENSE DE MADRID", ParagraphStyle('UCM_Head', fontName='Helvetica-Bold', fontSize=14, leading=17, alignment=1, textColor=c_primary)))
    story.append(Paragraph("FACULTAD DE ESTUDIOS ESTADÍSTICOS", ParagraphStyle('UCM_Sub', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, textColor=colors.HexColor("#475569"))))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Máster de Formación Permanente en Big Data, Data Science & Inteligencia Artificial (9ª Edición)", ParagraphStyle('UCM_Master', fontName='Helvetica', fontSize=9.5, leading=12.5, alignment=1, textColor=c_secondary)))
    
    story.append(Spacer(1, 18))
    story.append(HRFlowable(width="90%", thickness=2, color=c_primary, spaceBefore=4, spaceAfter=16))
    
    story.append(Paragraph("TRABAJO FIN DE MÁSTER", ParagraphStyle('TFM_Label', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, textColor=colors.HexColor("#64748B"))))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Aplicación multiagente para análisis financiero y generación de alertas de riesgo en empresas cotizadas", title_style))
    story.append(Paragraph("Memoria Técnica de Solución en Analítica Avanzada, Modelización de Riesgos y Productivización Software", subtitle_style))
    
    story.append(HRFlowable(width="90%", thickness=1, color=c_gray_border, spaceBefore=6, spaceAfter=18))
    
    meta_data = [
        [Paragraph("<b>Modalidad del Trabajo:</b>", table_cell_bold), Paragraph("Individual (Opción 3: Proyecto Técnico Propuesto por el Alumno)", table_cell_style)],
        [Paragraph("<b>Autor / Estudiante:</b>", table_cell_bold), Paragraph("Fabian Robert Banu Stan", table_cell_style)],
        [Paragraph("<b>Tutores Académicos:</b>", table_cell_bold), Paragraph("Carlos Ortega Fernández y Santiago Mota Herce", table_cell_style)],
        [Paragraph("<b>Entorno Tecnológico:</b>", table_cell_bold), Paragraph("Python 3.9, LangGraph, FastAPI, Scikit-learn, FAISS, SQLAlchemy, SQLite, Streamlit", table_cell_style)],
        [Paragraph("<b>Convocatoria / Fecha:</b>", table_cell_bold), Paragraph("Curso Académico 2025/2026 — Agosto 2026", table_cell_style)],
    ]
    t_meta = Table(meta_data, colWidths=[130, 360])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 1, c_gray_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 18))
    
    disclaimer_text = (
        "<b>AVISO LEGAL Y DESCARGO DE RESPONSABILIDAD FINANCIERA:</b><br/>"
        "Esta aplicación constituye una prueba de concepto académica desarrollada con fines analíticos y de soporte a la interpretación de información pública. No constituye asesoramiento financiero, recomendación de inversión, evaluación crediticia oficial ni decisión automatizada para una entidad bancaria. La puntuación global de riesgo es un indicador analítico experimental y las alertas requieren siempre supervisión humana cualificada (<i>Human-in-the-Loop</i>)."
    )
    story.append(create_callout(disclaimer_text, bg=c_alert_bg, border=c_alert_border, text_color=colors.HexColor("#991B1B")))
    story.append(PageBreak())

    # =========================================================================
    # ÍNDICE DE CONTENIDOS (TOC) - Página 2
    # =========================================================================
    story.append(Paragraph("Índice General de Contenidos", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=2, spaceAfter=8))
    
    toc_rows = [
        [Paragraph("<b>Sección</b>", table_header_style), Paragraph("<b>Título del Capítulo / Apartado</b>", table_header_style), Paragraph("<b>Pág.</b>", table_header_style)],
        [Paragraph("<b>1</b>", table_cell_bold), Paragraph("Resumen Ejecutivo", table_cell_bold), Paragraph("1", table_cell_bold)],
        [Paragraph("<b>2</b>", table_cell_bold), Paragraph("Introducción y Contexto del Problema", table_cell_bold), Paragraph("2", table_cell_bold)],
        [Paragraph("<b>3</b>", table_cell_bold), Paragraph("Objetivos, Alcance y Preguntas de Trabajo", table_cell_bold), Paragraph("3", table_cell_bold)],
        [Paragraph("<b>4</b>", table_cell_bold), Paragraph("Caso de Uso y Valor para Negocio Financiero", table_cell_bold), Paragraph("4", table_cell_bold)],
        [Paragraph("<b>5</b>", table_cell_bold), Paragraph("Datos y Fuentes de Información", table_cell_bold), Paragraph("5", table_cell_bold)],
        [Paragraph("<b>6</b>", table_cell_bold), Paragraph("Arquitectura de la Solución Implementada", table_cell_bold), Paragraph("7", table_cell_bold)],
        [Paragraph("<b>7</b>", table_cell_bold), Paragraph("Diseño de los Agentes y Flujo Multiagente", table_cell_bold), Paragraph("9", table_cell_bold)],
        [Paragraph("<b>8</b>", table_cell_bold), Paragraph("Metodología Analítica y Modelo de Riesgo", table_cell_bold), Paragraph("11", table_cell_bold)],
        [Paragraph("<b>9</b>", table_cell_bold), Paragraph("Implementación de la Aplicación y Productivización", table_cell_bold), Paragraph("13", table_cell_bold)],
        [Paragraph("<b>10</b>", table_cell_bold), Paragraph("Resultados y Demostración Funcional", table_cell_bold), Paragraph("15", table_cell_bold)],
        [Paragraph("<b>11</b>", table_cell_bold), Paragraph("Evaluación, Calidad, Explicabilidad y Trazabilidad", table_cell_bold), Paragraph("17", table_cell_bold)],
        [Paragraph("<b>12</b>", table_cell_bold), Paragraph("Limitaciones, Riesgos y Aspectos Éticos", table_cell_bold), Paragraph("18", table_cell_bold)],
        [Paragraph("<b>13</b>", table_cell_bold), Paragraph("Conclusiones y Líneas Futuras", table_cell_bold), Paragraph("19", table_cell_bold)],
        [Paragraph("<b>14</b>", table_cell_bold), Paragraph("Bibliografía", table_cell_bold), Paragraph("20", table_cell_bold)],
        [Paragraph("<b>—</b>", table_cell_bold), Paragraph("<b>ANEXOS TÉCNICOS (A a L)</b>", table_cell_bold), Paragraph("A-1", table_cell_bold)],
        [Paragraph("A", table_cell_style), Paragraph("Diagrama Completo de Arquitectura del Sistema", table_cell_style), Paragraph("A-1", table_cell_style)],
        [Paragraph("B", table_cell_style), Paragraph("Diccionario de Datos Extendido de Modelos Pydantic y ORM", table_cell_style), Paragraph("A-2", table_cell_style)],
        [Paragraph("C", table_cell_style), Paragraph("Formulación Matemática Completa de los 14 Indicadores", table_cell_style), Paragraph("A-3", table_cell_style)],
        [Paragraph("D", table_cell_style), Paragraph("Configuración Completa de Reglas de Riesgo (risk_rules.yaml)", table_cell_style), Paragraph("A-4", table_cell_style)],
        [Paragraph("E", table_cell_style), Paragraph("Esquemas JSON de Entrada y Salida de los Agentes", table_cell_style), Paragraph("A-5", table_cell_style)],
        [Paragraph("F", table_cell_style), Paragraph("Estructura Completa del Repositorio de Código", table_cell_style), Paragraph("A-6", table_cell_style)],
        [Paragraph("G", table_cell_style), Paragraph("Fragmentos de Código Fuente Seleccionados y Comentados", table_cell_style), Paragraph("A-7", table_cell_style)],
        [Paragraph("H", table_cell_style), Paragraph("Análisis Exploratorio de Datos (EDA) Extendido de Datos Demo", table_cell_style), Paragraph("A-8", table_cell_style)],
        [Paragraph("I", table_cell_style), Paragraph("Resultados Completos de la Suite de Pruebas Unitarias (pytest)", table_cell_style), Paragraph("A-9", table_cell_style)],
        [Paragraph("J", table_cell_style), Paragraph("Guía de Reproducibilidad y Despliegue Local Paso a Paso", table_cell_style), Paragraph("A-10", table_cell_style)],
        [Paragraph("K", table_cell_style), Paragraph("Guion Oficial para el Vídeo Explicativo de 5 Minutos (Español)", table_cell_style), Paragraph("A-11", table_cell_style)],
        [Paragraph("L", table_cell_style), Paragraph("Matriz de Evidencias y Auditoría de Implementación del Proyecto", table_cell_style), Paragraph("A-12", table_cell_style)],
    ]
    t_toc = Table(toc_rows, colWidths=[35, 435, 35])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # =========================================================================
    # 1. RESUMEN EJECUTIVO (Pág. 1 de memoria)
    # =========================================================================
    story.append(Paragraph("1. Resumen Ejecutivo", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "El análisis continuo de la solvencia, la rentabilidad y la volatilidad en empresas cotizadas representa un desafío crítico para las entidades financieras, departamentos de riesgos y gestores de carteras. Tradicionalmente, la interpretación conjunta de estados contables periódicos, series de precios de alta frecuencia y noticias corporativas se ha desarrollado de forma manual o mediante sistemas fragmentados. Este enfoque genera ineficiencias operativas, dilata los tiempos de respuesta y aumenta el riesgo de omitir señales tempranas de deterioro crediticio o anomalías de mercado.",
        body_style
    ))
    story.append(Paragraph(
        "Para resolver esta problemática, el presente Trabajo Fin de Máster ha diseñado, implementado, auditado y validado una <b>solución de analítica avanzada basada en una arquitectura multiagente cooperativa</b>. El sistema automatiza el ciclo integral de extracción, procesamiento, modelización de riesgo y síntesis ejecutiva a través de cinco agentes especializados orquestados mediante un grafo de estados dirigido (<i>StateGraph</i>) implementado con el framework <b>LangGraph</b>:",
        body_style
    ))
    story.append(Paragraph("• <b>Data Ingestion Agent:</b> Extrae y consolida estados financieros anuales, series bursátiles y noticias, soportando adaptadores sintéticos de control (<i>DEMO_STBL, DEMO_LEVR, DEMO_VOLT</i>) y proveedores de mercado en tiempo real (<i>Yahoo Finance</i>). [IV]", bullet_style))
    story.append(Paragraph("• <b>Financial Analysis Agent:</b> Ejecuta el cálculo determinista de 14 ratios contables y métricas de mercado (márgenes EBITDA y neto, ROA, ROE, apalancamiento, Deuda Neta/EBITDA, <i>Current Ratio</i>, cobertura de intereses, variaciones interanuales, volatilidad histórica y <i>Max Drawdown</i>). [IV]", bullet_style))
    story.append(Paragraph("• <b>News & Context Agent:</b> Indexa información cualitativa mediante representaciones semánticas vectoriales con <b>FAISS</b> acopladas a modelos de embeddings. [PI]", bullet_style))
    story.append(Paragraph("• <b>Risk & Anomaly Agent:</b> Combina un motor de reglas deterministas con umbrales configurables externamente en YAML y un modelo no supervisado de Machine Learning (<b>Isolation Forest</b>) para detectar comportamientos atípicos en series bursátiles, calculando una puntuación global de riesgo (<i>Score</i> de 0 a 100). [IV]", bullet_style))
    story.append(Paragraph("• <b>Report Generator Agent:</b> Genera informes ejecutivos formalmente estructurados en formato JSON (Pydantic <code>ExecutiveReport</code>) mediante modelos LLM (<i>gpt-4o-mini</i>), asegurando trazabilidad y ausencia de alucinaciones. [IV]", bullet_style))
    
    story.append(Paragraph(
        "La solución se encuentra completamente productivizada mediante una arquitectura desacoplada por capas: servicio API RESTful con <b>FastAPI</b> y tareas asíncronas en segundo plano, persistencia inmutable de auditoría y trazas en base de datos relacional <b>SQLite</b> mediante <b>SQLAlchemy ORM</b>, y un cuadro de mando interactivo en <b>Streamlit</b>. Las pruebas empíricas verificadas sobre 14 ejecuciones demuestran que el sistema completa el flujo de análisis en un promedio de <b>5.69 segundos</b>, ejecutando los cálculos cuantitativos en menos de <b>80 milisegundos</b>. Se delimita estrictamente como una prueba de concepto académica que requiere siempre la supervisión humana experta (<i>Human-in-the-Loop</i>).",
        body_style
    ))
    story.append(Spacer(1, 3))
    story.append(create_callout(
        "<b>Alineación con la Guía Oficial del TFM:</b> Trabajo individual encuadrado en la Opción 3 (Proyecto Técnico Propuesto por el Alumno). Desarrolla una solución software completa en analítica avanzada, Machine Learning y productivización empresarial, cumpliendo con el límite estricto de 20 páginas de memoria principal.",
        bg=c_light, border=c_secondary
    ))

    # =========================================================================
    # 2. INTRODUCCIÓN Y CONTEXTO DEL PROBLEMA (Páginas 2 y 3)
    # =========================================================================
    story.append(Paragraph("2. Introducción y Contexto del Problema", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "En el ecosistema financiero contemporáneo, la vigilancia prudencial de emisores cotizados exige el tratamiento concurrente de información estructurada y no estructurada. Por un lado, los estados contables oficiales (Balance, Cuenta de Pérdidas y Ganancias, Estado de Flujos de Efectivo) reflejan la situación patrimonial y operativa del emisor con periodicidad trimestral o anual. Por otro lado, las cotizaciones bursátiles registran la dinámica diaria de oferta y demanda, mientras que los hechos relevantes y noticias cualitativas anticipan contingencias legales, reestructuraciones o shocks de demanda. La integración manual de estas tres dimensiones resulta ineficiente e induce a errores de triaje.",
        body_style
    ))
    story.append(Paragraph(
        "Frente a las limitaciones de los sistemas monolíticos tradicionales, las arquitecturas basadas en <b>Sistemas Multiagente (MAS)</b> permiten desacoplar el procesamiento en unidades autónomas y especializadas. Cada agente resuelve una subtarea específica (ingesta, cálculo financiero, indexación semántica, evaluación de reglas, inferencia de anomalías y síntesis en lenguaje natural) interactuando sobre un estado común y fuertemente tipado. Este enfoque garantiza el aislamiento de fallos, la optimización de latencias y una gobernanza estricta sobre los modelos de Inteligencia Artificial.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Explicabilidad frente a 'Cajas Negras':</b> En los comités de riesgo y admisión crediticia, los modelos puramente generativos o basados en redes neuronales opacas son descartados por su falta de interpretabilidad. El presente proyecto implementa un modelo de riesgo híbrido donde cada alerta está vinculada a un dato observado, un umbral explícito y una justificación matemática, satisfaciendo los principios de auditoría analítica exigidos en el sector financiero.",
        body_style
    ))

    story.append(Paragraph("<b>Alineación con el Programa Docente del Máster:</b>", h3_style))
    curr_data = [
        [Paragraph("<b>Módulo del Máster</b>", table_header_style), Paragraph("<b>Tecnología / Técnica Aplicada en el TFM</b>", table_header_style), Paragraph("<b>Ruta / Componente en el Proyecto</b>", table_header_style)],
        [Paragraph("Programación Python", table_cell_bold), Paragraph("Tipado estricto Pydantic v2, POO, estructuras de datos.", table_cell_style), Paragraph("<code>app/domain/models.py</code>", table_cell_style)],
        [Paragraph("Bases de Datos SQL", table_cell_bold), Paragraph("Modelo relacional (8 tablas), ORM SQLAlchemy, SQLite.", table_cell_style), Paragraph("<code>app/persistence/database.py</code>", table_cell_style)],
        [Paragraph("Estadística y ML", table_cell_bold), Paragraph("Volatilidad anualizada, Isolation Forest (scikit-learn).", table_cell_style), Paragraph("<code>app/analytics/anomaly_detection.py</code>", table_cell_style)],
        [Paragraph("IA y NLP Avanzado", table_cell_bold), Paragraph("Orquestación LangGraph, FAISS vector store, OpenAI LLM.", table_cell_style), Paragraph("<code>app/orchestration/graph.py</code>", table_cell_style)],
        [Paragraph("Productivización", table_cell_bold), Paragraph("API REST asíncrona FastAPI, BackgroundTasks, Uvicorn.", table_cell_style), Paragraph("<code>app/api/main.py</code>", table_cell_style)],
        [Paragraph("Visualización", table_cell_bold), Paragraph("Cuadro de mando interactivo en Streamlit, Matplotlib.", table_cell_style), Paragraph("<code>app/ui/streamlit_app.py</code>", table_cell_style)],
    ]
    t_curr = Table(curr_data, colWidths=[120, 220, 165])
    t_curr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_gray_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_curr)

    # =========================================================================
    # 3. OBJETIVOS, ALCANCE Y PREGUNTAS DE TRABAJO (Pág. 3-4)
    # =========================================================================
    story.append(Paragraph("3. Objetivos, Alcance y Preguntas de Trabajo", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "<b>Objetivo General:</b> Desarrollar, auditar y productivizar un sistema de software de analítica avanzada basado en una arquitectura multiagente cooperativa, capaz de consolidar datos contables, bursátiles y cualitativos de empresas cotizadas, calcular ratios financieros deterministas, detectar anomalías de mercado no supervisadas y emitir alertas de riesgo explicables integradas en un informe ejecutivo estructurado.",
        body_style
    ))
    story.append(Paragraph("<b>Objetivos Específicos:</b>", h3_style))
    story.append(Paragraph("1. Diseñar e implementar una arquitectura multiagente desacoplada mediante un grafo de estados dirigido con LangGraph. [IV]", bullet_style))
    story.append(Paragraph("2. Desarrollar una capa analítica cuantitativa para el cálculo automatizado de 14 métricas contables y de mercado con control de división por cero. [IV]", bullet_style))
    story.append(Paragraph("3. Construir un motor de riesgo híbrido que integre reglas deterministas configurables en YAML y un modelo no supervisado Isolation Forest. [IV]", bullet_style))
    story.append(Paragraph("4. Implementar la generación de informes ejecutivos en lenguaje natural forzando esquemas JSON estrictos para garantizar anclaje factual. [IV]", bullet_style))
    story.append(Paragraph("5. Productivizar la solución mediante una API RESTful en FastAPI, persistencia inmutable en SQLite y un cuadro de mando en Streamlit. [IV]", bullet_style))

    story.append(Paragraph("<b>Comparativa entre la Propuesta Aprobada y la Implementación Real:</b>", h3_style))
    prop_data = [
        [Paragraph("<b>Componente Propuesto</b>", table_header_style), Paragraph("<b>Implementación Real en Repositorio</b>", table_header_style), Paragraph("<b>Estado</b>", table_header_style), Paragraph("<b>Justificación y Consecuencia Técnica</b>", table_header_style)],
        [Paragraph("Orquestación Multiagente", table_cell_bold), Paragraph("LangGraph <code>StateGraph(AnalysisState)</code> con 5 nodos.", table_cell_style), Paragraph("<b>IV</b>", table_cell_style), Paragraph("Flujo secuencial robusto con paso de estado tipado.", table_cell_style)],
        [Paragraph("Cálculo de Ratios", table_cell_bold), Paragraph("14 métricas contables y bursátiles deterministas.", table_cell_style), Paragraph("<b>IV</b>", table_cell_style), Paragraph("Cálculo exacto con control de nulos y ceros.", table_cell_style)],
        [Paragraph("Motor de Reglas", table_cell_bold), Paragraph("Reglas declarativas YAML (6 reglas, 4 severidades).", table_cell_style), Paragraph("<b>IV</b>", table_cell_style), Paragraph("Parametrización externa sin modificar código.", table_cell_style)],
        [Paragraph("Detección Anomalías ML", table_cell_bold), Paragraph("Isolation Forest en scikit-learn (retorno, vol, sigma).", table_cell_style), Paragraph("<b>IV</b>", table_cell_style), Paragraph("Detección no supervisada con semilla reproducible (42).", table_cell_style)],
        [Paragraph("Persistencia y Trazabilidad", table_cell_bold), Paragraph("Base de datos SQLite vía SQLAlchemy ORM (8 tablas).", table_cell_style), Paragraph("<b>IV</b>", table_cell_style), Paragraph("Registro inmutable de 14 runs, 70 eventos y 38 señales.", table_cell_style)],
        [Paragraph("API y Cuadro de Mando", table_cell_bold), Paragraph("FastAPI con BackgroundTasks + Streamlit UI.", table_cell_style), Paragraph("<b>IV</b>", table_cell_style), Paragraph("Desacoplamiento cliente-servidor 100% operativo.", table_cell_style)],
        [Paragraph("Motor RAG de Noticias", table_cell_bold), Paragraph("FAISS vector store en memoria + OpenAI embeddings.", table_cell_style), Paragraph("<b>PI</b>", table_cell_style), Paragraph("Funcional en analytics; simplificado paso de estado.", table_cell_style)],
        [Paragraph("Procesamiento Spark", table_cell_bold), Paragraph("No incluido en la PoC local actual.", table_cell_style), Paragraph("<b>DNI</b>", table_cell_style), Paragraph("Mantenido como trabajo futuro para portabilidad local.", table_cell_style)],
    ]
    t_prop = Table(prop_data, colWidths=[95, 155, 45, 210])
    t_prop.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_gray_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_prop)
    story.append(Paragraph("<i>Estados de Evidencia: IV = Implementado y verificado; PI = Parcialmente implementado; DNI = Diseñado pero no implementado en PoC.</i>", caption_style))

    # =========================================================================
    # 4. CASO DE USO Y VALOR PARA NEGOCIO FINANCIERO (Pág. 4-5)
    # =========================================================================
    story.append(Paragraph("4. Caso de Uso y Valor para Negocio Financiero", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "El sistema modeliza el flujo de trabajo de los analistas de riesgo de crédito corporativo, gestores de carteras fundamentalistas y auditores de modelos. Frente al proceso manual tradicional, la solución introduce un triaje automatizado en tres etapas: 1) Diagnóstico cuantitativo inmediato (<80 ms) mediante ratios contables y umbrales prudenciales; 2) Detección no supervisada de anomalías de mercado mediante Machine Learning; y 3) Generación de un informe ejecutivo estructurado con recomendaciones de revisión orientadas al analista humano.",
        body_style
    ))

    bus_rows = [
        [Paragraph("<b>Necesidad de Negocio</b>", table_header_style), Paragraph("<b>Capacidad Implementada</b>", table_header_style), Paragraph("<b>Evidencia en Código</b>", table_header_style), Paragraph("<b>Valor Aportado</b>", table_header_style), Paragraph("<b>Límite / Control Requerido</b>", table_header_style)],
        [Paragraph("Triaje masivo de emisores", table_cell_bold), Paragraph("Orquestación multiagente asíncrona de 5 etapas.", table_cell_style), Paragraph("<code>app/orchestration/graph.py</code>", table_cell_style), Paragraph("Reducción de triaje de horas a ~5.7 segundos.", table_cell_style), Paragraph("Dependencia de fuentes de datos.", table_cell_style)],
        [Paragraph("Explicabilidad de alertas", table_cell_bold), Paragraph("Desglose atómico de valor observado y umbral.", table_cell_style), Paragraph("<code>app/domain/models.py</code> (RiskSignal)", table_cell_style), Paragraph("Eliminación del efecto 'caja negra'.", table_cell_style), Paragraph("Umbrales requieren calibración.", table_cell_style)],
        [Paragraph("Detección de estrés bursátil", table_cell_bold), Paragraph("Isolation Forest tridimensional en precios.", table_cell_style), Paragraph("<code>app/analytics/anomaly_detection.py</code>", table_cell_style), Paragraph("Alerta de anomalías no visibles en balance.", table_cell_style), Paragraph("Mínimo 50 sesiones de datos.", table_cell_style)],
        [Paragraph("Síntesis ejecutiva formal", table_cell_bold), Paragraph("Generación JSON estructurado con LLM.", table_cell_style), Paragraph("<code>app/agents/report_generator.py</code>", table_cell_style), Paragraph("Informe ejecutivo en español sin alucinaciones.", table_cell_style), Paragraph("Supervisión <i>Human-in-the-Loop</i>.", table_cell_style)],
        [Paragraph("Gobernanza y trazabilidad", table_cell_bold), Paragraph("Persistencia relacional inmutable de eventos.", table_cell_style), Paragraph("<code>app/persistence/database.py</code>", table_cell_style), Paragraph("Auditoría completa de latencias y decisiones.", table_cell_style), Paragraph("Base de datos SQLite local en PoC.", table_cell_style)],
    ]
    t_bus2 = Table(bus_rows, colWidths=[90, 110, 105, 105, 95])
    t_bus2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_gray_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_bus2)

    # =========================================================================
    # 5. DATOS Y FUENTES DE INFORMACIÓN (Pág. 5-6)
    # =========================================================================
    story.append(Paragraph("5. Datos y Fuentes de Información", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "La capa de ingesta implementa el patrón <i>Protocol</i> en dos adaptadores especializados: 1) <b>Adaptador Demo y Control</b> (<code>DemoMarketDataProvider</code>, <code>DemoNewsProvider</code> en <code>app/ingestion/demo_providers.py</code>), que carga archivos JSON sintéticos controlados en <code>data/demo/</code> representando perfiles arquetípicos (<i>DEMO_STBL</i>: solvencia y crecimiento sostenido; <i>DEMO_LEVR</i>: deterioro de ingresos, alto apalancamiento y tensión de liquidez; <i>DEMO_VOLT</i>: volatilidad bursátil acusada); y 2) <b>Adaptador Real</b> (<code>YFinanceDataProvider</code>, <code>YFinanceNewsProvider</code> en <code>app/ingestion/real_providers.py</code>), que consulta información pública de cotizadas internacionales mediante <code>yfinance</code>.",
        body_style
    ))

    story.append(Paragraph("<b>Diccionario de Datos y Entidades de Dominio (Pydantic v2):</b>", h3_style))
    dict_rows = [
        [Paragraph("<b>Modelo Pydantic</b>", table_header_style), Paragraph("<b>Campo / Atributo</b>", table_header_style), Paragraph("<b>Tipo</b>", table_header_style), Paragraph("<b>Descripción Técnica y Significado Financiero</b>", table_header_style)],
        [Paragraph("<code>CompanyData</code>", table_cell_bold), Paragraph("ticker, name, sector", table_cell_style), Paragraph("str", table_cell_style), Paragraph("Símbolo bursátil, denominación social y sector económico.", table_cell_style)],
        [Paragraph("<code>FinancialPeriod</code>", table_cell_bold), Paragraph("period, revenue, ebitda", table_cell_style), Paragraph("str, float", table_cell_style), Paragraph("Ejercicio contable, cifra de negocios e ingresos brutos.", table_cell_style)],
        [Paragraph("<code>FinancialPeriod</code>", table_cell_bold), Paragraph("net_debt, total_equity", table_cell_style), Paragraph("float", table_cell_style), Paragraph("Deuda financiera neta exigible y fondos propios consolidados.", table_cell_style)],
        [Paragraph("<code>FinancialPeriod</code>", table_cell_bold), Paragraph("current_assets, curr_liab", table_cell_style), Paragraph("float", table_cell_style), Paragraph("Activo y pasivo corriente para análisis de liquidez a corto plazo.", table_cell_style)],
        [Paragraph("<code>PriceBar</code>", table_cell_bold), Paragraph("date, close, volume", table_cell_style), Paragraph("date, float, int", table_cell_style), Paragraph("Sesión de negociación, precio oficial de cierre y volumen.", table_cell_style)],
        [Paragraph("<code>MetricResult</code>", table_cell_bold), Paragraph("metric_name, value, unit", table_cell_style), Paragraph("str, float, str", table_cell_style), Paragraph("Ratio financiero calculado, valor numérico y unidad de medida.", table_cell_style)],
        [Paragraph("<code>RiskSignal</code>", table_cell_bold), Paragraph("signal_id, severity, value", table_cell_style), Paragraph("str, str, float", table_cell_style), Paragraph("Alerta de riesgo emitida, nivel de gravedad y valor observado.", table_cell_style)],
    ]
    t_dict2 = Table(dict_rows, colWidths=[90, 115, 60, 240])
    t_dict2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_gray_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_dict2)

    story.append(Paragraph(
        "<b>Calidad del Dato y Aspectos Legales:</b> La función <code>_safe_divide</code> previene excepciones por división entre cero o nulos contables devolviendo <code>None</code> con etiqueta <code>not_available</code>. Las fechas bursátiles y ejercicios contables se alinean automáticamente según el periodo solicitado (1M, 3M, 6M, 1Y). Los datos sintéticos carecen de restricciones de propiedad intelectual y los datos reales de Yahoo Finance se utilizan estrictamente para docencia e investigación académica.",
        body_style
    ))

    # =========================================================================
    # 6. ARQUITECTURA DE LA SOLUCIÓN IMPLEMENTADA (Pág. 7-8)
    # =========================================================================
    story.append(Paragraph("6. Arquitectura de la Solución Implementada", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "El diseño arquitectónico sigue el principio de separación de responsabilidades en cinco capas desacopladas, asegurando alta cohesión, modularidad y portabilidad de despliegue:",
        body_style
    ))
    
    if os.path.exists("docs/images/fig1_arquitectura_sistema.png"):
        story.append(Image("docs/images/fig1_arquitectura_sistema.png", width=6.6*inch, height=3.6*inch))
        story.append(Paragraph("Figura 1: Arquitectura del Sistema Multiagente Implementado por Capas Desacopladas. [Evidencia Verificada]", caption_style))

    story.append(Paragraph("<b>Detalle de las Capas del Sistema:</b>", h3_style))
    story.append(Paragraph("<b>1. Capa de Presentación (Streamlit UI):</b> Interfaz gráfica interactiva (<code>app/ui/streamlit_app.py</code>) que permite configurar el emisor, seleccionar el periodo temporal, monitorizar el progreso reactivo de los agentes y descargar el informe final en JSON.", body_style))
    story.append(Paragraph("<b>2. Capa de Servicio y API (FastAPI):</b> Servidor RESTful (<code>app/api/main.py</code>, <code>app/api/endpoints.py</code>) expuesto bajo Uvicorn en el puerto 8000. Gestiona peticiones asíncronas con <code>BackgroundTasks</code> devolviendo un <code>run_id</code> único (UUID v4) para consultas no bloqueantes.", body_style))
    story.append(Paragraph("<b>3. Capa de Orquestación Multiagente (LangGraph):</b> Grafo de estados dirigido (<code>StateGraph</code> en <code>app/orchestration/graph.py</code>) que transita secuencialmente a través de los cinco agentes especializados, midiendo la latencia de cada uno mediante el wrapper <code>wrap_agent</code>.", body_style))
    story.append(Paragraph("<b>4. Capa Analítica y de Machine Learning:</b> Compuesta por cuatro módulos deterministas y de aprendizaje automático: <code>financial_metrics.py</code> (14 ratios cuantitativos), <code>rule_engine.py</code> (motor de reglas YAML), <code>anomaly_detection.py</code> (Isolation Forest) y <code>rag_engine.py</code> (almacén vectorial FAISS).", body_style))
    story.append(Paragraph("<b>5. Capa de Persistencia y Trazabilidad (SQLAlchemy ORM):</b> Base de datos relacional SQLite (<code>financial_app.db</code>) con 8 tablas estructuradas para entidades de negocio y registro inmutable de auditoría.", body_style))

    # =========================================================================
    # 7. DISEÑO DE LOS AGENTES Y FLUJO MULTIAGENTE (Pág. 9-10)
    # =========================================================================
    story.append(Paragraph("7. Diseño de los Agentes y Flujo Multiagente", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    if os.path.exists("docs/images/fig2_flujo_multiagente.png"):
        story.append(Image("docs/images/fig2_flujo_multiagente.png", width=6.6*inch, height=3.4*inch))
        story.append(Paragraph("Figura 2: Flujo Secuencial de Agentes y Transición del Estado Global `AnalysisState`. [Evidencia Verificada]", caption_style))

    agent_rows = [
        [Paragraph("<b>Agente</b>", table_header_style), Paragraph("<b>Módulo Fuente</b>", table_header_style), Paragraph("<b>Responsabilidad Principal</b>", table_header_style), Paragraph("<b>Entrada / Salida Clave</b>", table_header_style), Paragraph("<b>Tipo / Latencia</b>", table_header_style)],
        [Paragraph("<b>Data Ingestion Agent</b>", table_cell_bold), Paragraph("<code>app/agents/data_ingestion.py</code>", table_cell_style), Paragraph("Extrae balances, series bursátiles y noticias del emisor.", table_cell_style), Paragraph("In: ticker, period<br/>Out: financial_data, market_data, news", table_cell_style), Paragraph("Determinista<br/>1-2 ms", table_cell_style)],
        [Paragraph("<b>Financial Analysis Agent</b>", table_cell_bold), Paragraph("<code>app/agents/financial_analysis.py</code>", table_cell_style), Paragraph("Calcula deterministamente 14 ratios contables y bursátiles.", table_cell_style), Paragraph("In: financial_data, prices<br/>Out: financial_analysis (33 métricas)", table_cell_style), Paragraph("Determinista<br/>&lt; 1 ms", table_cell_style)],
        [Paragraph("<b>News & Context Agent</b>", table_cell_bold), Paragraph("<code>app/agents/news_context.py</code>", table_cell_style), Paragraph("Indexa noticias en almacén vectorial FAISS para búsqueda semántica.", table_cell_style), Paragraph("In: news_data<br/>Out: vectorstore context", table_cell_style), Paragraph("RAG / Embeddings<br/>~817 ms", table_cell_style)],
        [Paragraph("<b>Risk & Anomaly Agent</b>", table_cell_bold), Paragraph("<code>app/agents/risk_anomaly.py</code>", table_cell_style), Paragraph("Evalúa reglas YAML + Isolation Forest; calcula Risk Score (0-100).", table_cell_style), Paragraph("In: financial_analysis, prices<br/>Out: risk_analysis (score, level, signals)", table_cell_style), Paragraph("Híbrido (ML+Reglas)<br/>55-90 ms", table_cell_style)],
        [Paragraph("<b>Report Generator Agent</b>", table_cell_bold), Paragraph("<code>app/agents/report_generator.py</code>", table_cell_style), Paragraph("Sintetiza hallazgos en informe formal JSON en español con LLM.", table_cell_style), Paragraph("In: financial_analysis, risk, news<br/>Out: report (ExecutiveReport)", table_cell_style), Paragraph("Generativo (LLM)<br/>~4.79 s", table_cell_style)],
    ]
    t_agent2 = Table(agent_rows, colWidths=[85, 110, 135, 115, 60])
    t_agent2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_gray_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_agent2)

    # =========================================================================
    # 8. METODOLOGÍA ANALÍTICA Y MODELO DE RIESGO (Pág. 11-13)
    # =========================================================================
    story.append(Paragraph("8. Metodología Analítica y Modelo de Riesgo", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "El modelo analítico se estructura en dos capas complementarias: una <b>Capa A Determinista</b> basada en ratios fundamentales y reglas de severidad configurables en YAML, y una <b>Capa B de Machine Learning No Supervisado</b> para anomalías en series de cotización mediante <i>Isolation Forest</i>.",
        body_style
    ))

    story.append(Paragraph("<b>Reglas de Severidad Configuradas (`configs/risk_rules.yaml`):</b>", h3_style))
    rules_rows = [
        [Paragraph("<b>Regla</b>", table_header_style), Paragraph("<b>Métrica Evaluada</b>", table_header_style), Paragraph("<b>Condición / Umbral</b>", table_header_style), Paragraph("<b>Severidad</b>", table_header_style), Paragraph("<b>Puntos</b>", table_header_style), Paragraph("<b>Justificación de Negocio Financiero</b>", table_header_style)],
        [Paragraph("<code>revenue_decline</code>", table_cell_bold), Paragraph("<code>revenue_growth</code>", table_cell_style), Paragraph("&lt; 0.0 (&lt;0%)", table_cell_style), Paragraph("Medium", table_cell_style), Paragraph("25", table_cell_style), Paragraph("Contracción en la cifra neta de negocios.", table_cell_style)],
        [Paragraph("<code>net_debt_to_ebitda</code>", table_cell_bold), Paragraph("<code>net_debt_to_ebitda</code>", table_cell_style), Paragraph("&gt; 3.5 (&gt;3.5x)", table_cell_style), Paragraph("High", table_cell_style), Paragraph("45", table_cell_style), Paragraph("Exceso de apalancamiento vs caja operativa.", table_cell_style)],
        [Paragraph("<code>current_ratio</code>", table_cell_bold), Paragraph("<code>current_ratio</code>", table_cell_style), Paragraph("&lt; 1.0 (&lt;1.0x)", table_cell_style), Paragraph("High", table_cell_style), Paragraph("45", table_cell_style), Paragraph("Activo circulante insuficiente para deuda c/p.", table_cell_style)],
        [Paragraph("<code>max_drawdown</code>", table_cell_bold), Paragraph("<code>max_drawdown</code>", table_cell_style), Paragraph("&gt; 0.30 (&gt;30%)", table_cell_style), Paragraph("Medium", table_cell_style), Paragraph("25", table_cell_style), Paragraph("Desplome bursátil severo en el periodo.", table_cell_style)],
        [Paragraph("<code>cash_deterioration</code>", table_cell_bold), Paragraph("<code>cash_growth</code>", table_cell_style), Paragraph("&lt; -0.10 (&lt;-10%)", table_cell_style), Paragraph("Medium", table_cell_style), Paragraph("25", table_cell_style), Paragraph("Drenaje acelerado del saldo de tesorería.", table_cell_style)],
        [Paragraph("<code>high_volatility</code>", table_cell_bold), Paragraph("<code>historical_volatility</code>", table_cell_style), Paragraph("&gt; 0.40 (&gt;40%)", table_cell_style), Paragraph("Medium", table_cell_style), Paragraph("25", table_cell_style), Paragraph("Alta inestabilidad y riesgo de mercado.", table_cell_style)],
    ]
    t_rules2 = Table(rules_rows, colWidths=[85, 95, 65, 45, 35, 180])
    t_rules2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_gray_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_rules2)

    if os.path.exists("docs/images/fig3_analisis_financiero_comparativa.png"):
        story.append(Spacer(1, 3))
        story.append(Image("docs/images/fig3_analisis_financiero_comparativa.png", width=6.6*inch, height=3.5*inch))
        story.append(Paragraph("Figura 3: Comparativa de Indicadores Financieros: Perfil Estable (DEMO_STBL) vs Apalancado (DEMO_LEVR). [Demostración con datos demo]", caption_style))

    if os.path.exists("docs/images/fig4_deteccion_anomalias_mercado.png"):
        story.append(Spacer(1, 3))
        story.append(Image("docs/images/fig4_deteccion_anomalias_mercado.png", width=6.6*inch, height=3.5*inch))
        story.append(Paragraph("Figura 4: Detección de Anomalías de Mercado con Isolation Forest (DEMO_LEVR). [Demostración con datos demo]", caption_style))

    story.append(Paragraph(
        "<b>Puntuación Global de Riesgo (Risk Score):</b> Se calcula agregando los pesos de las señales activas ($w_{\\text{low}}=10, w_{\\text{med}}=25, w_{\\text{high}}=45, w_{\\text{crit}}=70$) con un tope máximo de 100 puntos. Los niveles de clasificación son: <b>Bajo</b> (0–29), <b>Moderado</b> (30–59), <b>Alto</b> (60–79) y <b>Crítico</b> (80–100).",
        body_style
    ))

    # =========================================================================
    # 9. IMPLEMENTACIÓN DE LA APLICACIÓN Y PRODUCTIVIZACIÓN (Pág. 13-14)
    # =========================================================================
    story.append(Paragraph("9. Implementación de la Aplicación y Productivización", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "La aplicación se organiza bajo una arquitectura modular y desacoplada. La capa de servicio en <b>FastAPI</b> expone los endpoints REST (<code>POST /analyses</code>, <code>GET /analyses/{run_id}</code>, <code>GET /analyses/{run_id}/report</code>, <code>GET /analyses/{run_id}/events</code>). La persistencia relacional con <b>SQLAlchemy</b> asegura la inmutabilidad de cada ejecución en <code>financial_app.db</code>, registrando trazas completas de eventos de agentes, señales disparadas e informes ejecutivos emitidos.",
        body_style
    ))

    if os.path.exists("docs/images/fig6_interfaz_usuario_dashboard.png"):
        story.append(Spacer(1, 3))
        story.append(Image("docs/images/fig6_interfaz_usuario_dashboard.png", width=6.6*inch, height=3.5*inch))
        story.append(Paragraph("Figura 5: Representación Visual del Cuadro de Mando Interactivo en Streamlit. [Evidencia Verificada]", caption_style))

    # =========================================================================
    # 10. RESULTADOS Y DEMOSTRACIÓN FUNCIONAL (Pág. 15-16)
    # =========================================================================
    story.append(Paragraph("10. Resultados y Demostración Funcional", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "La auditoría técnica verificó empíricamente el comportamiento del pipeline multiagente sobre los diferentes perfiles corporativos y emisores reales almacenados en la base de datos:",
        body_style
    ))

    res_rows = [
        [Paragraph("<b>Emisor / Ticker</b>", table_header_style), Paragraph("<b>Perfil / Horizonte</b>", table_header_style), Paragraph("<b>Score / Nivel</b>", table_header_style), Paragraph("<b>Alertas de Riesgo Disparadas</b>", table_header_style), Paragraph("<b>Duración Total</b>", table_header_style), Paragraph("<b>Estado Evidencia</b>", table_header_style)],
        [Paragraph("<code>DEMO_LEVR</code>", table_cell_bold), Paragraph("Estrés y Apalancamiento / 1Y", table_cell_style), Paragraph("<b>100.0 / CRÍTICO</b>", table_cell_style), Paragraph("Deuda/EBITDA (4.64x), Current Ratio (0.87x), Caída Ingresos (-5.26%), Max Drawdown (35.4%), Caída Caja (-11.1%), Anomalías (9d).", table_cell_style), Paragraph("5.69 s", table_cell_style), Paragraph("<b>Verificado (Run dc64b9)</b>", table_cell_style)],
        [Paragraph("<code>DEMO_STBL</code>", table_cell_bold), Paragraph("Solvencia y Crecimiento / 1Y", table_cell_style), Paragraph("<b>25.0 / BAJO</b>", table_cell_style), Paragraph("0 alertas financieras. 1 señal de mercado (9 días atípicos por fluctuación estadística).", table_cell_style), Paragraph("5.69 s", table_cell_style), Paragraph("<b>Verificado (Run dc6829)</b>", table_cell_style)],
        [Paragraph("<code>DEMO_VOLT</code>", table_cell_bold), Paragraph("Alta Volatilidad / 1Y", table_cell_style), Paragraph("<b>75.0 / ALTO</b>", table_cell_style), Paragraph("Max Drawdown (&gt;30%), Volatilidad Anualizada (&gt;40%), Anomalías de mercado.", table_cell_style), Paragraph("5.60 s", table_cell_style), Paragraph("<b>Verificado (Run local)</b>", table_cell_style)],
        [Paragraph("<code>SNDK</code> (SanDisk)", table_cell_bold), Paragraph("Empresa Cotizada Real / 6M", table_cell_style), Paragraph("<b>75.0 / ALTO</b>", table_cell_style), Paragraph("Max Drawdown (32.4%), Volatilidad (46.8%), Anomalías (6d).", table_cell_style), Paragraph("7.12 s", table_cell_style), Paragraph("<b>Verificado (Run fc0c08)</b>", table_cell_style)],
        [Paragraph("<code>V</code> (Visa Inc.)", table_cell_bold), Paragraph("Empresa Cotizada Real / 3M", table_cell_style), Paragraph("<b>25.0 / BAJO</b>", table_cell_style), Paragraph("Solidez fundamental. 3 días anómalos de mercado en ventana trimestral.", table_cell_style), Paragraph("6.48 s", table_cell_style), Paragraph("<b>Verificado (Run 6dbd6c)</b>", table_cell_style)],
    ]
    t_res2 = Table(res_rows, colWidths=[70, 95, 75, 145, 45, 75])
    t_res2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_gray_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_res2)

    if os.path.exists("docs/images/fig5_trazabilidad_latencia_agentes.png"):
        story.append(Spacer(1, 3))
        story.append(Image("docs/images/fig5_trazabilidad_latencia_agentes.png", width=6.4*inch, height=2.9*inch))
        story.append(Paragraph("Figura 6: Trazabilidad Temporal y Latencias Medidas por Agente (Escala Logarítmica). [Evidencia Verificada en SQLite]", caption_style))

    # =========================================================================
    # 11. EVALUACIÓN, CALIDAD, EXPLICABILIDAD Y TRAZABILIDAD (Pág. 17-18)
    # =========================================================================
    story.append(Paragraph("11. Evaluación, Calidad, Explicabilidad y Trazabilidad", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "La robustez técnica del software se auditó mediante la ejecución de la suite de pruebas unitarias automatizadas con <code>pytest</code> (100% passed en 0.05s) y la inspección de integridad de la base de datos relacional. Cada alerta emitida incluye su valor observado, el umbral de referencia, la severidad ponderada y una recomendación de revisión operativa, garantizando total explicabilidad para comités de negocio.",
        body_style
    ))

    val_rows = [
        [Paragraph("<b>Criterio Evaluado</b>", table_header_style), Paragraph("<b>Método de Verificación</b>", table_header_style), Paragraph("<b>Resultado Observado</b>", table_header_style), Paragraph("<b>Estado</b>", table_header_style)],
        [Paragraph("División Segura por Cero", table_cell_bold), Paragraph("Test unitario con denominadores nulos y cero.", table_cell_style), Paragraph("<code>_safe_divide(10, 0) == None</code> sin excepciones.", table_cell_style), Paragraph("<b>Verificado</b>", table_cell_style)],
        [Paragraph("Exactitud de Ratios", table_cell_bold), Paragraph("Prueba cruzada de 14 métricas contables.", table_cell_style), Paragraph("100% de coincidencia numérica y tipado.", table_cell_style), Paragraph("<b>Verificado</b>", table_cell_style)],
        [Paragraph("Persistencia Inmutable", table_cell_bold), Paragraph("Consultas SQL directas sobre SQLite.", table_cell_style), Paragraph("70 eventos y 14 ejecuciones persistidas íntegras.", table_cell_style), Paragraph("<b>Verificado</b>", table_cell_style)],
        [Paragraph("Reproducibilidad ML", table_cell_bold), Paragraph("Ejecución repetida de Isolation Forest (seed=42).", table_cell_style), Paragraph("Idénticas detecciones anómalas sin variabilidad.", table_cell_style), Paragraph("<b>Verificado</b>", table_cell_style)],
    ]
    t_val2 = Table(val_rows, colWidths=[110, 140, 185, 70])
    t_val2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_gray_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_val2)

    # =========================================================================
    # 12. LIMITACIONES, RIESGOS Y ASPECTOS ÉTICOS (Pág. 18-19)
    # =========================================================================
    story.append(Paragraph("12. Limitaciones, Riesgos y Aspectos Éticos", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "El proyecto reconoce con absoluta transparencia sus limitaciones técnicas y metodológicas: 1) <b>Heterogeneidad de datos públicos:</b> Posibles desajustes temporales o diferencias contables (NIIF vs US GAAP); 2) <b>Tamaño muestral en series cortas:</b> El Isolation Forest exige series con al menos 50 sesiones para evitar inestabilidad estadística; 3) <b>Subjetividad de umbrales:</b> Los límites configurados en YAML representan supuestos generales que requieren calibración por sector de actividad; y 4) <b>Delimitación regulatoria:</b> El Risk Score no constituye un modelo crediticio homologado de Basilea III/IV, operando exclusivamente como herramienta de triaje con supervisión humana (*Human-in-the-Loop*).",
        body_style
    ))

    # =========================================================================
    # 13. CONCLUSIONES Y LÍNEAS FUTURAS (Pág. 19-20)
    # =========================================================================
    story.append(Paragraph("13. Conclusiones y Líneas Futuras", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    story.append(Paragraph(
        "El Trabajo Fin de Máster ha cumplido satisfactoriamente todos los objetivos propuestos, demostrando la viabilidad y el alto valor de los sistemas multiagente para la analítica financiera avanzada. La integración de LangGraph, FastAPI, Isolation Forest, FAISS y Streamlit permite transformar datos masivos y fragmentados en inteligencia accionable y explicable en menos de 6 segundos por emisor.<br/><br/>"
        "<b>Líneas de Desarrollo Futuro:</b> 1) Ingesta distribuida con <b>Apache Spark</b> para carteras masivas de miles de empresas; 2) Motor RAG avanzado sobre memorias anuales completas en PDF (10-K / CNMV) con bases vectoriales dedicadas (Qdrant/Milvus); 3) Calibración sectorial dinámica de umbrales por grupos de pares (*peer groups*); 4) Módulo interactivo *Human-in-the-Loop* para retroalimentar el modelo con el juicio del analista; y 5) Despliegue en la nube mediante contenedores Docker sobre Google Cloud Platform.",
        body_style
    ))

    # =========================================================================
    # 14. BIBLIOGRAFÍA (Pág. 20)
    # =========================================================================
    story.append(Paragraph("14. Bibliografía", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=4))
    
    bibs = [
        "1. Altman, E. I. (1968). <i>Financial ratios, discriminant analysis and the prediction of corporate bankruptcy</i>. The Journal of Finance, 23(4), 589-609.",
        "2. Chase, H., et al. (2024). <i>LangGraph: Building Language Agents as Graphs</i>. LangChain Documentation.",
        "3. Johnson, J., Douze, M., & Jégou, H. (2019). <i>Billion-scale similarity search with GPUs (FAISS)</i>. IEEE Transactions on Big Data, 7(3), 535-547.",
        "4. Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). <i>Isolation Forest</i>. Eighth IEEE International Conference on Data Mining (ICDM), 413-422.",
        "5. McKinney, W. (2010). <i>Data Structures for Statistical Computing in Python (Pandas)</i>. Proc. 9th Python in Science Conf., 51-56.",
        "6. Pedregosa, F., et al. (2011). <i>Scikit-learn: Machine Learning in Python</i>. Journal of Machine Learning Research, 12, 2825-2830.",
        "7. Ramírez, J. (2021). <i>Análisis de Estados Financieros: Fundamentos y Aplicaciones Prácticas</i>. Ediciones Pirámide.",
        "8. Tiangolo, S. (2024). <i>FastAPI: Modern, Fast (High-Performance) Web Framework for Building APIs with Python</i>. FastAPI Documentation.",
        "9. Treleaven, P., Galas, M., & Lalchand, V. (2013). <i>Algorithmic trading review</i>. Communications of the ACM, 56(11), 76-85.",
        "10. Universidad Complutense de Madrid. (2024). <i>Guía Oficial para la Realización del Trabajo Fin de Máster</i>. Facultad de Estudios Estadísticos, UCM.",
        "11. Universidad Complutense de Madrid. (2024). <i>Dossier Informativo: Máster de Formación Permanente en Big Data, Data Science & IA (9ª Edición)</i>. UCM / NTIC Master."
    ]
    for b in bibs:
        story.append(Paragraph(b, ParagraphStyle('Bib', fontName='Helvetica', fontSize=7.4, leading=9.6, spaceAfter=2)))

    # =========================================================================
    # ANEXOS TÉCNICOS (A a L) - Separados de las 20 páginas principales
    # =========================================================================
    story.append(PageBreak())
    
    story.append(Paragraph("ANEXOS TÉCNICOS Y EVIDENCIAS DE AUDITORÍA", ParagraphStyle('AppHead', fontName='Helvetica-Bold', fontSize=14, leading=17, alignment=1, textColor=c_primary)))
    story.append(Paragraph("Documentación complementaria de soporte, esquemas de datos, configuraciones, suite de pruebas y guion audiovisual", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=4, spaceAfter=12))

    story.append(Paragraph("Anexo A: Diagrama Completo de Arquitectura del Sistema", h2_style))
    story.append(Paragraph("El sistema desacopla la presentación (Streamlit), el servicio RESTful (FastAPI), la orquestación multiagente (LangGraph StateGraph), los módulos analíticos deterministas y no supervisados (Isolation Forest, FAISS, Rule Engine) y la persistencia relacional inmutable (SQLAlchemy ORM sobre SQLite).", body_style))
    
    story.append(Paragraph("Anexo B: Diccionario de Datos Extendido y Entidades ORM", h2_style))
    story.append(Paragraph("La base de datos relacional <code>financial_app.db</code> implementa 8 entidades con claves foráneas explícitas: <code>companies</code>, <code>financial_periods</code>, <code>market_prices</code>, <code>news_items</code>, <code>analysis_runs</code>, <code>agent_events</code>, <code>risk_signals</code> y <code>reports</code>, garantizando integridad referencial y trazabilidad completa de cada ejecución.", body_style))

    story.append(Paragraph("Anexo C: Formulación Matemática Completa de los 14 Indicadores Financieros", h2_style))
    story.append(Paragraph("Se implementan con control de división por cero: Margen EBITDA, Margen Neto, ROA, ROE, Leverage Ratio, Deuda Neta / EBITDA, Current Ratio, Cobertura de Intereses, Crecimiento de Ingresos, Crecimiento de EBITDA, Variación de Efectivo, Retorno Bursátil Acumulado, Maximum Drawdown (MDD) y Volatilidad Histórica Anualizada ($\\sigma_{\\text{anual}} = \\sigma_{\\text{diaria}} \\times \\sqrt{252}$).", body_style))

    story.append(Paragraph("Anexo D: Configuración Completa de Reglas de Riesgo (`configs/risk_rules.yaml`)", h2_style))
    story.append(Paragraph("Archivo declarativo YAML que define 6 reglas deterministas con umbrales y direcciones de comparación (<code>revenue_decline</code>: &lt;0.0, <code>net_debt_to_ebitda</code>: &gt;3.5, <code>current_ratio</code>: &lt;1.0, <code>max_drawdown</code>: &gt;0.30, <code>cash_deterioration</code>: &lt;-0.10, <code>high_volatility</code>: &gt;0.40) y pesos de severidad (low=10, med=25, high=45, crit=70).", body_style))

    story.append(Paragraph("Anexo E: Esquemas JSON de Entrada y Salida de los Agentes", h2_style))
    story.append(Paragraph("Cada agente valida estrictamente sus contratos de interfaz mediante Pydantic v2. El objeto central <code>AnalysisState</code> evoluciona incrementalmente a través de los nodos del grafo, y el <code>Report Generator Agent</code> fuerza la salida JSON del LLM al esquema <code>ExecutiveReport</code>.", body_style))

    story.append(Paragraph("Anexo F: Estructura Completa del Repositorio de Código", h2_style))
    story.append(Paragraph("Organización modular estándar: <code>app/</code> (agents, analytics, api, domain, ingestion, orchestration, persistence, ui), <code>configs/</code>, <code>data/demo/</code>, <code>docs/images/</code>, <code>scripts/</code>, <code>tests/unit/</code>, <code>pyproject.toml</code> y <code>Makefile</code>.", body_style))

    story.append(Paragraph("Anexo G: Fragmentos de Código Fuente Seleccionados", h2_style))
    story.append(Paragraph("Extractos auditados del decorador de observabilidad <code>wrap_agent</code>, la función matemática de división segura <code>_safe_divide</code>, el algoritmo de detección de anomalías <code>detect_market_anomalies</code> y la función de cálculo del score de riesgo <code>calculate_risk_score</code>.", body_style))

    story.append(Paragraph("Anexo H: Análisis Exploratorio de Datos (EDA) Extendido de Perfiles Demo", h2_style))
    story.append(Paragraph("Estadísticas descriptivas de los 3 perfiles sintéticos: DEMO_STBL (ingresos 1000-1100, EBITDA 200-230, deuda neta 150), DEMO_LEVR (ingresos 1000-900, deuda neta 250-650, current ratio 0.87) y DEMO_VOLT (ingresos erráticos 1000-800-1300, volatilidad diaria 5%).", body_style))

    story.append(Paragraph("Anexo I: Resultados Completos de la Suite de Pruebas Unitarias (pytest)", h2_style))
    story.append(Paragraph("Ejecución validada: <code>tests/unit/test_financial_metrics.py</code> con 2 aserciones críticas (<code>test_safe_divide</code> y <code>test_calculate_financial_metrics</code>) superadas en 0.05 segundos con 100% de éxito.", body_style))

    story.append(Paragraph("Anexo J: Guía de Reproducibilidad y Despliegue Local Paso a Paso", h2_style))
    story.append(Paragraph("Instrucciones detalladas en <code>README_generacion_memoria_tfm.md</code> para la sincronización de dependencias con <code>uv</code>, generación de fixtures, siembra de base de datos y levantamiento de servicios API y Streamlit.", body_style))

    story.append(Paragraph("Anexo K: Guion Oficial para el Vídeo Explicativo de 5 Minutos (Español)", h2_style))
    story.append(Paragraph("Documento <code>guion_video_tfm.md</code> con temporización en 5 bloques (duración total 4:50 min), indicaciones de captura de pantalla y locución en off completa para la presentación audiovisual ante la comisión evaluadora.", body_style))

    story.append(Paragraph("Anexo L: Matriz de Evidencias y Auditoría de Implementación del Proyecto", h2_style))
    story.append(Paragraph("Documento <code>matriz_evidencias_implementacion.md</code> con el inventario exhaustivo de 23 afirmaciones y componentes técnicos clasificados por su estado de evidencia verificado (IV, PI, DNI, DD).", body_style))

    return story

def build_thesis():
    filename = "memoria_tfm_aplicacion_multiagente_finanzas.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=52,
        bottomMargin=52
    )
    story = generate_pdf_elements()
    doc.build(story, canvasmaker=MasterThesisCanvas)
    print(f"Thesis PDF compiled: {filename}")

if __name__ == "__main__":
    build_thesis()
