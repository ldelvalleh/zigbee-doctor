# Instalación y configuración inicial

Zigbee Doctor es una integración no oficial de Home Assistant pensada para diagnosticar redes Zigbee2MQTT de forma clara.

## 1. Requisitos

Necesitas:

- Home Assistant.
- MQTT configurado en Home Assistant.
- Zigbee2MQTT usando el mismo broker MQTT.
- HACS instalado.

## 2. Configuración recomendada en Zigbee2MQTT

Zigbee Doctor necesita que Zigbee2MQTT publique disponibilidad, estado del bridge, health y datos de dispositivos.

Revisa el archivo `configuration.yaml` de Zigbee2MQTT:

```yaml
availability:
  enabled: true

health:
  interval: 10
  reset_on_check: true

advanced:
  last_seen: ISO_8601
```

Notas importantes:

- En algunas versiones de Zigbee2MQTT, `availability: true` también puede ser válido.
- Lo importante es que existan topics como `zigbee2mqtt/<friendly_name>/availability`.
- `last_seen: ISO_8601` ayuda a detectar dispositivos que llevan demasiado tiempo sin reportar.
- `health.interval` define cada cuánto se publica el estado de salud.
- `reset_on_check: true` hace que las métricas de health sean más fáciles de interpretar por ventanas de tiempo.

Después de cambiar esto, reinicia Zigbee2MQTT.

## 3. Instalación con HACS

1. Abre HACS.
2. Entra en Integraciones.
3. Pulsa el menú de los tres puntos.
4. Selecciona Repositorios personalizados.
5. Añade:

```text
https://github.com/ldelvalleh/zigbee-doctor
```

6. Categoría: Integración.
7. Instala Zigbee Doctor.
8. Reinicia Home Assistant.
9. Ve a Ajustes > Dispositivos y servicios > Añadir integración.
10. Busca Zigbee Doctor.

## 4. Opciones iniciales

- Topic base de Zigbee2MQTT: normalmente `zigbee2mqtt`.
- Activar panel lateral: recomendado.
- Umbral de batería baja: por defecto 20%.
- Tiempo máximo sin respuesta en dispositivos pasivos: por defecto 25 horas.
- Tiempo máximo sin respuesta en dispositivos activos: por defecto 10 minutos.

## 5. Qué verás en Home Assistant

Zigbee Doctor crea entidades y un panel lateral.

El panel muestra:

- Estado general.
- Puntuación orientativa de salud.
- Dispositivos detectados.
- Dispositivos sin conexión.
- Problemas encontrados.
- Dispositivos con batería baja.
- Dispositivos que llevan mucho tiempo sin reportar.

## 6. Aviso honesto

Zigbee Doctor no pretende adivinar la radiofrecuencia con una bola de cristal domótica.

Puede detectar síntomas muy útiles, pero no siempre puede demostrar la causa exacta. Por ejemplo, una mala cobertura, una interferencia WiFi o un router Zigbee defectuoso pueden parecerse mucho desde los datos de Zigbee2MQTT.

La idea es ayudarte a saber dónde mirar primero, no vender magia.
