# Learning Journal

This journal tracks what I learn while building this Odoo module on my own:
what I discovered, what blocked me, and how I solved it.

---

## Session 1 — Development environment (October 5, 2026)

**Goal:** run Odoo locally with Docker, ready for module development.

### What I learned
- **Docker Compose** runs several containers together: here, `db` (PostgreSQL)
  and `odoo` (the Odoo server).
- **`depends_on`** only sets the start order (`db` before `odoo`). It does not
  connect them: the connection comes from `db_host = db` in `odoo.conf`, because
  Compose puts both containers on the same network.
- **Volumes** keep the data when a container is removed. A container is
  disposable; persistent data lives in a volume.
  `docker compose down` keeps the volumes, `docker compose down -v` deletes them.
- **Mounting `./addons`** into the container lets Odoo see the modules I write
  on my Mac.
- **Odoo 20** is the latest version (September 2026). I switched from 19 to 20
  before writing any code, to work on the version the R&D team uses.

### What blocked me
1. `docker compose up` failed with
   `failed to connect to the docker API at unix:///.../docker.sock`.
2. Odoo was running, but the browser could not open `http://localhost:8069`
   (`curl: Connection reset by peer`).

### How I solved it
1. The Docker engine was not running: I started Docker Desktop
   (Apple Silicon version for my M2 Mac).
2. I read the logs (`docker compose logs --tail=40 odoo`) and found
   `HTTP service running on 127.0.0.1:8069`.
   Inside a container, `127.0.0.1` means the container itself, so Odoo refused
   every connection coming from my Mac. I added `http_interface = 0.0.0.0`
   to `odoo.conf` so Odoo accepts outside connections.

**Lesson:** when a service in a container is unreachable, check which address
it listens on. The logs gave the answer in one line.

---

## Session 2 — Odoo guidelines (October 8, 2026)

**Goal:** read Odoo's Coding guidelines and Git guidelines before writing code.

### Rules I will apply from now on
- One file per main model, views in `<model>_views.xml`, access rights in
  `security/ir.access.csv` (Odoo 20, see Session 5).
- Model names are singular, with dots and the module prefix
  (for example `module.equipment`, not `module.equipments`).
- Relational fields: `_id` for Many2one, `_ids` for One2many / Many2many.
- Commit messages follow `[TAG] module: short sentence`, and the description
  explains **why**, not what.
- Never write raw SQL when the ORM can do it, and never call `cr.commit()`.

### What blocked me
I added GitHub's official Python `.gitignore` template and almost pushed it
as is. Two of its rules conflict with the way Odoo modules are organized:
- `*.pot` would ignore Odoo translation templates, which live in each
  module's `i18n/` folder and must be versioned.
- `lib/` would ignore every folder named `lib`, including `static/lib/`,
  where Odoo stores JavaScript libraries.

### How I solved it
I read the template line by line before committing and removed both rules.

**Lesson:** a generic template is a starting point, not a final answer.
Read it before pushing and check it against the framework's conventions.

---

## Session 3 — Module skeleton and first model (October 8, 2026)

**Goal:** create the `bs_haccp` module, design the data model and write the
first model (`bs.haccp.location`).

### What I learned
- **Data model design:** a model is a table, a field is a column. I designed
  three models on paper before coding: locations, equipment and readings.
  A reading stores only `equipment_id`, so the equipment name is written
  once (normalization).
- **Naming rules:** Many2one fields end with `_id`, One2many/Many2many with
  `_ids`, the main field is `name`, and reserved words like `type` are avoided.
- **Odoo adds technical columns to every table:** `id` (primary key),
  `create_uid`, `create_date`, `write_uid` and `write_date`.
- **Restart vs Upgrade:** a restart reloads the Python code, an Upgrade
  updates the database (tables, columns) and the module information.
  After a manifest change: Update Apps List, then Upgrade.
- **Module category:** an unknown category creates a new one. I used the same
  category as the official Maintenance app (`Supply Chain/Maintenance`).
- **Git:** run `git status` and `git diff` before every commit, use the right
  tag (`[ADD]`, `[IMP]`, `[FIX]`), and never rewrite a pushed commit.
- **Docker:** a container keeps the absolute path of its mounted folders.
  After moving the project folder, the containers must be recreated
  (`docker compose down` then `up -d`). Renaming the folder would change the
  volume names and hide the database.

### Design choices
- **Business choices:** locations configurable by each restaurant (consistent
  data instead of free text), temperature thresholds on each equipment,
  a check state computed automatically.
- **Technical choices:** the `bs_` prefix recommended by Odoo's guidelines,
  and an `active` field to archive locations instead of deleting them,
  so the HACCP history stays complete for an inspection.

### What blocked me
- The model table was not created. Three mistakes in the import chain:
  a typo in a file name (`__intit__.py`), files edited but not saved,
  and the two `__init__.py` files with swapped imports.
- Odoo then returned an Internal Server Error.

### How I solved it
- I checked each link of the import chain with `cat`, one file at a time.
- With AI help, I read the traceback. Method for next time:
  the **last line** gives the error, the **`File` line just above** gives
  the file and the line.

### Habits for next session
- Write one file at a time, finish it and save it before moving on.
- Turn on Auto Save in VS Code.
- Verify each step (logs, `psql`) before going further.

---

## Session 4 — All three models (October 8, 2026)

**Goal:** finish the data model with equipment and temperature readings.

### What I learned
- **Code in English:** labels and selection values are written in English.
  Translations go in the `i18n/` folder.
- **Selection values** are stored as they are in the database
  (`fridge`, `freezer`), so they must stay stable and technical.
- **Default values** (`default=`) are applied by Odoo in Python when a record
  is created. Only `required=True` becomes a database rule (`not null`).
- **`ondelete='restrict'`** on `equipment_id`: the database refuses to delete
  a piece of equipment that has readings.
- **A One2many field is not stored:** `reading_ids` has no column. Odoo finds
  the readings through `equipment_id` on the other side.
- **Datetime fields** are stored in UTC and shown in the user's time zone.
- **Ruff:** a `pyproject.toml` at the project root keeps Odoo's style
  (single quotes, imports in `__init__.py` files left as they are).

---

## Session 5 — Access rights and views (October 12, 2026)

**Goal:** make the three models usable in Odoo's interface.

### What I learned
- **Access rights in Odoo 20** use `security/ir.access.csv`, with an
  `operation` column (`crud`) instead of four `perm_*` columns.
  The old `ir.model.access.csv` no longer exists.
- **Views are XML records:** a list view, a form view, a search view and a
  window action for each model, then menu items that open the actions.
- **Order matters in the manifest:** a file that uses an action must be
  loaded after the file that defines it.
- **Search views:** filters use a domain, such as
  `[('active', '=', False)]` for archived records, and `group_by` for grouping.
- **Archive instead of delete:** with `ondelete='restrict'` and an `active`
  field, Odoo refuses to delete equipment that has readings and offers to
  archive it instead.

### What blocked me
- `KeyError: 'ir.model.access'` during the upgrade.
- `FileNotFoundError` twice: typos in file names
  (`ir.model.acces.csv`, `bs_haccp_location.views.xml`).
- After changing the manifest, Odoo still looked for the old file name.

### How I solved it
- The last line of the traceback pointed to the cause each time.
- Odoo 20 replaced `ir.model.access.csv` with `ir.access.csv`. Most tutorials
  and AI answers still describe older versions, so I check the version
  of every source.
- `ls` showed the real file names.
- After changing the manifest's data list, restart Odoo before the upgrade.