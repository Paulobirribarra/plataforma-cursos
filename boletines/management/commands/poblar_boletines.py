from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from boletines.models import Boletin, PlantillaBoletin
from blogs.models import BlogPost
from cursos.models import Course
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Poblar datos de prueba para el sistema de boletines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=10,
            help='Cantidad de boletines de prueba a crear'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Limpiar boletines existentes antes de crear nuevos'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        limpiar = options['limpiar']

        if limpiar:
            self.stdout.write(self.style.WARNING('Limpiando boletines existentes...'))
            Boletin.objects.all().delete()
            PlantillaBoletin.objects.all().delete()

        # Obtener o crear un usuario administrador
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username='admin_boletines',
                email='admin@example.com',
                password='admin123',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS(f'Usuario administrador creado: {admin_user.username}'))

        # Crear plantillas por defecto
        self.crear_plantillas_defecto(admin_user)

        # Crear boletines de prueba
        self.crear_boletines_prueba(cantidad, admin_user)

        self.stdout.write(
            self.style.SUCCESS(f'✅ Se han creado {cantidad} boletines de prueba exitosamente')
        )

    def crear_plantillas_defecto(self, admin_user):
        """Crear plantillas por defecto para cada categoría"""
        self.stdout.write('Creando plantillas por defecto...')
        
        plantillas_data = [
            {
                'nombre': 'Plantilla Blog Estándar',
                'categoria': 'blog',
                'descripcion': 'Plantilla estándar para boletines de blog y noticias',
                'por_defecto': True
            },
            {
                'nombre': 'Plantilla Curso Promocional',
                'categoria': 'cursos',
                'descripcion': 'Plantilla promocional para cursos',
                'por_defecto': True
            },
            {
                'nombre': 'Plantilla Ofertas',
                'categoria': 'promociones',
                'descripcion': 'Plantilla para promociones y ofertas especiales',
                'por_defecto': True
            },
            {
                'nombre': 'Plantilla Membresías',
                'categoria': 'membresias',
                'descripcion': 'Plantilla para boletines de membresías',
                'por_defecto': True
            },
            {
                'nombre': 'Plantilla Anuncios',
                'categoria': 'anuncios',
                'descripcion': 'Plantilla general para anuncios',
                'por_defecto': True
            },
            {
                'nombre': 'Plantilla Eventos',
                'categoria': 'eventos',
                'descripcion': 'Plantilla para eventos y webinars',
                'por_defecto': True
            }
        ]

        for plantilla_data in plantillas_data:
            plantilla, created = PlantillaBoletin.objects.get_or_create(
                categoria=plantilla_data['categoria'],
                por_defecto=True,
                defaults={
                    'nombre': plantilla_data['nombre'],
                    'descripcion': plantilla_data['descripcion'],
                    'html_template': self.get_template_html(plantilla_data['categoria']),
                    'css_styles': self.get_template_css(),
                    'creada_por': admin_user,
                    'activa': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Plantilla creada: {plantilla.nombre}')

    def crear_boletines_prueba(self, cantidad, admin_user):
        """Crear boletines de prueba"""
        self.stdout.write(f'Creando {cantidad} boletines de prueba...')
        
        categorias = ['blog', 'cursos', 'promociones', 'membresias', 'anuncios', 'eventos']
        estados = ['borrador', 'programado', 'enviado']
        prioridades = ['baja', 'normal', 'alta', 'urgente']
        
        # Obtener algunos blogs y cursos para relacionar
        blogs = list(BlogPost.objects.filter(activo=True)[:5])
        cursos = list(Course.objects.filter(is_available=True)[:5])

        for i in range(cantidad):
            categoria = random.choice(categorias)
            estado = random.choice(estados)
            prioridad = random.choice(prioridades)
            
            # Generar contenido basado en la categoría
            titulo, resumen, contenido = self.generar_contenido(categoria, i + 1)
            
            # Crear fechas aleatorias
            fecha_base = timezone.now()
            if estado == 'programado':
                fecha_programada = fecha_base + timedelta(days=random.randint(1, 30))
            elif estado == 'enviado':
                fecha_programada = None
                fecha_enviado = fecha_base - timedelta(days=random.randint(1, 90))
            else:
                fecha_programada = None
                fecha_enviado = None

            # Crear el boletín
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
                total_enviados=random.randint(0, 1000) if estado == 'enviado' else 0,
                total_abiertos=random.randint(0, 500) if estado == 'enviado' else 0,
                total_clicks=random.randint(0, 100) if estado == 'enviado' else 0
            )

            # Relacionar con blog o curso ocasionalmente
            if categoria == 'blog' and blogs and random.choice([True, False]):
                boletin.blog_relacionado = random.choice(blogs)
                boletin.save()
            elif categoria == 'cursos' and cursos and random.choice([True, False]):
                boletin.curso_relacionado = random.choice(cursos)
                boletin.save()

            self.stdout.write(f'  ✓ Boletín {i+1}/{cantidad}: {boletin.titulo}')

    def generar_contenido(self, categoria, numero):
        """Generar contenido de prueba basado en la categoría"""
        contenidos = {
            'blog': {
                'titulo': f'Nuevo Artículo del Blog #{numero}',
                'resumen': 'Descubre las últimas tendencias y noticias en nuestro blog. Contenido exclusivo para mantenerte actualizado.',
                'contenido': '''
                <h2>¡Nuevo contenido disponible!</h2>
                <p>Estamos emocionados de compartir nuestro último artículo del blog, donde exploramos temas fascinantes y proporcionamos insights valiosos para nuestra comunidad.</p>
                
                <h3>Lo que encontrarás:</h3>
                <ul>
                    <li>Análisis profundo del tema</li>
                    <li>Ejemplos prácticos</li>
                    <li>Consejos de expertos</li>
                    <li>Recursos adicionales</li>
                </ul>
                
                <p>No te pierdas esta oportunidad de aprender algo nuevo. <strong>¡Lee el artículo completo ahora!</strong></p>
                '''
            },
            'cursos': {
                'titulo': f'Nuevo Curso Disponible: Aprendizaje #{numero}',
                'resumen': 'Amplía tus conocimientos con nuestro nuevo curso. Contenido estructurado y práctico para tu crecimiento profesional.',
                'contenido': '''
                <h2>🎓 ¡Nuevo Curso Disponible!</h2>
                <p>Hemos lanzado un nuevo curso diseñado especialmente para ayudarte a alcanzar tus objetivos de aprendizaje.</p>
                
                <h3>¿Qué incluye este curso?</h3>
                <ul>
                    <li>Módulos interactivos</li>
                    <li>Ejercicios prácticos</li>
                    <li>Certificado de finalización</li>
                    <li>Acceso de por vida</li>
                </ul>
                
                <p><strong>Precio especial de lanzamiento:</strong> ¡Solo por tiempo limitado!</p>
                '''
            },
            'promociones': {
                'titulo': f'¡Oferta Especial #{numero} - No te la pierdas!',
                'resumen': 'Aprovecha nuestras ofertas exclusivas con descuentos increíbles. Por tiempo limitado.',
                'contenido': '''
                <h2>🏷️ ¡OFERTA ESPECIAL!</h2>
                <p>Esta es una oportunidad única que no puedes dejar pasar. Ofertas exclusivas con descuentos de hasta el 70%.</p>
                
                <h3>Incluye:</h3>
                <ul>
                    <li>Descuentos en cursos premium</li>
                    <li>Acceso gratuito a webinars</li>
                    <li>Recursos descargables</li>
                    <li>Soporte prioritario</li>
                </ul>
                
                <p><strong>⏰ Oferta válida hasta agotar stock</strong></p>
                '''
            },
            'membresias': {
                'titulo': f'Actualización de Membresía #{numero}',
                'resumen': 'Información importante sobre tu membresía y los nuevos beneficios disponibles.',
                'contenido': '''
                <h2>💎 Novedades en tu Membresía</h2>
                <p>Queremos mantenerte informado sobre las últimas actualizaciones y beneficios de tu membresía.</p>
                
                <h3>Nuevos beneficios incluidos:</h3>
                <ul>
                    <li>Acceso anticipado a nuevos cursos</li>
                    <li>Descuentos exclusivos</li>
                    <li>Sesiones personalizadas</li>
                    <li>Comunidad VIP</li>
                </ul>
                
                <p>¡Aprovecha al máximo tu membresía!</p>
                '''
            },
            'anuncios': {
                'titulo': f'Anuncio Importante #{numero}',
                'resumen': 'Información importante sobre cambios y actualizaciones en nuestra plataforma.',
                'contenido': '''
                <h2>📢 Anuncio Importante</h2>
                <p>Queremos comunicarte algunas actualizaciones importantes en nuestra plataforma que mejorarán tu experiencia de aprendizaje.</p>
                
                <h3>Cambios implementados:</h3>
                <ul>
                    <li>Mejoras en la interfaz de usuario</li>
                    <li>Nuevas funcionalidades</li>
                    <li>Optimización de rendimiento</li>
                    <li>Corrección de errores</li>
                </ul>
                
                <p>Estos cambios estarán disponibles en los próximos días.</p>
                '''
            },
            'eventos': {
                'titulo': f'Próximo Evento: Webinar #{numero}',
                'resumen': 'Únete a nuestro próximo evento online. Aprende de expertos y conecta con la comunidad.',
                'contenido': '''
                <h2>🎉 ¡Próximo Evento!</h2>
                <p>Te invitamos a participar en nuestro próximo webinar donde abordaremos temas de actualidad y relevancia para tu desarrollo profesional.</p>
                
                <h3>Detalles del evento:</h3>
                <ul>
                    <li>Fecha: Por confirmar</li>
                    <li>Duración: 2 horas</li>
                    <li>Modalidad: Online</li>
                    <li>Certificado de participación</li>
                </ul>
                
                <p><strong>¡Reserva tu lugar ahora!</strong> Cupos limitados.</p>
                '''
            }
        }

        content = contenidos.get(categoria, contenidos['anuncios'])
        return content['titulo'], content['resumen'], content['contenido']

    def get_template_html(self, categoria):
        """Obtener template HTML básico por categoría"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{{ boletin.titulo }}</title>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>{{ boletin.titulo }}</h1>
                    <p>{{ boletin.resumen }}</p>
                </header>
                <main>
                    {{ boletin.contenido|safe }}
                </main>
                <footer>
                    <p>Saludos,<br>Equipo de Plataforma Cursos</p>
                </footer>
            </div>
        </body>
        </html>
        '''

    def get_template_css(self):
        """Obtener CSS básico para las plantillas"""
        return '''
        .container { max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }
        header { text-align: center; margin-bottom: 30px; }
        main { line-height: 1.6; }
        footer { margin-top: 30px; text-align: center; color: #666; }
        h1 { color: #333; }
        h2 { color: #555; }
        '''
