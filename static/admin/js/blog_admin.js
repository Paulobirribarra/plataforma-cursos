// JavaScript personalizado para el admin del blog

(function() {
    'use strict';
    
    // Esperar a que el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        
        // Auto-generar slug desde el título
        const tituloField = document.querySelector('#id_titulo');
        const slugField = document.querySelector('#id_slug');
        
        if (tituloField && slugField) {
            tituloField.addEventListener('input', function() {
                if (slugField.readOnly) return; // No actualizar si es readonly
                
                let slug = this.value
                    .toLowerCase()
                    .trim()
                    .replace(/[áàäâã]/g, 'a')
                    .replace(/[éèëê]/g, 'e')
                    .replace(/[íìïî]/g, 'i')
                    .replace(/[óòöôõ]/g, 'o')
                    .replace(/[úùüû]/g, 'u')
                    .replace(/[ñ]/g, 'n')
                    .replace(/[ç]/g, 'c')
                    .replace(/[^a-z0-9\s-]/g, '') // Remover caracteres especiales
                    .replace(/\s+/g, '-') // Espacios a guiones
                    .replace(/-+/g, '-') // Múltiples guiones a uno solo
                    .replace(/^-|-$/g, ''); // Remover guiones al inicio y final
                
                slugField.value = slug;
            });
        }
        
        // Contador de caracteres para meta_description
        const metaDescField = document.querySelector('#id_meta_description');
        if (metaDescField) {
            const maxChars = 160;
            const counter = document.createElement('div');
            counter.style.fontSize = '11px';
            counter.style.color = '#666';
            counter.style.marginTop = '5px';
            
            function updateCounter() {
                const remaining = maxChars - metaDescField.value.length;
                counter.textContent = `${metaDescField.value.length}/${maxChars} caracteres`;
                
                if (remaining < 20) {
                    counter.style.color = '#d63384';
                } else if (remaining < 40) {
                    counter.style.color = '#fd7e14';
                } else {
                    counter.style.color = '#666';
                }
            }
            
            metaDescField.parentNode.appendChild(counter);
            metaDescField.addEventListener('input', updateCounter);
            updateCounter(); // Inicializar
        }
        
        // Auto-generar resumen desde el contenido
        const contenidoField = document.querySelector('#id_contenido');
        const resumenField = document.querySelector('#id_resumen');
        
        if (contenidoField && resumenField) {
            const generateButton = document.createElement('button');
            generateButton.type = 'button';
            generateButton.textContent = '📝 Generar resumen automático';
            generateButton.className = 'button default';
            generateButton.style.marginTop = '5px';
            
            generateButton.addEventListener('click', function(e) {
                e.preventDefault();
                
                if (resumenField.value.trim() && 
                    !confirm('¿Estás seguro de que quieres sobrescribir el resumen existente?')) {
                    return;
                }
                
                // Extraer texto plano del contenido HTML
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = contenidoField.value;
                const plainText = tempDiv.textContent || tempDiv.innerText || '';
                
                // Generar resumen (primeras 250 palabras)
                const words = plainText.trim().split(/\s+/);
                const summary = words.slice(0, 40).join(' '); // Aproximadamente 250 caracteres
                
                resumenField.value = summary.length > 250 ? 
                    summary.substring(0, 250) + '...' : summary;
                
                // Actualizar meta_description si está vacío
                if (metaDescField && !metaDescField.value.trim()) {
                    metaDescField.value = summary.length > 160 ? 
                        summary.substring(0, 160) : summary;
                    
                    // Disparar evento para actualizar contador
                    metaDescField.dispatchEvent(new Event('input'));
                }
                
                // Feedback visual
                generateButton.textContent = '✅ Resumen generado';
                generateButton.style.background = '#198754';
                generateButton.style.color = 'white';
                
                setTimeout(() => {
                    generateButton.textContent = '📝 Generar resumen automático';
                    generateButton.style.background = '';
                    generateButton.style.color = '';
                }, 2000);
            });
            
            resumenField.parentNode.appendChild(generateButton);
        }
        
        // Validación de imagen en tiempo real
        const imagenField = document.querySelector('#id_imagen_destacada');
        if (imagenField) {
            imagenField.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;
                
                const maxSize = 5 * 1024 * 1024; // 5MB
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
                
                // Remover alertas previas
                const prevAlert = imagenField.parentNode.querySelector('.image-validation-alert');
                if (prevAlert) prevAlert.remove();
                
                let isValid = true;
                let message = '';
                
                if (file.size > maxSize) {
                    isValid = false;
                    message = `⚠️ Archivo demasiado grande: ${(file.size / (1024 * 1024)).toFixed(1)}MB. Máximo permitido: 5MB`;
                } else if (!allowedTypes.includes(file.type)) {
                    isValid = false;
                    message = `⚠️ Tipo de archivo no permitido: ${file.type}. Usa JPG, PNG, GIF o WebP`;
                }
                
                if (!isValid) {
                    const alert = document.createElement('div');
                    alert.className = 'image-validation-alert';
                    alert.style.cssText = `
                        background: #f8d7da;
                        color: #721c24;
                        padding: 8px 12px;
                        border: 1px solid #f5c6cb;
                        border-radius: 4px;
                        margin-top: 5px;
                        font-size: 12px;
                    `;
                    alert.textContent = message;
                    imagenField.parentNode.appendChild(alert);
                    
                    // Limpiar el campo
                    imagenField.value = '';
                } else {
                    // Mostrar preview de la imagen
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const prevPreview = imagenField.parentNode.querySelector('.image-preview');
                        if (prevPreview) prevPreview.remove();
                        
                        const preview = document.createElement('div');
                        preview.className = 'image-preview';
                        preview.innerHTML = `
                            <div style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                                <p style="margin: 0 0 5px 0; font-size: 12px; color: #666;">Vista previa:</p>
                                <img src="${e.target.result}" style="max-width: 200px; max-height: 150px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <p style="margin: 5px 0 0 0; font-size: 11px; color: #666;">
                                    📁 ${file.name} (${(file.size / 1024).toFixed(1)} KB)
                                </p>
                            </div>
                        `;
                        imagenField.parentNode.appendChild(preview);
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
        
        // Mostrar tiempo de lectura estimado
        if (contenidoField) {
            const readingTimeDisplay = document.createElement('div');
            readingTimeDisplay.style.cssText = `
                margin-top: 5px;
                padding: 5px 10px;
                background: #e7f3ff;
                border-left: 3px solid #0066cc;
                font-size: 12px;
                color: #0066cc;
            `;
            
            function updateReadingTime() {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = contenidoField.value;
                const plainText = tempDiv.textContent || tempDiv.innerText || '';
                const wordCount = plainText.trim().split(/\s+/).length;
                const readingTime = Math.max(1, Math.ceil(wordCount / 200)); // 200 palabras por minuto
                
                readingTimeDisplay.innerHTML = `
                    📖 Tiempo de lectura estimado: <strong>${readingTime} minuto${readingTime > 1 ? 's' : ''}</strong> 
                    (${wordCount} palabras)
                `;
            }
            
            contenidoField.parentNode.appendChild(readingTimeDisplay);
            contenidoField.addEventListener('input', updateReadingTime);
            updateReadingTime(); // Inicializar
        }
        
        // Confirmación antes de despublicar posts con muchas visitas
        const activoField = document.querySelector('#id_activo');
        const visitasField = document.querySelector('.field-visitas .readonly');
        
        if (activoField && visitasField) {
            activoField.addEventListener('change', function() {
                if (!this.checked) { // Si se está despublicando
                    const visitasText = visitasField.textContent || '0';
                    const visitas = parseInt(visitasText.replace(/\D/g, '')) || 0;
                    
                    if (visitas > 100) {
                        const confirmed = confirm(
                            `⚠️ Este post tiene ${visitas} visitas.\n\n` +
                            `¿Estás seguro de que quieres despublicarlo?\n` +
                            `Considera usar "Destacado: No" en lugar de despublicar.`
                        );
                        
                        if (!confirmed) {
                            this.checked = true; // Revertir el cambio
                        }
                    }
                }
            });
        }
        
        console.log('🚀 Scripts del admin del blog cargados correctamente');
    });
})();
