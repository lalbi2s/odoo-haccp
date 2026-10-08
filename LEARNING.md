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
  `security/ir.model.access.csv`.
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