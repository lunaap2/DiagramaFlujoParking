import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import base64
from io import BytesIO
import numpy as np


class GeneradorDiagramaParqueadero:
    def __init__(self, titulo="Sistema de Parqueadero - Diagrama de Flujo"):
        self.titulo = titulo
        self.secciones = []
        self.fig_width = 22
        self.fig_height = 130
        self.y_step = 7  # Mayor espaciado vertical entre bloques
        self.current_y = 125  # Posición Y inicial

    def crear_rectangulo(self, ax, x, y, w, h, texto, color='lightgreen', fontsize=10, fontweight='bold'):
        """Crea un rectángulo con texto centrado (auto-wrap) mejorado"""
        # Sombra
        shadow = patches.Rectangle((x + 0.15, y - 0.15), w, h, 
                                 facecolor='gray', alpha=0.3, zorder=1)
        ax.add_patch(shadow)
        
        # Rectángulo principal
        rect = patches.Rectangle((x, y), w, h, facecolor=color, 
                               edgecolor='black', lw=2.5, zorder=2)
        ax.add_patch(rect)

        # Ajustar salto de línea con mejor control
        max_chars_per_line = 20 if w < 6 else 25
        if len(texto) > max_chars_per_line:
            lineas = []
            linea_actual = ""
            for palabra in texto.split():
                if len(linea_actual + palabra) <= max_chars_per_line:
                    linea_actual += palabra + " "
                else:
                    lineas.append(linea_actual.strip())
                    linea_actual = palabra + " "
            if linea_actual.strip():
                lineas.append(linea_actual.strip())
            texto = '\n'.join(lineas)

        # Texto con mejor formato
        ax.text(x + w / 2, y + h / 2, texto, ha='center', va='center',
                fontsize=fontsize, fontweight=fontweight, linespacing=1.4, 
                zorder=3, color='black')
        
        # Devolver puntos de conexión exactos
        return {
            'top': (x + w / 2, y + h),
            'bottom': (x + w / 2, y),
            'left': (x, y + h / 2),
            'right': (x + w, y + h / 2)
        }

    def crear_rombo(self, ax, x, y, w, h, texto, color='lightblue', fontsize=9, fontweight='bold'):
        """Crea un rombo (decisión) con texto centrado mejorado"""
        # Sombra del rombo
        shadow_vertices = [(x + w / 2 + 0.15, y - 0.15), 
                          (x + w + 0.15, y + h / 2 - 0.15), 
                          (x + w / 2 + 0.15, y + h - 0.15), 
                          (x + 0.15, y + h / 2 - 0.15)]
        shadow_codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
        shadow_rombo = patches.PathPatch(Path(shadow_vertices + [(0, 0)], shadow_codes),
                                        facecolor='gray', alpha=0.3, zorder=1)
        ax.add_patch(shadow_rombo)
        
        # Rombo principal
        vertices = [(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h), (x, y + h / 2)]
        codigos = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
        rombo = patches.PathPatch(Path(vertices + [(0, 0)], codigos),
                                 facecolor=color, edgecolor='black', lw=2.5, zorder=2)
        ax.add_patch(rombo)

        # Ajustar texto para rombo
        max_chars = 16
        if len(texto) > max_chars:
            palabras = texto.split()
            lineas = []
            linea = ""
            for p in palabras:
                if len(linea + p) < 12:
                    linea += p + " "
                else:
                    lineas.append(linea.strip())
                    linea = p + " "
            if linea.strip():
                lineas.append(linea.strip())
            texto = '\n'.join(lineas)

        ax.text(x + w / 2, y + h / 2, texto, ha='center', va='center',
                fontsize=fontsize, fontweight=fontweight, zorder=3, color='black')
        
        # Devolver puntos de conexión exactos del rombo
        return {
            'top': (x + w / 2, y + h),
            'bottom': (x + w / 2, y),
            'left': (x, y + h / 2),
            'right': (x + w, y + h / 2),
            'center': (x + w / 2, y + h / 2)
        }

    def crear_flecha_perfecta(self, ax, x1, y1, x2, y2, etiqueta=None, color='black', lw=2):
        """Crea una flecha que toca exactamente las figuras sin espacios"""
        dx, dy = x2 - x1, y2 - y1
        
        # No reducir la longitud - la flecha debe tocar exactamente
        ax.arrow(x1, y1, dx, dy, head_width=0.35, head_length=0.35,
                fc=color, ec=color, lw=lw, length_includes_head=True, zorder=4)
        
        if etiqueta:
            # Calcular posición de etiqueta
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            offset_y = 0.7 if dx == 0 else 0.5
            
            ax.text(mid_x, mid_y + offset_y, etiqueta,
                    ha='center', va='bottom', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", 
                             edgecolor="gray", alpha=0.95), zorder=5)

    def crear_flecha_horizontal_perfecta(self, ax, x1, y1, x2, y2, etiqueta=None, color='black'):
        """Crea flecha horizontal perfectamente alineada"""
        # Asegurar que y1 y y2 sean exactamente iguales para alineación perfecta
        y_aligned = y1
        self.crear_flecha_perfecta(ax, x1, y_aligned, x2, y_aligned, etiqueta=etiqueta, color=color)

    def crear_flecha_horizontal_con_punta_izquierda(self, ax, x1, y1, x2, y2, color='purple', lw=2):
        """Crea una flecha horizontal con punta apuntando hacia la izquierda"""
        # Crear la línea horizontal
        ax.plot([x1, x2], [y1, y2], color=color, lw=lw, zorder=4)
        
        # Crear la punta de flecha apuntando hacia la izquierda
        # La punta se coloca en x1 (punto izquierdo)
        ax.arrow(x1 + 0.4, y1, -0.4, 0, head_width=0.3, head_length=0.3,
                fc=color, ec=color, lw=lw, length_includes_head=True, zorder=5)

    def avanzar_y(self, pasos=1):
        """Avanza la posición Y actual"""
        self.current_y -= self.y_step * pasos
        return self.current_y

    def resetear_y(self, valor):
        """Restablece Y a un valor específico"""
        self.current_y = valor
        return self.current_y

    def crear_diagrama_completo(self):
        """Crea el diagrama completo del sistema de parqueadero con flechas perfectamente ajustadas"""
        fig, ax = plt.subplots(figsize=(self.fig_width, self.fig_height))
        ax.set_xlim(0, 22)
        ax.set_ylim(0, 130)
        ax.axis('off')

        # Título del diagrama con mejor diseño
        title_box = patches.FancyBboxPatch((2, 126), 18, 4, 
                                         boxstyle="round,pad=0.5",
                                         facecolor="#E6B3FF", 
                                         edgecolor="#C8A8E9", 
                                         linewidth=3,
                                         zorder=2)
        ax.add_patch(title_box)
        
        ax.text(11, 128, 'DIAGRAMA DE FLUJO\nSISTEMA DE PARQUEADERO', 
                ha='center', va='center', fontsize=18, fontweight='bold', 
                color='black', zorder=3)

        # === 1. INICIO ===
        y = self.avanzar_y(0.5)
        inicio_pts = self.crear_rectangulo(ax, 8, y, 6, 2.5, 'INICIO', 'lightcoral', 12, 'bold')
        
        # === 2. Inicializar matriz ===
        y = self.avanzar_y(1.2)
        init_pts = self.crear_rectangulo(ax, 7, y, 8, 2.5, 'Inicializar matriz\nb = zeros((8,5))', 'lightgreen', 11)
        # Flecha perfecta desde inicio hasta inicializar
        self.crear_flecha_perfecta(ax, inicio_pts['bottom'][0], inicio_pts['bottom'][1], 
                                  init_pts['top'][0], init_pts['top'][1])
        
        # === 3. entrada = 0 ===
        y = self.avanzar_y(1.2)
        entrada_pts = self.crear_rectangulo(ax, 8.5, y, 5, 2.5, 'entrada = 0', 'wheat', 11)
        # Flecha perfecta
        self.crear_flecha_perfecta(ax, init_pts['bottom'][0], init_pts['bottom'][1], 
                                  entrada_pts['top'][0], entrada_pts['top'][1])

        # === 4. Bucle principal ===
        y = self.avanzar_y(1.2)
        bucle_y = y
        bucle_pts = self.crear_rombo(ax, 7, y, 8, 4, "entrada != 's'", 'lightblue', 11)
        # Flecha perfecta
        self.crear_flecha_perfecta(ax, entrada_pts['bottom'][0], entrada_pts['bottom'][1], 
                                  bucle_pts['top'][0], bucle_pts['top'][1])
        
        # Flecha NO → Salir (perfectamente alineada)
        salir_y = y + 0.5
        salir_pts = self.crear_rectangulo(ax, 17, salir_y, 4, 3, 'Salir del\nprograma', 'lightcoral', 11)
        self.crear_flecha_horizontal_perfecta(ax, bucle_pts['right'][0], bucle_pts['right'][1], 
                                            salir_pts['left'][0], salir_pts['left'][1])
        ax.text(15.5, bucle_pts['right'][1] + 0.5, 'NO', ha='center', va='center', fontsize=10, 
                fontweight='bold', color='red',
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.9))
        
        # === 5. Mostrar menú ===
        y = self.avanzar_y(1.8)
        menu_texto = ("MENÚ DE OPCIONES:\n"
                      "1. Visualización    2. Aparcar\n"
                      "3. Sacar coche     4. Plantas libres\n"
                      "5. Planta más vacía  6. Total coches\n"
                      "7. Mantenimiento   8. Porcentaje ocupación\n"
                      "9. No reservadas   s. Salir")
        menu_pts = self.crear_rectangulo(ax, 4, y, 14, 6, menu_texto, 'lightyellow', 10)
        # Flecha SÍ perfecta
        self.crear_flecha_perfecta(ax, bucle_pts['bottom'][0], bucle_pts['bottom'][1], 
                                  menu_pts['top'][0], menu_pts['top'][1])
        ax.text(bucle_pts['bottom'][0] + 0.8, bucle_pts['bottom'][1] - 1, 'SÍ', ha='center', va='center', 
                fontsize=10, fontweight='bold', color='green',
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.9))

        # === 6. Leer opción ===
        y = self.avanzar_y(2.5)
        leer_pts = self.crear_rectangulo(ax, 7, y, 8, 2.5, 'Leer opción (entrada)', 'lightgreen', 11)
        self.crear_flecha_perfecta(ax, menu_pts['bottom'][0], menu_pts['bottom'][1], 
                                  leer_pts['top'][0], leer_pts['top'][1])

        # === 7. SWITCH DE OPCIONES (LIMPIO Y SIN FLECHAS EXTRA) ===
        y = self.avanzar_y(1.5)
        opciones_y = y
        x_decision = 1.5
        x_accion = 10
        w_decision, h_decision = 6, 3.5
        gap = 6.5

        opciones = [
            ("entrada == '1'", 'Mostrar estado de cada planta'),
            ("entrada == '2'", 'Aparcar: validar planta y espacio'),
            ("entrada == '3'", 'Sacar coche: liberar primer espacio'),
            ("entrada == '4'", 'Mostrar plantas con espacios libres'),
            ("entrada == '5'", 'Identificar planta más vacía'),
            ("entrada == '6'", 'Calcular total de coches: np.sum(b)'),
            ("entrada == '7'", 'Mantenimiento: redistribuir vehículos'),
            ("entrada == '8'", 'Calcular porcentaje por planta'),
            ("entrada == '9'", 'Contar coches en plantas\nno reservadas [2, 3, 5, 7]')
        ]

        # Conexión desde leer opción hasta la primera decisión (sin flecha extra)
        primera_decision_y = opciones_y + h_decision/2
        self.crear_flecha_perfecta(ax, leer_pts['bottom'][0], leer_pts['bottom'][1], 
                                  leer_pts['bottom'][0], primera_decision_y + 2)
        

        # Línea lateral para retorno (CON flechas apuntando hacia la izquierda)
        return_x = 0.3
        return_points = []
        
        for i, (condicion, accion) in enumerate(opciones):
            y_actual = opciones_y - i * gap
            
            # Rombo de decisión
            rombo_pts = self.crear_rombo(ax, x_decision, y_actual, w_decision, h_decision, condicion, 'lightblue', 9)
            
            # SOLO una flecha SÍ hacia la acción
            w_accion = 8 if i != 8 else 9
            accion_pts = self.crear_rectangulo(ax, x_accion, y_actual - 0.5, w_accion, 4, accion, 'lightgreen', 10)
            self.crear_flecha_horizontal_perfecta(ax, rombo_pts['right'][0], rombo_pts['right'][1], 
                                                accion_pts['left'][0], accion_pts['left'][1])
            
            # Etiqueta "SÍ"
            mid_x_si = (rombo_pts['right'][0] + accion_pts['left'][0]) / 2
            ax.text(mid_x_si, rombo_pts['right'][1] + 0.5, 'SÍ', 
                    ha='center', va='center', fontsize=9, fontweight='bold', color='green',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.9))
            
            # Línea de retorno horizontal CON FLECHA APUNTANDO HACIA LA IZQUIERDA
            return_y = rombo_pts['center'][1]
            return_points.append((return_x, return_y))
            
            # Línea horizontal de retorno con flecha hacia la izquierda
            self.crear_flecha_horizontal_con_punta_izquierda(ax, return_x, return_y, rombo_pts['left'][0], return_y)

        # === 8. Retorno simple y limpio ===
        y_return_bottom = opciones_y - 8 * gap - 3
        
        # UNA SOLA línea vertical de retorno
        ax.plot([return_x, return_x], [return_points[0][1], y_return_bottom], 
               color='purple', lw=2, zorder=4)
        
        # Línea de retorno al bucle principal
        ax.plot([return_x, return_x], [y_return_bottom, bucle_pts['left'][1]], 
               color='purple', lw=2, zorder=4)
        
        # Flecha final hacia el bucle
        self.crear_flecha_horizontal_perfecta(ax, return_x, bucle_pts['left'][1], 
                                            bucle_pts['left'][0], bucle_pts['left'][1], color='purple')

        # Etiqueta de retorno
        ax.text(return_x, (y_return_bottom + bucle_pts['left'][1]) / 2, '← Retorno\nal menú', 
                ha='center', va='center', fontsize=10, fontweight='bold', 
                color='purple', rotation=90,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lavender", alpha=0.9))

        plt.tight_layout()
        return fig

    def fig_to_base64(self, fig):
        buffer = BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight", dpi=300)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_base64}" class="grafico" style="border-radius: 12px;">'

    def agregar_seccion(self, titulo, contenido_html):
        self.secciones.append(f"<h2>{titulo}</h2>\n{contenido_html}")

    def exportar_html(self, filename="diagrama_flujo_parqueadero_con_flechas_moradas.html"):
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.titulo}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                body {{
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                    line-height: 1.7;
                }}
                .container {{
                    max-width: 1400px;
                    margin: 20px auto;
                    padding: 30px;
                }}
                h1 {{
                    text-align: center;
                    color: white;
                    font-weight: 700;
                    font-size: 2.5em;
                    text-shadow: 3px 3px 8px rgba(0,0,0,0.6);
                    margin-bottom: 15px;
                    padding: 25px;
                    border-radius: 20px;
                    background: rgba(0,0,0,0.4);
                    backdrop-filter: blur(15px);
                }}
                h2 {{
                    color: #fff;
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    padding: 15px 25px;
                    border-radius: 15px;
                    margin: 35px 0 20px;
                    box-shadow: 0 6px 15px rgba(0,0,0,0.2);
                    font-weight: 600;
                    font-size: 1.4em;
                }}
                .grafico {{
                    display: block;
                    margin: 25px auto;
                    max-width: 100%;
                    border: 5px solid #2c3e50;
                    border-radius: 20px;
                    box-shadow: 0 15px 40px rgba(0,0,0,0.4);
                    transition: transform 0.3s ease;
                }}
                .grafico:hover {{
                    transform: scale(1.02);
                }}
                .download-button {{
                    display: inline-block;
                    margin: 20px auto;
                    padding: 12px 24px;
                    background: linear-gradient(135deg, #28a745, #20c997);
                    color: white;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: 600;
                    font-size: 1.1em;
                    box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
                    transition: all 0.3s ease;
                    border: none;
                    cursor: pointer;
                }}
                .download-button:hover {{
                    background: linear-gradient(135deg, #34ce57, #17a2b8);
                    box-shadow: 0 8px 25px rgba(40, 167, 69, 0.6);
                    transform: translateY(-2px);
                }}
                .download-container {{
                    text-align: center;
                    margin: 20px 0;
                    padding: 20px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                }}
                .seccion {{
                    background: rgba(255, 255, 255, 0.96);
                    padding: 30px;
                    margin: 25px auto;
                    border-radius: 25px;
                    box-shadow: 0 12px 35px rgba(0,0,0,0.25);
                    backdrop-filter: blur(15px);
                    border: 1px solid rgba(255,255,255,0.2);
                }}
                .descripcion {{
                    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                    padding: 25px;
                    border-radius: 18px;
                    border-left: 8px solid #3498db;
                    margin: 20px 0;
                    font-size: 1.05em;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                ul, ol {{
                    padding-left: 25px;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                .leyenda {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                    font-size: 1em;
                }}
                .item {{
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 8px;
                    border-radius: 8px;
                    background: rgba(0,0,0,0.03);
                }}
                .color-box {{
                    width: 20px;
                    height: 20px;
                    border: 2px solid #333;
                    border-radius: 4px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }}
                footer {{
                    text-align: center;
                    margin-top: 50px;
                    color: white;
                    font-size: 1em;
                    opacity: 0.9;
                    background: rgba(0,0,0,0.3);
                    padding: 20px;
                    border-radius: 15px;
                }}
            </style>
            <script>
                function descargarDiagrama() {{
                    const img = document.querySelector('.grafico');
                    const link = document.createElement('a');
                    link.href = img.src;
                    link.download = 'diagrama_sistema_parqueadero.png';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    // Mostrar mensaje de confirmación
                    const button = document.querySelector('.download-button');
                    const originalText = button.textContent;
                    button.textContent = '✓ Descarga iniciada';
                    button.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
                    
                    setTimeout(() => {{
                        button.textContent = originalText;
                        button.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
                    }}, 2000);
                }}
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🚗 {self.titulo} - Con Flechas Moradas Mejoradas</h1>
                
                <div class="download-container">
                    <button class="download-button" onclick="descargarDiagrama()">
                        📥 Descargar Diagrama PNG
                    </button>
                    <p style="color: white; margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                        Haz clic para descargar el diagrama en alta resolución
                    </p>
                </div>
                
                {"".join([f'<div class="seccion">{sec}</div>' for sec in self.secciones])}
                <footer>
                    &copy; {self.titulo} - Flechas Moradas con Punta hacia la Izquierda<br>
                    Generado con Python + Matplotlib
                </footer>
            </div>
        </body>
        </html>
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Diagrama con flechas moradas mejoradas generado: {filename}")


# ====== EJECUCIÓN ======
if __name__ == "__main__":
    generador = GeneradorDiagramaParqueadero("Sistema de Gestión de Parqueadero")

    print("🚀 Generando diagrama con flechas moradas con punta hacia la izquierda...")
    figura = generador.crear_diagrama_completo()
    img_html = generador.fig_to_base64(figura)

    # Descripción de mejoras
    mejoras = """
    <div class="descripcion">
        <h3>✨ Mejoras en las Flechas Moradas y Funcionalidad</h3>
        <ul>
            <li><strong>🏹 Punta de Flecha:</strong> Las flechas moradas ahora tienen una punta que apunta hacia la izquierda.</li>
            <li><strong>🎯 Dirección Clara:</strong> Indica visualmente la dirección del flujo de retorno desde los rombos hacia la línea lateral.</li>
            <li><strong>📏 Posicionamiento Preciso:</strong> La punta se posiciona correctamente en el extremo izquierdo de cada línea horizontal.</li>
            <li><strong>🔄 Consistencia Visual:</strong> Mantiene el color morado y el grosor consistente con el resto del sistema de retorno.</li>
            <li><strong>🎨 Claridad de Flujo:</strong> Mejora la comprensión del diagrama mostrando claramente la dirección del retorno al menú.</li>
            <li><strong>📥 Descarga PNG:</strong> Botón interactivo para descargar el diagrama en formato PNG de alta resolución.</li>
        </ul>
    </div>
    """

    # Descripción técnica
    descripcion_tecnica = """
    <div class="descripcion">
        <h3>🔧 Implementación Técnica</h3>
        <ul>
            <li><strong>Nueva Función:</strong> <code>crear_flecha_horizontal_con_punta_izquierda()</code> para flechas moradas</li>
            <li><strong>Metodología:</strong> Primero dibuja la línea horizontal, luego añade la punta de flecha en el extremo izquierdo</li>
            <li><strong>Parámetros de la Punta:</strong> head_width=0.3, head_length=0.3 para proporción adecuada</li>
            <li><strong>Posicionamiento:</strong> La punta se dibuja con un pequeño offset (0.4) desde el punto izquierdo</li>
            <li><strong>Integración:</strong> Se mantiene la funcionalidad existente agregando solo la mejora visual</li>
            <li><strong>Función de Descarga:</strong> JavaScript que convierte la imagen base64 en un enlace descargable</li>
            <li><strong>UX del Botón:</strong> Feedback visual que confirma la descarga con animación y cambio de texto temporal</li>
        </ul>
    </div>
    """

    # Agregar secciones
    generador.agregar_seccion("📋 Diagrama de Flujo con Flechas Mejoradas", img_html)
    generador.agregar_seccion("✅ Mejoras Implementadas", mejoras)
    generador.agregar_seccion("⚙️ Detalles Técnicos", descripcion_tecnica)

    # Exportar
    generador.exportar_html("diagrama_flujo_parqueadero_con_flechas_moradas.html")
    print("🎉 ¡Diagrama con flechas moradas mejoradas completado!")
    print("📄 Archivo generado: diagrama_flujo_parqueadero_con_flechas_moradas.html")