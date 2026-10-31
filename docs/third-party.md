# Third-party software in the Pond family

What the family's release artifacts bring along that others wrote, and where
its licence notices travel. Our own licences are in each repository's
COPYING.md. Software that is only installed on the way (pip and npm packages
at build time, a Docker base image pulled on the target, d365fo.tools from the
PowerShell Gallery) is not shipped by us and carries its own terms.

A release can run without a checkout or a connection to its dependencies'
repositories. Its notices therefore travel with the software, so an operator
can see what was shipped and under which terms. The build checks refuse
missing notices; when dependencies change, their inventory must change too.

| Shipped in | Third-party inside | Its notices |
|---|---|---|
| Linux release tarballs of the Crocodile and the Pirates (`python.tar.gz`) | CPython from python-build-standalone, with OpenSSL, SQLite, libffi, zlib, bzip2, xz, mpdecimal, expat, ncurses, libedit, Tcl/Tk and others linked in | `python/licenses/` in the runtime, kept by boring-deploy per build (Pond Common, `python_notices/`); CPython's own `LICENSE.txt` |
| The same tarballs (`wheels/`) and every service image | Python packages from PyPI (MCP SDK, httpx, cryptography, pydantic, ...) | each wheel's `*.dist-info/licenses/`, installed with it |
| Canvas (wheel, service image, pondNT bundle) | Excalidraw 0.18.0 with React and its other npm dependencies, built into browser assets; eight font families | `assets/licenses/` (one file per package), `*.LEGAL.txt` next to the chunks, `assets/DEPENDENCIES.json` (which packages are bundled), `assets/fonts/*/LICENSE.txt`; notices upstream does not ship are kept in `canvas/frontend/notices/` |
| pondNT Windows bundle | CPython for Windows; PowerShell 7 with its modules | `python/LICENSE.txt` (includes the conditions of its bundled libraries); `pwsh/LICENSE.txt` and `pwsh/ThirdPartyNotices.txt` |

## Licences worth knowing about

Almost everything is under permissive licences (MIT, BSD, ISC, Apache-2.0,
PSF, OFL-1.1). The exceptions, all in Canvas's browser bundle, which is a
separate work next to our code, not linked into it:

- **elkjs** (EPL-2.0, a weak copyleft): shipped unmodified; its source is at
  github.com/kieler/elkjs and on npm.
- **DOMPurify** (MPL-2.0 or Apache-2.0): shipped unmodified.
- **Excalifont**: Excalidraw states OFL-1.1, but the font file itself only
  says "All rights reserved". Recorded in the maintained [Canvas notice inventory](https://github.com/the-boring-crocodile/boring-services/blob/main/canvas/frontend/notices/README.md).

Left out on purpose: **Liberation Sans 1.05**, which Excalidraw registers for
server-side rendering only. Its licence (GPL-2.0 with the Liberation font
exception) asks for the font's source alongside; text that names it is drawn
in the browser's default font.

## Keeping it complete

- Canvas's [`frontend/build.mjs`](https://github.com/the-boring-crocodile/boring-services/blob/main/canvas/frontend/build.mjs)
  refuses to build when a bundled package or a font family has no notice.
  Its [notice inventory](https://github.com/the-boring-crocodile/boring-services/blob/main/canvas/frontend/notices/README.md)
  records the upstream sources for notices absent from the npm packages.
- boring-deploy refuses to pack a CPython whose licence notices it does not
  keep; `scripts/python_notices.py` in Pond Common fetches them.
- `reuse lint` on each repository (without its private material) checks that
  every file of ours has a licence.
