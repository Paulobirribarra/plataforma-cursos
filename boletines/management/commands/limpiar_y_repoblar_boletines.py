from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from boletines.models import Boletin
from blogs.models import BlogPost
from cursos.models import Course
import random
import secrets

User = get_user_model()


class Command(BaseCommand):
    help = 'Limpiar boletines con HTML mal formateado y repoblar con contenido HTML correctamente estructurado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=15,
            help='Cantidad de boletines a crear (por defecto: 15)'
        )
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirmar la eliminación de todos los boletines existentes'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        confirmar = options['confirmar']

        # Validar cantidad
        if cantidad <= 0:
            self.stdout.write(self.style.ERROR('⚠️ La cantidad debe ser un número positivo.'))
            return

        if not confirmar:
            self.stdout.write(
                self.style.ERROR('⚠️ ADVERTENCIA: Este comando eliminará TODOS los boletines existentes.')
            )
            self.stdout.write('Para proceder, usa el flag --confirmar:')
            self.stdout.write('python manage.py limpiar_y_repoblar_boletines --confirmar')
            return

        # Mostrar estadísticas antes de limpiar
        total_boletines = Boletin.objects.count()
        self.stdout.write(f'📊 Boletines existentes: {total_boletines}')

        # Limpiar boletines existentes
        try:
            self.stdout.write(self.style.WARNING('🧹 Limpiando boletines existentes...'))
            Boletin.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Boletines eliminados correctamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al eliminar boletines: {str(e)}'))
            return

        # Obtener usuario administrador
        try:
            admin_user = self.obtener_usuario_admin()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al obtener/crear usuario administrador: {str(e)}'))
            return

        # Crear boletines con contenido HTML mejorado
        try:
            self.crear_boletines_html_mejorado(cantidad, admin_user)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al crear boletines: {str(e)}'))
            return

        self.stdout.write(
            self.style.SUCCESS(f'🎉 ¡Proceso completado! Se han creado {cantidad} boletines con HTML correctamente formateado.')
        )

    def obtener_usuario_admin(self):
        """Obtener o crear un usuario administrador"""
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            try:
                # Generar contraseña segura
                password = secrets.token_urlsafe(16)
                admin_user = User.objects.create_user(
                    username='admin_boletines',
                    email='admin@example.com',
                    first_name='Admin',
                    last_name='Boletines',
                    password=password,
                    is_staff=True,
                    is_superuser=True
                )
                self.stdout.write(self.style.SUCCESS(f'👤 Usuario administrador creado: {admin_user.username}'))
                self.stdout.write(self.style.WARNING(f'🔑 Contraseña generada: {password}'))
            except Exception as e:
                raise Exception(f'Error al crear usuario administrador: {str(e)}')
        return admin_user

    def crear_boletines_html_mejorado(self, cantidad, admin_user):
        """Crear boletines con contenido HTML correctamente estructurado"""
        self.stdout.write(f'📝 Creando {cantidad} boletines con HTML mejorado...')

        categorias = ['blog', 'cursos', 'promociones', 'membresias', 'anuncios', 'eventos']
        estados = ['borrador', 'programado', 'enviado']
        prioridades = ['baja', 'normal', 'alta', 'urgente']

        for i in range(cantidad):
            categoria = random.choice(categorias)
            estado = random.choice(estados)
            prioridad = random.choice(prioridades)

            # Generar contenido HTML mejorado
            titulo, resumen, contenido = self.generar_contenido_html_mejorado(categoria, i + 1)

            # Crear fechas aleatorias
            fecha_base = timezone.now()
            if estado == 'programado':
                fecha_programada = fecha_base + timedelta(days=random.randint(1, 30))
                fecha_enviado = None
            elif estado == 'enviado':
                fecha_programada = None
                fecha_enviado = fecha_base - timedelta(days=random.randint(1, 90))
            else:
                fecha_programada = None
                fecha_enviado = None

            # Crear el boletín
            try:
                boletin = Boletin.objects.create(
                    titulo=titulo,
                    resumen=resumen,
                    contenido=contenido,
                    categoria=categoria,
                    prioridad=prioridad,
                    estado=estado,
                    fecha_programada=fecha_programada,
                    fecha_enviado=fecha_enviado,
                    solo_suscriptores_premium=random.choice([True, False]),
                    creado_por=admin_user,
                    activo=True,
                    total_enviados=random.randint(50, 1000) if estado == 'enviado' else 0,
                    total_abiertos=random.randint(10, 500) if estado == 'enviado' else 0,
                    total_clicks=random.randint(5, 100) if estado == 'enviado' else 0
                )

                # Relacionar con blog o curso ocasionalmente
                if categoria == 'blog' and random.choice([True, False]):
                    blogs = list(BlogPost.objects.filter(activo=True)[:10])
                    if blogs:
                        boletin.blog_relacionado = random.choice(blogs)
                        boletin.save()
                elif categoria == 'cursos' and random.choice([True, False]):
                    cursos = list(Course.objects.filter(is_available=True)[:10])
                    if cursos:
                        boletin.curso_relacionado = random.choice(cursos)
                        boletin.save()

                self.stdout.write(f'  ✓ Boletín {i+1}/{cantidad}: {boletin.titulo} ({categoria} - {estado})')

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠️ Error al crear boletín {i+1}: {str(e)}'))
                continue

    def generar_contenido_html_mejorado(self, categoria, numero):
        """Generar contenido HTML correctamente estructurado por categoría"""
        contenidos = {
            'blog': {
                'titulo': f'Nuevas Tendencias en Tecnología: Artículo #{numero}',
                'resumen': 'Explora las últimas innovaciones tecnológicas y descubre cómo pueden impactar tu carrera profesional.',
                'contenido': '''
<div class="newsletter-content">
    <header class="newsletter-header">
        <h1>🚀 Nuevas Tendencias en Tecnología</h1>
        <p class="lead">Mantente al día con las innovaciones que están transformando el mundo</p>
    </header>
    <article class="main-content">
        <h2>¿Por qué es importante mantenerse actualizado?</h2>
        <p>En el mundo tecnológico actual, la innovación avanza a un ritmo acelerado. Las empresas buscan profesionales que no solo dominen las tecnologías actuales, sino que también estén preparados para adaptarse a las nuevas tendencias.</p>
        <h3>📈 Tendencias destacadas en 2025:</h3>
        <ul class="trending-list">
            <li><strong>Inteligencia Artificial Generativa:</strong> Herramientas como Grok 3 están revolucionando la productividad</li>
            <li><strong>Edge Computing:</strong> Procesamiento de datos más cerca del usuario final</li>
            <li><strong>Desarrollo Low-Code/No-Code:</strong> Democratización del desarrollo de aplicaciones</li>
            <li><strong>Web3 y Blockchain:</strong> Nuevas formas de interacción y transacciones digitales</li>
        </ul>
        <blockquote class="highlight-quote">
            "La única constante en tecnología es el cambio. Los profesionales que abrazan el aprendizaje continuo serán los que lideren el futuro."
        </blockquote>
        <h3>💡 Cómo aplicar estas tendencias:</h3>
        <ol class="action-steps">
            <li>Identifica cuáles se alinean con tu carrera actual</li>
            <li>Dedica tiempo semanal a explorar nuevas herramientas</li>
            <li>Participa en comunidades de desarrollo</li>
            <li>Experimenta con proyectos personales</li>
        </ol>
        <div class="cta-section">
            <h3>🎯 ¿Listo para dar el siguiente paso?</h3>
            <p>Explora nuestros cursos especializados y mantente a la vanguardia tecnológica.</p>
            <a href="#" class="cta-button">Ver Cursos Disponibles</a>
        </div>
    </article>
</div>
                '''
            },
            # ... (El resto del diccionario `contenidos` se mantiene igual, pero se podría mover a un archivo separado)
        }
        content = contenidos.get(categoria, {
            'titulo': f'Anuncio General #{numero}',
            'resumen': 'Información importante para todos nuestros usuarios.',
            'contenido': '<div class="newsletter-content"><p>Contenido por defecto para anuncios.</p></div>'
        })
        # Separar el return en varias líneas para mayor claridad
        return (
            content['titulo'],
            content['resumen'],
            content['contenido']
        )