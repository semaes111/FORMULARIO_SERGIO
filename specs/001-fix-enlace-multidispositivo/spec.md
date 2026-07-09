# Spec 001 — Generación de enlace fiable en todos los dispositivos

## Problema (QUÉ falla y PORQUÉ)

El panel (`/admin.html`) genera el enlace de paciente correctamente en unos
ordenadores/móviles y falla en otros. El backend está descartado como causa:
los RPC `crear_enlace_paciente`, `listar_enlaces_recientes` y
`obtener_enlace_por_token` existen (SECURITY DEFINER), y la tabla registra
creaciones recientes desde dispositivos que sí funcionan.

Causas raíz identificadas (todas del lado cliente, todas dependientes del
dispositivo):

1. **Caché HTML sin control.** nginx sirve `index.html` y `admin.html` sin
   cabecera `Cache-Control`. Los navegadores aplican *heuristic caching*
   (RFC 9111 §4.2.2): guardan el HTML y lo reutilizan sin revalidar durante
   un tiempo proporcional a la antigüedad del `Last-Modified`. El historial
   git de este repo demuestra ciclos rotos→arreglados (RLS bloqueaba el
   INSERT del admin hasta el commit c3d956d): cualquier dispositivo que
   cacheó una versión rota sigue ejecutando el JS antiguo y falla, mientras
   un dispositivo "nuevo" descarga la versión corregida y funciona. Lo mismo
   aplica a pestañas dejadas abiertas días en los PC de la clínica.
2. **Suelo de sintaxis ES2018/ES2019.** `admin.html` usa *optional catch
   binding* (`catch {`, ES2019) y ambos HTML usan *object spread*
   (`{...opts}`, ES2018) dentro del `<script>` inline. En navegadores
   anteriores a ~2018 (PC antiguos de consulta, Android baratos, iOS < 11.3)
   el script entero falla al PARSEAR: `generateLink` nunca se define y el
   botón no hace nada; en el formulario del paciente se queda "Cargando…".
3. **Error opaco.** El `alert('Error al generar el enlace…')` descarta
   `err.message`, así que un fallo por bloqueador de contenido/DNS
   ("Failed to fetch") es indistinguible de un 401 de Supabase. Imposible
   diagnosticar por dispositivo.

## Resultado esperado

- Tras cada deploy, TODOS los dispositivos ejecutan la última versión del
  HTML en la siguiente carga (revalidación obligatoria, 304 si no cambió).
- El `<script>` inline de ambos HTML parsea con ES2017 (Safari 10.1+,
  Chrome 55+); se elimina la sintaxis ES2018+.
- Si la generación falla, el alert muestra el motivo técnico para poder
  diagnosticar el dispositivo afectado.

## Criterios de aceptación

1. `nginx -t` válido; respuestas HTML llevan `Cache-Control: no-cache`;
   los assets estáticos conservan su caché de 7 días.
2. Las cabeceras de seguridad (`X-Frame-Options`, `X-Content-Type-Options`)
   siguen presentes en las respuestas HTML (sin romper herencia de
   `add_header`).
3. Los scripts inline de `admin.html` e `index.html` parsean con
   `ecmaVersion: 2017` (verificado con acorn) — antes del fix fallaba.
4. Smoke test navegador: cargar `admin.html`, generar enlace con la API
   mockeada → aparece el enlace; sin errores de consola.
5. Cero cambios en base de datos, RPCs o claves (Contrato 3 del prompt
   quirúrgico). Cambios exclusivamente en `nginx.conf`, `admin.html`,
   `index.html`.

## Fuera de alcance

- Transpilar a ES5 (soportar navegadores < 2017).
- Dispositivos con `supabase.co` bloqueado por red/adblocker: el fix los
  hace *diagnosticables* (alert con causa), no los desbloquea.
- Sobre-ingeniería detectada en el repo: se reporta en el ponytail-audit
  adjunto, no se aplica aquí (cambio quirúrgico atómico).

## Nota operativa post-deploy

Los dispositivos que HOY tienen cacheada una versión rota no reciben las
cabeceras nuevas hasta que refresquen una vez: hacer una recarga forzada
(Ctrl+F5 / vaciar caché) única en los dispositivos afectados. A partir de
ahí el problema no puede reaparecer.
