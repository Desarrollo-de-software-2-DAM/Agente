# Guía de contribución

Este documento define el flujo de trabajo del equipo para colaborar en el repositorio de Amershop sin trabajar directamente sobre la rama de integración.

## 1. Clonar el repositorio

```bash
git clone https://github.com/Desarrollo-de-software-2-DAM/Agente.git
cd Agente
```

## 2. Actualizar `develop` y crear una rama de trabajo

La rama `develop` es la rama de integración del equipo. Antes de comenzar una tarea:

```bash
git switch develop
git pull origin develop
git switch -c feature/nombre-de-la-tarea
```

Utilizar nombres breves y descriptivos, por ejemplo `feature/documentacion-entrega-1` o `fix/pruebas-rag`.

## 3. Registrar los cambios

Revisar los archivos modificados:

```bash
git status
git diff
```

Agregar y confirmar los cambios relacionados con la tarea:

```bash
git add README.md docs/
git commit -m "docs: actualiza documentación de la primera entrega"
```

Prefijos acordados:

| Prefijo | Uso |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de un error |
| `test` | Agregar o modificar pruebas |
| `docs` | Documentación |
| `refactor` | Reorganización interna sin cambiar el comportamiento |

## 4. Publicar la rama

Primera publicación:

```bash
git push -u origin feature/nombre-de-la-tarea
```

Publicaciones posteriores:

```bash
git push
```

No hacer `push` directo a `develop` ni a `master`.

## 5. Crear un Pull Request

Abrir un Pull Request desde la rama de trabajo hacia `develop`. Utilizar `.github/PULL_REQUEST_TEMPLATE.md` e incluir:

- Qué cambió y por qué.
- Enlace a la tarjeta de Trello relacionada.
- Cómo se validaron los cambios (comandos y resultados).
- Capturas o evidencias cuando correspondan.
- Checklist completado.
- Una persona revisora asignada.

Antes de solicitar revisión, comprobar que la rama esté actualizada y que las pruebas relacionadas pasen.

## 6. Finalizar la tarea

Después de que el Pull Request sea revisado y fusionado:

```bash
git switch develop
git pull origin develop
git branch -d feature/nombre-de-la-tarea
```

La eliminación de la rama local es opcional si se necesita conservarla para consulta.
