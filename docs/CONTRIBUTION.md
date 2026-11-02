# De qué Trata este Documento?

Este documento se establecerán las reglas para que puedas contribuir a este proyecto de Inteligencia Artificial de forma cómoda y ordenada.

## Antes de Empezar

Antes de empezar necesitas clonar el repositorio:

```bash
git clone https://github.com/Desarrollo-de-software-2-DAM/Agente.git
cd Agente
```

## Actualizar el Repositorio Local

Punto importante a la hora de modificar el proyecto, la rama `develop` es la rama con la que se trabajará con el fin de no afectar la rama principal.

Luego tendrás que crear una rama con la cual podrás modificar libremente. 

```bash
git checkout develop
git pull origin develop
git checkout -b feature/nombre-de-tu-tarea
```

## Subir Avances a la Rama Develop

después de realizar los cambios:

```bash
git add .
git commit -m "prefijo: descripción del cambio"
```

Cuando vayas a subir la rama por primera vez:

```bash
git push -u origin feature/nombre-de-tu-tarea
```

Las siguientes veces que vayas a hacerlo desde la misma rama:

```bash
git push
```

### Lista de prefijos con sus funcionalidad

| Prefijo | Función |
| --- | --- |
| `feat` | Nueva integración |
| `fix` | Corrección de un error |
| `test` | pruebas del proyecto |
| `docs` | Modificación de la documentación |


## Pull Request

Todas las pull request que se realicen deben de integrarse primero a la rama `develop`, nunca se debe de hacer push directo, cuando se haga una pull request debe debes de llenar los siguientes campos:

- **Qué Cambió** - Descripción corta de lo que se modificó.
- **Tarjeta de trello** - Envío del enlace de la tarea que realizaste.
- **Cómo se validó** - cómo comprobaste el cambio que hiciste.
- **Imagenes de prueba** - Imagenes referentes al cambio (Obligatorio).
- **Checklist** - Marcar el campo según corresponda la tarea que realizaste.

### Requisitos adicionales para el Pull Request

- Debe asignarse a una persona como revisora.
- Debe incluir imágenes de prueba como evidencia de que el cambio funciona.