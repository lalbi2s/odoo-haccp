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
<!-- Read and adjust: keep only the rules you agree with, in your own words. -->
- One file per main model, views in `<model>_views.xml`, access rights in
  `security/ir.model.access.csv`.
- Model names are singular, with dots and the module prefix
  (for example `module.equipment`, not `module.equipments`).
- Relational fields: `_id` for Many2one, `_ids` for One2many / Many2many.
- Commit messages follow `[TAG] module: short sentence`, and the description
  explains **why**, not what.
- Never write raw SQL when the ORM can do it, and never call `cr.commit()`.

### What blocked me
<!-- To complete. -->

### How I solved it
<!-- To complete. -->